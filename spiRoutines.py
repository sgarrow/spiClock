# This script sends various commands and data to the waveshare 320x240 LCD
# module.  The LCD uses the st7789v controller.  The LCD is connected to the
# Raspberry Pi 4 and they communicate via an SPI interface.

# Import required modules.
import time
import spidev                     # pylint: disable=E0401
import gpiozero as gp

#               default           default
# LED(pin=None, active_high=True, initial_value=False)
# So with default constructor all the chip selects would be low and 
# hence all the LCD would be selected simultaneously, not good.
# So, init all the CS pins to high using initial_value=True.

# GPIO pin assignments for the LCD's backlight, reset and data/command.
BL_PIN   = gp.LED( 'J8:12' )      # Grey.  on() = 1 = Lit.  off()=0=Not Lit.
RST_PIN  = gp.LED( 'J8:13' )      # Brown. Active low.
DC_PIN   = gp.LED( 'J8:22' )      # Blue.  on() = 1 = Data. off()=0=Cmd.

CS_PIN_HR_MSD = gp.LED( 'J8:29', initial_value = True ) # Yellow. GPIO-05.
CS_PIN_HR_LSD = gp.LED( 'J8:31', initial_value = True ) # Yellow. GPIO-06.
CS_PIN_MN_MSD = gp.LED( 'J8:11', initial_value = True ) # Yellow. GPIO-17.
CS_PIN_MN_LSD = gp.LED( 'J8:15', initial_value = True ) # Yellow. GPIO-22.
CS_PIN_SC_MSD = gp.LED( 'J8:16', initial_value = True ) # Yellow. GPIO-23.
CS_PIN_SC_LSD = gp.LED( 'J8:37', initial_value = True ) # Yellow. GPIO-26.

csDict = { 'CS_PIN_HR_MSD' : CS_PIN_HR_MSD, 'CS_PIN_HR_LSD' : CS_PIN_HR_LSD,
           'CS_PIN_MN_MSD' : CS_PIN_MN_MSD, 'CS_PIN_MN_LSD' : CS_PIN_MN_LSD,
           'CS_PIN_SC_MSD' : CS_PIN_SC_MSD, 'CS_PIN_SC_LSD' : CS_PIN_SC_LSD }

lcdToCsXlateDict = { 'hrMSD' : 'CS_PIN_HR_MSD', 'hrLSD' : 'CS_PIN_HR_LSD',
                     'mnMSD' : 'CS_PIN_MN_MSD', 'mnLSD' : 'CS_PIN_MN_LSD',
                     'scMSD' : 'CS_PIN_SC_MSD', 'scLSD' : 'CS_PIN_SC_LSD'}

# Some unused text strings.
PWR_PIN  = 'J8:1'                 # Purple.  3.3V.
GND_PIN  = 'J8:6'                 # White.
MOSI_PIN = 'J8:19'                # Green.
CLK_PIN  = 'J8:23'                # Orange.
CS_PIN   = 'J8:24'                # Yellow. Not used - supports only 1 device.

# Open up the SPI channel (global to this script).
spi = spidev.SpiDev()
spi.open(0, 0)                    # Open SPI bus 0, device 0 (CE0).
#print('open')
spi.mode = 0b00                   # SPI mode 0, CPOL = 0, CPHA = 0.
spi.max_speed_hz = 20000000       # max = 20000000
#############################################################################

def getDisplayIdDict():           # For external users of these functions.
    return lcdToCsXlateDict
#############################################################################

def setBackLight(parmLst):
    # Turn the backlight of the LCD on/off.
    dsrdState = int(parmLst[0])
    if dsrdState == 0:
        BL_PIN.off()
    elif dsrdState == 1:
        BL_PIN.on()
    return ['Backlight Set']
#############################################################################

def hwReset():
    # Performs a hardware reset on the st7789v controller.
    RST_PIN.off()
    time.sleep(.2)
    RST_PIN.on()
    time.sleep(.2)
    return ['hwReset done.']
#############################################################################

def swReset(displayID):
    # Performs a software reset on the st7789v controller.
    # It also initializes the controller to the desired configuration.
    print(' swReset {}'.format(displayID))
    sendCmdToSt7789( displayID, 0x01 )  # Software reset.
    time.sleep(0.2)

    sendCmdToSt7789(displayID,  0x11 )  # Sleep out.
    time.sleep(0.2)

    sendCmdToSt7789(displayID,  0x36 )  # Memory Data Access Control.
    sendDatToSt7789(displayID, [0xC0])  # Set orientation to portrait mode

    sendCmdToSt7789(displayID,  0x3A )  # Pixel Format to RGB565 (16-bit).
    sendDatToSt7789(displayID, [0x05])

    sendCmdToSt7789(displayID,  0x21 )  # Display Inversion Off

    sendCmdToSt7789(displayID,  0x29 )  # Display on.
    return ['swReset done.']
#############################################################################

