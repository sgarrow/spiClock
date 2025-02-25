# This script sends various commands and data to the waveshare 320x240 LCD 
# module.  The LCD uses the st7789v controller.  The LCD is connected to the
# Raspberry Pi 4 and they communicate via an SPI interface.

# Import required modules.
import time
import pprint as pp
import spidev
import gpiozero as gp
from PIL import Image, ImageDraw, ImageFont

# GPIO pin assignments for the LCD's backlight, reset and data/command.
BL_PIN   = gp.LED( 'J8:12' ) # Grey.    on() = 1 = Lit.    off() = 0 = Not Lit.
RST_PIN  = gp.LED( 'J8:13' ) # Brown.   Active low.
DC_PIN   = gp.LED( 'J8:22' ) # Blue.    on() = 1 = Data.   off() = 0 = Cmd.

# Some unused text strings.
PWR_PIN  = 'J8:1'            # Purple.  3.3V.
GND_PIN  = 'J8:6'            # White.
MOSI_PIN = 'J8:19'           # Green.
CLK_PIN  = 'J8:23'           # Orange.
CS_PIN   = 'J8:24'           # Yellow.

# Open up the SPI channel (global to this script).
spi = spidev.SpiDev()
spi.open(0, 0)               # Open SPI bus 0, device 0 (CE0).
spi.mode = 0b00              # SPI mode 0, CPOL = 0, CPHA = 0.
spi.max_speed_hz = 20000000  # max = 20000000 
#############################################################################

def setBackLight(parmLst):

    # This function turn the backlight of the LCD on/off.

    dsrdState = parmLst[0]
    if dsrdState == '0':
        BL_PIN.off()
    elif dsrdState == '1':
        BL_PIN.on()
    return ['done2']
#############################################################################

def hwReset():

    # This function performs a hardware reset on the st7789v controller. 

    RST_PIN.off()
    time.sleep(.2)
    RST_PIN.on()
    time.sleep(.2)
    return ['hwReset done.']
#############################################################################

def swReset():

    # This function performs a software reset on the st7789v controller. 
    # It also initializes the controller to the desired configuration.

    sendCmdToSt7789(0x01)    # Software reset.
    time.sleep(0.2)

    sendCmdToSt7789(0x11)    # Sleep out.
    time.sleep(0.2)

    sendCmdToSt7789(0x36)    # Memory Data Access Control.
    sendDatToSt7789([0xC0])  # Set orientation to portrait mode

    sendCmdToSt7789(0x3A)    # Interface Pixel Format to RGB565 (16-bit). 
    sendDatToSt7789([0x05])  

    sendCmdToSt7789(0x29)    # Display on.
    return ['swReset done.']
#############################################################################

def sendCmdToSt7789(cmd):

    # This function sends the passed in command to the st7789v controller.
    # Use the spi writebytes function, which has a 4096 byte list size limit.

    DC_PIN.off()             # Set st7789v to command mode.
    spi.writebytes([cmd])    # Wrap the command in a list.
    time.sleep(0.001)        # Ensure proper timing.
    return ['sendCmdToSt7789 done.']
#############################################################################

def sendDatToSt7789(datLst):

    # This function sends the passed in data to the st7789v controller.
    # Use the spi writebytes function, which has a 4096 byte list size limit.

    chunkSize = 4096
    chunks = [ datLst[x:x+chunkSize] for x in range(0, len(datLst), chunkSize) ]

    DC_PIN.on()              # Set st7789v to data mode. 
    for c in chunks:
        spi.writebytes(c)    # Send a list of data.
        time.sleep(0.001)    # Ensure proper timing.
    return ['sendDatToSt7789 done.']
#############################################################################

def sendDat2ToSt7789(datLst):

    # This function sends the passed in data to the st7789v controller.
    # Use the spi writebytes2 function, which handles arbitraily large lists.

    DC_PIN.on()              # Set st7789v to data mode. 
    spi.writebytes2(datLst)  # Send a list of data.
    time.sleep(0.001)        # Ensure proper timing.
    return ['sendDat2ToSt7789 done.']
#############################################################################

def setOnePixel(row, col, pixelDataListOfBytes, sendFunc):

    # This function sets a single pixel at (row,col) to the RGB565 color data
    # contained in pixelDataListOfBytes.  The sendFunc parameter will be 
    # either sendDatToSt7789 or sendDat2ToSt7789.  When sendDatToSt7789 is 
    # specified no manual chunking of data will be required since 
    # len(pixelDataListOfBytes) = 2 < 4096.

    sendCmdToSt7789(0x2B)          # Set row addr command.
    sendDatToSt7789([row >> 8])    # Hi byte.
    sendDatToSt7789([row & 0xFF])  # Lo byte.

    sendCmdToSt7789(0x2A)          # Set col addr command.
    sendDatToSt7789([col >> 8])    # Hi byte.
    sendDatToSt7789([col & 0xFF])  # Lo byte.

    sendCmdToSt7789(0x2C)          # Memory write command (to write the pixel data).

    sendFunc(pixelDataListOfBytes) # Send pixel data.
    return ['setOnePixel done.']
