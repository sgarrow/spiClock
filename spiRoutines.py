import time
import spidev
import gpiozero as gp

# Pin assignments.
BL_PIN   = gp.LED( 'J8:12' ) # Grey.    on() = 1 = Lit.    off() = 0 = Not Lit.
RST_PIN  = gp.LED( 'J8:13' ) # Brown.   Active low.
DC_PIN   = gp.LED( 'J8:22' ) # Blue.    on() = 1 = Data.   off() = 0 = Cmd.

# Just text strings.
PWR_PIN  = 'J8:1'            # Purple.  3.3V.
GND_PIN  = 'J8:6'            # White.
MOSI_PIN = 'J8:19'           # Green.
CLK_PIN  = 'J8:23'           # Orange.
CS_PIN   = 'J8:24'           # Yellow.

spi = spidev.SpiDev()
spi.open(0, 0)               # Open SPI bus 0, device 0 (CE0).
spi.mode = 0b00              # SPI mode 0, CPOL = 0, CPHA = 0.
spi.max_speed_hz = 20000000  # max = 20000000 
#############################################################################

def sendCmd(cmd):
    #print('cmd = 0x{:02x}'.format(cmd))
    DC_PIN.off()
    #time.sleep(0.001)       # Ensure proper timing.
    spi.writebytes([cmd])    # Wrap the command in a list.
    time.sleep(0.001)        # Ensure proper timing.
#############################################################################

def sendDat(datLst):
    #print('dat = 0x{:02x}'.format(datLst[0]))
    DC_PIN.on()
    #time.sleep(0.001)       # Ensure proper timing.
    spi.writebytes(datLst)   # Send a list of data.
    time.sleep(0.001)        # Ensure proper timing.
#############################################################################

def hwReset():
    RST_PIN.off()
    time.sleep(.2)
    RST_PIN.on()
    time.sleep(.2)
    return ['doneyy']
#############################################################################

def swReset():

    # SW reset sequence.
    sendCmd(0x01)            # Software reset.
    time.sleep(0.2)

    sendCmd(0x11)            # Sleep out.
    time.sleep(0.2)

    sendCmd(0x36)            # Memory Data Access Control.
    sendDat([0x00])          # Set orientation (0x00 = normal orientation).

    sendCmd(0x3A)            # Interface Pixel Format.
    sendDat([0x05])          # RGB565 format (16-bit).

    sendCmd(0x29)            # Display on.

    return ['donexx']
#############################################################################

def setPixel(x, y, color):
    # Function to set a single pixel at (x, y) to specified color.
    # Set col addr (X-axis).
    sendCmd(0x2A)       # Column address set.
    sendDat([x >> 8])   # Hi byte.
    sendDat([x & 0xFF]) # Lo byte.

    # Set row addr (Y-axis).
    sendCmd(0x2B)       # Row address set.
    sendDat([y >> 8])   # Hi byte.
    sendDat([y & 0xFF]) # Lo byte.

    # Memory write command (to write the pixel data).
    sendCmd(0x2C)

    # Convert RGB888 (24-bit) to RGB565 (16-bit).
    r = (color >> 16) & 0xF8
    g = (color >> 8) & 0xFC
    b = color & 0xF8
    rgb565 = (r << 8) | (g << 3) | (b >> 3)

    # Send the RGB565 data.
    sendDat([rgb565 >> 8])   # Hi byte.
    sendDat([rgb565 & 0xFF]) # Lo byte.

    #print(' Pixel (row,col) = ({:3},{:3}) to color {:06x}'.format(y,x,color),flush = True)
#############################################################################
def setBackLight(parmLst):
    dsrdState = parmLst[0]
    if dsrdState == '0':
        BL_PIN.off()
    elif dsrdState == '1':
        BL_PIN.on()
    return ['done2']
#############################################################################

hwReset()  # HW Reset
swReset()  # SW Reset and the display initialization.

def setWhite():
    BL_PIN.on()    # Turn on backlight.
    print('backlight on, sleeping 5')
    time.sleep(1)  # Allow display to initialize and show content.

    for row in range(10,100):
        for col in range(10,100):
            #setPixel(row, col, 0xFFFFFF) # Black, not White.
            setPixel(row, col, 0xFF0000) # Blue,  not Red.
    print('pixels set sleeping 5')

    time.sleep(1)

    BL_PIN.off()   # Turn off backlight. 
    print('backlight off, sleeping 5')
    time.sleep(1)

    spi.close()
    return ['done2']
#############################################################################

if __name__ == '__main__':
    setWhite()