def sendCmdToSt7789(displayID, cmd):
    # Sends the passed in command to the st7789v controller.
    # Use the spi writebytes function, which has a 4096 byte list size limit.
    cs = lcdToCsXlateDict[displayID]      # Get cs pin.
    csDict[cs].off()                      # CS active lo.
    DC_PIN.off()                          # Set st7789v to command mode.
    spi.writebytes([cmd])                 # Wrap the command in a list.
    time.sleep(0.001)                     # Ensure proper timing.
    csDict[cs].on()
    return ['sendCmdToSt7789 done.']
#############################################################################

def sendDatToSt7789(displayID, datLst):
    # Sends the passed in data to the st7789v controller.
    # Use the spi writebytes function, which has a 4096 byte list size limit.
    chunkSize = 4096
    chunks = [ datLst[x:x+chunkSize] for x in range(0, len(datLst), chunkSize) ]

    cs = lcdToCsXlateDict[displayID]      # Get cs pin.
    csDict[cs].off()                      # CS active lo.
    DC_PIN.on()                           # Set st7789v to data mode.
    for c in chunks:
        spi.writebytes(c)                 # Send a list of data.
        time.sleep(0.001)                 # Ensure proper timing.
    csDict[cs].on()
    return ['sendDatToSt7789 done.']
#############################################################################

def sendDat2ToSt7789(displayID, datLst):
    # Sends the passed in data to the st7789v controller.
    # Use the spi writebytes2 function, which handles arbitraily large lists.
    cs = lcdToCsXlateDict[displayID]      # Get cs pin.
    csDict[cs].off()                      # CS active lo.
    DC_PIN.on()                           # Set st7789v to data mode.
    spi.writebytes2(datLst)               # Send a list of data.
    time.sleep(0.001)                     # Ensure proper timing.
    csDict[cs].on()
    return ['sendDat2ToSt7789 done.']
#############################################################################

def setOnePixel(displayID, row, col, pixelDataListOfBytes, sendFunc):
    # Sets a single pixel at (row,col) to the RGB565 color data
    # contained in pixelDataListOfBytes.  The sendFunc parameter will be
    # either sendDatToSt7789 or sendDat2ToSt7789.  When sendDatToSt7789 is
    # specified no manual chunking of data will be required since
    # len(pixelDataListOfBytes) = 2 < 4096.
    sendCmdToSt7789(displayID, 0x2B)          # Set row addr command.
    sendDatToSt7789(displayID, [row >> 8])    # Hi byte.
    sendDatToSt7789(displayID, [row & 0xFF])  # Lo byte.

    sendCmdToSt7789(displayID, 0x2A)          # Set col addr command.
    sendDatToSt7789(displayID, [col >> 8])    # Hi byte.
    sendDatToSt7789(displayID, [col & 0xFF])  # Lo byte.

    sendCmdToSt7789(displayID, 0x2C)          # Mem write cmd (write pix data).

    sendFunc(displayID, pixelDataListOfBytes) # Send pixel data.
    return ['setOnePixel done.']
#############################################################################

def setOneRow(displayID, row, pixelDataListOfBytes, sendFunc):
    # Sets an entire row to the RGB565 color data
    # contained in pixelDataListOfBytes.  The sendFunc parameter will be
    # either sendDatToSt7789 or sendDat2ToSt7789.  When sendDatToSt7789 is
    # specified no manual chunking of data will be required since
    # len(pixelDataListOfBytes) = 480 = 240 * 2 < 4096.
    sendCmdToSt7789(displayID, 0x2B)          # Row address set.
    sendDatToSt7789(displayID, [row >> 8])    # Hi byte.
    sendDatToSt7789(displayID, [row & 0xFF])  # Lo byte.

    sendCmdToSt7789(displayID, 0x2A)          # Set col addr command.
    sendDatToSt7789(displayID, [0])           # Hi byte.
    sendDatToSt7789(displayID, [0])           # Lo byte.

    sendCmdToSt7789(displayID, 0x2C)          # Mem write cmd (write pix data).
    sendFunc(displayID, pixelDataListOfBytes) # Send pixel data.
    return ['setOneRow done.']
#############################################################################

def setEntireDisplay(displayID, pixelDataListOfBytes, sendFunc):
    # Sets the entire displat to the RGB565 color data
    # contained in pixelDataListOfBytes.  The sendFunc parameter will be
    # either sendDatToSt7789 or sendDat2ToSt7789.  When sendDatToSt7789 is
    # specified manual chunking of data will be required since
    # len(pixelDataListOfBytes) = 153,600 = 240 * 320 *2 > 4096.
    sendCmdToSt7789(displayID, 0x2B)          # Row address set.
    sendDatToSt7789(displayID, [0])           # Hi byte.
    sendDatToSt7789(displayID, [0])           # Lo byte.

    sendCmdToSt7789(displayID, 0x2A)          # Set col addr command.
    sendDatToSt7789(displayID, [0])           # Hi byte.
    sendDatToSt7789(displayID, [0])           # Lo byte.

    sendCmdToSt7789(displayID, 0x2C)          # Mem write (write pix data).
    sendFunc(displayID, pixelDataListOfBytes) # Send pixel data.
    return ['setEntireDisplay done.']
#############################################################################
