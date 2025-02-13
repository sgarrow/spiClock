import time
import pprint   as pp
import spidev         # For SPI communication.
import gpiozero as gp # For controlling GPIO pins.
from datetime import datetime
#############################################################################

def cmds():

    commands = [
    # (ID, NAME,        W, R, "DESC")
    (0x01, 'SWRESET',   0, 0, 'Software Reset'),
    (0x04, 'RDDID',     0, 4, 'Read Display ID'),
    (0x05, 'RDDST',     0, 5, 'Read Display Status'),
    (0x0A, 'RDDPM',     0, 2, 'Read Display Power Mode'),
    (0x0B, 'RDDMADCTL', 0, 2, 'Read Display MADCTL'),
    (0x0C, 'RDDCOLMOD', 0, 2, 'Read Display Pixel Format'),
    (0x0D, 'RDDIM',     0, 2, 'Read Display Image Mode'),
    (0x0E, 'RDDSM',     0, 2, 'Read Display Signal Mode'),
    (0x0F, 'RDDSDR',    0, 2, 'Read Display Self-Diag Result'),
    (0x10, 'SLPIN',     0, 0, 'Sleep in'),                  # Default.
    (0x11, 'SLPOUT',    0, 0, 'Sleep out'),
    (0x12, 'PTLON',     0, 0, 'Partial Display Mode On'), # See 30h.
    (0x13, 'NORON',     0, 0, 'Normal Display Mode On'),  # Default.
    (0x20, 'INVOFF',    0, 0, 'Display Inversion Off'),   # Default.
    (0x21, 'INVON',     0, 0, 'Display Inversion On'),
    (0x26, 'GAMSET',    1, 0, 'Gamma Set'),
    (0x28, 'DISPOFF',   0, 0, 'Display Off'),             # Default.
    (0x29, 'DISPON',    0, 0, 'Display On'),
    (0x2A, 'CASET',     4, 0, 'Column Address Set'), # uint16 * 2.
    (0x2B, 'RASET',     4, 0, 'Row Address Set'),    # uint16 * 2.
    (0x2C, 'RAMWR',    -1, 0, 'Memory Write'),       # Not cleared on SW/HW reset, resets col/row.
    (0x2E, 'RAWRD',     0,-1, 'Memory Read'),        # Resets col/row registers, fixed 18-bit.
    (0x30, 'PTLAR',     4, 0, 'Partial Area'),       # uint16 * 2.
    (0x33, 'VSCRDEF',   6, 0, 'Vertical Scrolling Def'),  # uint16 * 3.
    (0x34, 'TEOFF',     0, 0, 'Tearing Effect Line OFF'), # Default.
    (0x35, 'TEON',      1, 0, 'Tearing Effect Line On'),
    (0x36, 'MADCTL',    1, 0, 'Memory Data Access Control'),
    (0x37, 'VSCSAD',    2, 0, 'Vertical Scroll Start Addr of RAM'),
    (0x38, 'IDMOFF',    0, 0, 'Idle Mode OFF'),           # Default.
    (0x39, 'IDMON',     0, 0, 'Idle Mode ON'),            # Reduced to 8 colors (RGB-111).
    (0x3A, 'COLMOD',    1, 0, 'Interface Pixel Format'),  # Default 66h (RGB-666).
    (0x3C, 'WRMEMC',   -1, 0, 'Write Memory Continue'),   # After 2Ch.
    (0x3E, 'RDMEMC',    0,-1, 'Read Memory Continue'),    # After 2Eh.
    (0x44, 'STE',       2, 0, 'Set Tear Scanline'),
    (0x45, 'GSCAN',     0, 3, 'Get Scanline'),
    (0x51, 'WRDISBV',   1, 0, 'Write Display Brightness'),
    (0x52, 'RDDISBV',   0, 2, 'Read Display Brightness Value'),
    (0x53, 'WRCTRLD',   1, 0, 'Write CTRL Display'),
    (0x54, 'RDCTRLD',   0, 2, 'Read CTRL Value Display'),
    (0x55, 'WRCACE',    1, 0, 'Write Content Adaptive Bright Ctrl & Color Enhance'),
    (0x56, 'RDCABC',    0, 2, 'Read Content Adaptive Brightness Control'),
    (0x5E, 'WRCACBCMB', 1, 0, 'Write CABC Minimum Brightness'),
    (0x5F, 'RDCABCMB',  0, 2, 'Read CABC Minimum Brightness'),
    (0x68, 'RDABCSDR',  0, 2, 'Read Automatic Bright Ctrl Self-Diag Result'),
    (0xDA, 'RDID1',     0, 2, 'Read ID1'),
    (0xDB, 'RDID2',     0, 2, 'Read ID2'),
    (0xDC, 'RDID3',     0, 2, 'Read ID3'),
    ]

    byName = {
        name: {'id': id, 'wrx': wrx, 'rdx': rdx, 'desc': desc}
        for id, name, wrx, rdx, desc in commands \
        if 'Read' not in desc and 'Get' not in desc }

    #byId = { id: {'name': name, 'wrx': wrx, 'rdx': rdx, 'desc': desc}
    #          for id, name, wrx, rdx, desc in commands \
    #          if 'Read' not in desc and 'Get' not in desc }

    rspStr  = '{:>10} {:>4} {:>4} {:>4}  {}'.\
        format('name', 'id', 'wrx', 'rdx', 'description \n')
    rspStr += '{:>10} {:>4} {:>4} {:>4}  {}'.\
        format('----', '--', '---', '---', '----------- \n')
    for k,v in byName.items():
        rspStr += '{:>10} {:>4} {:>4} {:>4}  {} \n'.\
            format(k,v['id'],v['wrx'],v['rdx'],v['desc'])
    #print(rspStr)
    return [rspStr]