#############################################################################

def setOneRow(row, pixelDataListOfBytes, sendFunc):

    # This function sets an entire row to the RGB565 color data
    # contained in pixelDataListOfBytes.  The sendFunc parameter will be 
    # either sendDatToSt7789 or sendDat2ToSt7789.  When sendDatToSt7789 is 
    # specified no manual chunking of data will be required since 
    # len(pixelDataListOfBytes) = 480 = 240 * 2 < 4096.

    sendCmdToSt7789(0x2B)          # Row address set.
    sendDatToSt7789([row >> 8])    # Hi byte.
    sendDatToSt7789([row & 0xFF])  # Lo byte.

    sendCmdToSt7789(0x2A)          # Set col addr command.
    sendDatToSt7789([0])           # Hi byte.
    sendDatToSt7789([0])           # Lo byte.

    sendCmdToSt7789(0x2C)          # Memory write command (to write the pixel data).
    sendFunc(pixelDataListOfBytes) # Send pixel data.
    return ['setOneRow done.']
#############################################################################

def setEntireDisplay(pixelDataListOfBytes, sendFunc):

    # This function sets the entire displat to the RGB565 color data
    # contained in pixelDataListOfBytes.  The sendFunc parameter will be 
    # either sendDatToSt7789 or sendDat2ToSt7789.  When sendDatToSt7789 is 
    # specified manual chunking of data will be required since 
    # len(pixelDataListOfBytes) = 153,600 = 240 * 320 *2 > 4096.

    sendCmdToSt7789(0x2B)          # Row address set.
    sendDatToSt7789([0])           # Hi byte.
    sendDatToSt7789([0])           # Lo byte.

    sendCmdToSt7789(0x2A)          # Set col addr command.
    sendDatToSt7789([0])           # Hi byte.
    sendDatToSt7789([0])           # Lo byte.

    sendCmdToSt7789(0x2C)          # Memory write command (to write the pixel data).
    sendFunc(pixelDataListOfBytes) # Send pixel data.
    return ['setEntireDisplay done.']
#############################################################################
    
def createPilImage(text):
    font = ImageFont.truetype('Font00.ttf' , 80)  # Set font size to 80

    # Create an RGB image with white background.
    background_color = (255, 255, 255) # White.
    #image = Image.new('RGB', (320, 240), background_color)
    image = Image.new('RGB', (240, 320), background_color)
    draw  = ImageDraw.Draw(image)

    # Define the text and it's color to be drawn.
    text_color = ( 0, 0, 0 ) # Black text color.

    # Define a bounding box.
    bbox = draw.textbbox( (0, 0), text, font = font )
    text_width  = bbox[2] - bbox[0]  # Calculate width  from bbox.
    text_height = bbox[3] - bbox[1]  # Calculate height from bbox.
    
    # Calculate position to center the text on the screen.
    x_pos = ( 320 - text_width  ) // 2
    y_pos = ( 240 - text_height ) // 2
    
    # Draw the text on the image.
    draw.text((x_pos, y_pos), text, font = font, fill = text_color, align= 'center' )
    return ['createPilImagedone.', image]
#############################################################################

