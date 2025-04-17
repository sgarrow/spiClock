# This script sends various cmds and data a waveshare 320x240 LCD display.
# The LCD uses the st7789v controller.  The LCD is connected to a Raspberry
# Pi 4B and they communicate via an SPI interface.
#############################################################################

# Import required modules.
import time
import spidev # pylint: disable=E0401
import gpiozero as gp
#############################################################################
#############################################################################

# Assign GPIO Pins for Chip Selects, SPI, Pwr, etc to the 6 LCD displays.

#               default           default
# LED(pin=None, active_high=True, initial_value=False)
# So with default constructor all the chip selects would be low and hence all
# the LCD would be selected simultaneously, not good. So, init all the CS
# pins to high using initial_value=True.

# GPIO pin assignments for the LCD's backlight, reset and data/command.
BL_PIN   = gp.LED( 'J8:12' ) # Grey.  on() = 1 = Lit.  off()=0=Not Lit.
RST_PIN  = gp.LED( 'J8:13' ) # Brown. Active low.
DC_PIN   = gp.LED( 'J8:22' ) # Blue.  on() = 1 = Data. off()=0=Cmd.

# GPIO pin assignments for the 6 LCD's chip selects.
CS_PIN_HR_MSD = gp.LED( 'J8:29', initial_value = True ) # Yellow. GPIO-05.
CS_PIN_HR_LSD = gp.LED( 'J8:31', initial_value = True ) # Yellow. GPIO-06.
CS_PIN_MN_MSD = gp.LED( 'J8:11', initial_value = True ) # Yellow. GPIO-17.
CS_PIN_MN_LSD = gp.LED( 'J8:15', initial_value = True ) # Yellow. GPIO-22.
CS_PIN_SC_MSD = gp.LED( 'J8:16', initial_value = True ) # Yellow. GPIO-23.
CS_PIN_SC_LSD = gp.LED( 'J8:37', initial_value = True ) # Yellow. GPIO-26.

# Unused text strings just to document the wire colors for various signals
PWR_PIN  = 'J8:1'            # Purple.  3.3V.
GND_PIN  = 'J8:6'            # White.
MOSI_PIN = 'J8:19'           # Green.
CLK_PIN  = 'J8:23'           # Orange.
CS_PIN   = 'J8:24'           # Yellow. Not used - supports only 1 device.
#############################################################################

# Create a dictionary that translates a displayID to a chip select pin.
# External callers of the functions herein pass in a displayID.
csDict = { 'hrMSD' : CS_PIN_HR_MSD, 'hrLSD' : CS_PIN_HR_LSD,
           'mnMSD' : CS_PIN_MN_MSD, 'mnLSD' : CS_PIN_MN_LSD,
           'scMSD' : CS_PIN_SC_MSD, 'scLSD' : CS_PIN_SC_LSD }
#############################################################################

# Open up the SPI channel (global to this script).
# This code gets executed the first time someone imports this module.
spi = spidev.SpiDev()
spi.open(0, 0)                    # Open SPI bus 0, device 0 (CE0).
spi.mode = 0b00                   # SPI mode 0, CPOL = 0, CPHA = 0.
spi.max_speed_hz = 20000000       # max = 20000000
#############################################################################
#############################################################################

def setBkLight(parmLst):
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
    RST_PIN.off()  # Active Lo Reset.
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
    csDict[displayID].off()               # CS active lo.
    DC_PIN.off()                          # Set st7789v to command mode.
    spi.writebytes([cmd])                 # Wrap the command in a list.
    time.sleep(0.001)                     # Ensure proper timing.
    csDict[displayID].on()
    return ['sendCmdToSt7789 done.']
#############################################################################

def sendDatToSt7789(displayID, datLst):
    # Sends passed in data, w/ possible chuncking, to the st7789v controller.
    # Use the spi writebytes function, which has a 4096 byte list size limit.
    chunkSize = 4096
    chunks = [ datLst[x:x+chunkSize] for x in range(0, len(datLst), chunkSize) ]

    csDict[displayID].off()           # CS active lo.
    DC_PIN.on()                       # Set st7789v to data mode.
    for c in chunks:
        spi.writebytes(c)             # Send a list of data.
        time.sleep(0.001)             # Ensure proper timing.
    csDict[displayID].on()
    return ['sendDatToSt7789 done.']
#############################################################################

def sendDat2ToSt7789(displayID, datLst):
    # Sends the passed in data to the st7789v controller.
    # Use the spi writebytes2 function, which handles arbitraily large lists.
    csDict[displayID].off()           # CS active lo.
    DC_PIN.on()                       # Set st7789v to data mode.
    spi.writebytes2(datLst)           # Send a list of data.
    time.sleep(0.001)                 # Ensure proper timing.
    csDict[displayID].on()
    return ['sendDat2ToSt7789 done.']
#############################################################################

def setOnePixel(displayID, row, col, pixelDataListOfBytes, sendFunc):
    # Sets the specified pixel of the specified display at to the data contained
    # in pixelDataListOfBytes.  sendFunc will be either sendDatToSt7789 or
    # sendDat2ToSt7789.  When sendDatToSt7789 is specified no chunking will
    # be required since  len(pixelDataListOfBytes) = 2 < 4096.
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
    # Sets the specified row of the specified display to the data contained
    # in pixelDataListOfBytes. sendFunc will be either sendDatToSt7789 or
    # sendDat2ToSt7789.  When sendDat2ToSt7789 is specified no chunking will
    # be required since len(pixelDataListOfBytes) = 480 = 240 * 2 < 4096.
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
    # Sets the entire specified display to the data contained
    # in pixelDataListOfBytes. sendFunc will be either sendDatToSt7789 or
    # sendDat2ToSt7789.  When sendDat2ToSt7789 is specified no chunking will
    # be required since len(pixelDataListOfBytes) = 480 = 240 * 2 < 4096.
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