#############################################################################

# write a python script to write a single pixel to the waveshare
# 320 x 240 spi display that uses the st7789v controller using
# gpiozero on a raspberry pi 4 using spidev writebytes function
# 
# 
# write a python script to write an entire row to the waveshare 
# 320 x 240 spi display that uses the st7789v controller using 
# gpiozero on a raspberry pi 4 using spidev writebytes function 
#############################################################################

def sendCmd(command):
    # writebytes() is used to send both cmd and data, making comm more
    # efficient than manually toggling the GPIO pins. If higher-performance
    # needed, consider using more luma.lcd or Pillow for handling graphics.
    spi.writebytes([0x00, command]) # 0x00 = Command mode.
    time.sleep(0.001)               # To ensure proper timing.
#############################################################################

def sendDat(data):
    spi.writebytes([0x01, data])    # 0x01 = Data mode.
    time.sleep(0.001)               # To ensure proper timing.
#############################################################################

def initDisplay():
    # Reset sequence. Can be done via GPIO if needed,
    # otherwise assume manual reset).
    sendCmd(0x01) # Software reset.
    time.sleep(0.1)

    sendCmd(0x11) # Sleep out.
    time.sleep(0.1)

    sendCmd(0x36) # Memory Data Access Control.
    sendDat(0x00)    # Set orientation (0x00 = normal orientation).

    sendCmd(0x3A) # Interface Pixel Format.
    sendDat(0x05)    # RGB565 format (16-bit).

    sendCmd(0x29) # Display on.

    print(' Display initialized.')
#############################################################################

def setPixel(x, y, color):
    # Function to set a single pixel at (x, y) to specified color.
    # Set col addr (X-axis).
    sendCmd(0x2A)  # Column address set.
    sendDat(x >> 8)   # Hi byte.
    sendDat(x & 0xFF) # Lo byte.

    # Set row addr (Y-axis).
    sendCmd(0x2B)  # Row address set.
    sendDat(y >> 8)   # Hi byte.
    sendDat(y & 0xFF) # Lo byte.

    # Memory write command (to write the pixel data).
    sendCmd(0x2C)

    # Convert RGB888 (24-bit) to RGB565 (16-bit).
    r = (color >> 16) & 0xF8
    g = (color >> 8) & 0xFC
    b = color & 0xF8
    rgb565 = (r << 8) | (g << 3) | (b >> 3)

    # Send the RGB565 data.
    sendDat(rgb565 >> 8)   # Hi byte.
    sendDat(rgb565 & 0xFF) # Lo byte.

    if y == 10:
        print(' Pixel (row,col) = ({:3},{:3}) to color {:06x}'.format(y,x,color),flush = True)
#############################################################################

spi = spidev.SpiDev()
def sr():

    # CS:   GPIO  8 (CE0)
    # SCLK: GPIO 11 (SCK)
    # MOSI: GPIO 10 (MOSI)

    spi.open(0, 0)                # Open SPI bus 0, device 0 (CE0).
    spi.max_speed_hz = 20000000    # max = 20000000
    spi.mode         = 0b00       # SPI mode 0, CPOL = 0, CPHA = 0.
    backlight        = gp.LED(18) # Assume backlight is GPIO 18.

    backlight.on()                # Turn on the backlight (optional).
    initDisplay()                # Initialize the display.

    for row in range(10,25+10):
        for col in range(10,25+10):
            setPixel(row,col, 0xFF0000)  # Red color (RGB format).

    # Optionally, turn off the backlight.
    # backlight.off().

    return ['done2']
#############################################################################

# On the second Sunday in March, clocks are set ahead one hour at 2:00 a.m.
# local standard time (which becomes 3:00 a.m. local Daylight Saving Time).
# On the first Sunday in November, clocks are set back one hour at 2:00 a.m.
# local Daylight Saving Time (which becomes 1:00 a.m. local standard time).


def clkCntr(prmLst):
    hours   = prmLst[0]
    minutes = prmLst[1]
    seconds = prmLst[2]

    while True:
        now = datetime.now()
        print(now)
        #year = now.year
        #month = now.month
        #day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        #microsecond = now.microsecond
    
        if hours == hour and minute == minutes and second == seconds:
            break
        time.sleep(.01)

    numSecAdded = 0
    while True:
        now = datetime.now()
        currTime = now.strftime("%H:%M:%S")
        print('{:02}:{:02}:{:02} ==? {}'.format(hours,minutes,seconds,currTime))
        time.sleep(1)
        seconds += 1

        numSecAdded += 1

        if numSecAdded >= (3600 + 60) and seconds < 60: # Add extra sec 3660 secs.
            seconds += 1
            numSecAdded = 0
            print('+ 1 s')

        if seconds  == 60:
            seconds  = 0
            minutes += 1
        if minutes  == 60:
            minutes  = 0
            hours   += 1
        if hours == 24:
            hours = 0
#############################################################################