if __name__ == '__main__':

    hwReset()    # HW Reset
    swReset()    # SW Reset and the display initialization.
    BL_PIN.on()  # Turn on backlight.

    # Create 3 lists each that holds 1 pixel (2-bytes) worth of data.
    # Each list holds a different RGB color value: Red, Green, Blue.
    colors = [ 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF ]
    for ii,c in enumerate(colors):
        rgb565  = ((c>>19) & 0x1F) << 11 | ((c>>10)&0x3F) << 5 | ((c>>3)&0x1F)
        if ii == 0: rPixLst = [ rgb565 >> 8, rgb565 & 0xFF ]
        if ii == 1: gPixLst = [ rgb565 >> 8, rgb565 & 0xFF ]
        if ii == 2: bPixLst = [ rgb565 >> 8, rgb565 & 0xFF ]
        if ii == 3: wPixLst = [ rgb565 >> 8, rgb565 & 0xFF ]

    rRowLst = rPixLst * 240 # Create a Rows worth of values.
    gRowLst = gPixLst * 240
    bRowLst = bPixLst * 240
    wRowLst = wPixLst * 240
    

    rAllLst = rRowLst * 320 # Create a whole Displays worth of values. 
    gAllLst = gRowLst * 320 # These contain flat scenes.
    bAllLst = bRowLst * 320
    wAllLst = wRowLst * 320

    # Create a display that has r,g,b,w bars - wach bar 10 rows thick
    barAllLst = []
    for numRepeats in range(8):
        for coloredBar in [rRowLst,gRowLst,bRowLst,wRowLst]:
            for barWidth in range(10):
                barAllLst.extend(coloredBar)
    setEntireDisplay(barAllLst, sendDat2ToSt7789)
    time.sleep(1)
    ########################################################

    # Create two images using PIL
    for text in ['0','1','2','3','4','5','6','7','8','9']:
        rspStr, myImage2 = createPilImage(text)
        width, height = myImage2.size
        pixels2 = list(myImage2.getdata()) 
    
        #pixData  = open('pixData.txt', 'w')
        #rgbData  = open('rgbData.txt', 'w')
        #pixData1 = open('pixData1.txt', 'w')
        #rgbData1 = open('rgbData1.txt', 'w')
    
        rgb565Lst = []
        for row in range(320):
            for col in range(240):
                pixel = pixels2[row*240+col]
                r, g, b = pixel
                rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
                rgb565Lst.append((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
                #pixData.write('{:3} {:3} {}\n'.format(row, col, pixel   ))
                #rgbData.write('{:3} {:3} {:04x}\n'.format(row, col, rgb565  ))
    
                #if pixel  == (255, 255, 255):  pixData1.write('0')
                #else:                          pixData1.write('1')
                #
                #if rgb565 == 0xffff:           rgbData1.write('0')
                #else:                          rgbData1.write('1')
    
            #pixData1.write('\n')
            #rgbData1.write('\n')
    
        #pixData.close
        #rgbData.close
        #pixData1.close
        #rgbData1.close
    
        data2 = [byte for el in rgb565Lst for byte in (el >> 8, el & 0xFF)]
        setEntireDisplay(data2, sendDatToSt7789)
        time.sleep(1)

    exit()

    rgb565 = []
    for pixel in pixels2:
        r, g, b = pixel
        rgb565.append((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
    data2 = [byte for el in rgb565 for byte in (el >> 8, el & 0xFF)]
    ########################################################
    
    sendFuncs = [ sendDatToSt7789, sendDat2ToSt7789 ]

    # Test 1 - Fill LCD with solid color via setOnePixel using both types of sendFuncs.
    #          Use a different color for each screen fill to be able to 
    #          tell if both fill methods work.
    print('Begin test 1')
    pixLst    = [ rPixLst, gPixLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        for row in range(320):
            for col in range(240):
                setOnePixel(row, col, pl, sf)
        print('Test 1 half done')
    ##################################################
    
    # Test 2 - Fill LCD with solid color via setOneRow using both types of sendFuncs.
    #          Use a different color for each screen fill to be able to 
    #          tell if both fill methods work.
    print('Begin test 2')
    pixLst    = [ rRowLst, gRowLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        for row in range(320):
            setOneRow(row, pl, sf)
        print('Test 2 half done')
    ###################################################

    # Test 3 - Fill LCD with solid color via setEntireDisplay using both types of sendFuncs.
    #          Use a different color for each screen fill to be able to 
    #          tell if both fill methods work.
    print('Begin test 3')
    pixLst    = [ rAllLst, gAllLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        setEntireDisplay(pl, sf)
        print('Test 3 half done')
    ####################################################

    # Test 4 - Fill LCD with image 1 via setOnePixel using simplest sendFunc.
    print('Begin test 4')
    for row in range(320):
        for col in range(240):
            r, g, b = pixels1[row*240+col]
            rgb565  = (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)
            byLst   = [rgb565 >> 8, rgb565 & 0xFF]
            setOnePixel(row, col, byLst, sendDatToSt7789)
        print('row {:3} done'.format(row))

    # Clear screen before sending image 2.
    setEntireDisplay(rAllLst, sendDatToSt7789)

    # Test 5 - Fill LCD with image 2 via setOnePixel using simplest sendFunc.
    print('Begin test 5')
    kStart = time.time()
    for row in range(320):
        for col in range(240):
            r, g, b = pixels2[row*240+col]
            rgb565  = (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)
            byLst   = [rgb565 >> 8, rgb565 & 0xFF]
            setOnePixel(row, col, byLst, sendDatToSt7789)
        print('row {:3} done'.format(row))

    BL_PIN.off()   # Turn off backlight. 

