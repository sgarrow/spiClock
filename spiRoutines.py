import time
import spidev
import gpiozero as gp
from PIL import Image, ImageDraw, ImageFont
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
    spi.writebytes2(datLst)   # Send a list of data.
    time.sleep(0.001)        # Ensure proper timing.
    print('XXXXXXXXXXXXX')
#############################################################################

def hwReset():
    RST_PIN.off()
    time.sleep(.2)
    RST_PIN.on()
    time.sleep(.2)
    return ['hwReset done.']
#############################################################################

def swReset():

    sendCmd(0x01)            # Software reset.
    time.sleep(0.2)

    sendCmd(0x11)            # Sleep out.
    time.sleep(0.2)

    sendCmd(0x36)            # Memory Data Access Control. Set orientation. 
    sendDat([0xC0])          # Bot Rt - 0x00, Bot Lft - 0x40, 
                             # Top Rt - 0x80, Top Lft - 0xC0;
                             # Portrait, Connector at bottom.

    sendCmd(0x3A)            # Interface Pixel Format.
    sendDat([0x05])          # RGB565 format (16-bit).

    sendCmd(0x29)            # Display on.

    return ['swReset done.']
#############################################################################

def setPixel(row, col, color):
    # Set a single pixel at (row,col) to specified RGB565 color.

    sendCmd(0x2B)         # Set row addr command.
    sendDat([row >> 8])   # Hi byte.
    sendDat([row & 0xFF]) # Lo byte.

    sendCmd(0x2A)         # Set col addr command.
    sendDat([col >> 8])   # Hi byte.
    sendDat([col & 0xFF]) # Lo byte.

    sendCmd(0x2C)         # Memory write command (to write the pixel data).

                          # Send the RGB565 data.
    sendDat([color >> 8, color & 0xFF])  # Send RGB565 (hi byte first).

    #print(' Pixel (row,col) = ({:3},{:3}) to color {:06x}'.\
    #      format(row, col, color))
#############################################################################

def setRow(row, startCol, numPix, color):
    # Set numPix in specified row starting at specified col to specified color.

    sendCmd(0x2B)              # Row address set.
    sendDat([row >> 8])        # Hi byte.
    sendDat([row & 0xFF])      # Lo byte.

    sendCmd(0x2A)              # Set col addr command.
    sendDat([startCol >> 8])   # Hi byte.
    sendDat([startCol & 0xFF]) # Lo byte.

    sendCmd(0x2C)              # Memory write command (to write the pixel data).

    data = [color >> 8, color & 0xFF] * numPix
    sendDat(data)              # Send RGB565 as 2 bytes (hi byte first)

    #print(' Pixel (row,col) = ({:3},{:3}) to color {:06x}'.format(y,x,color),flush = True)
#############################################################################
def setBackLight(parmLst):
    # Turn the backlight on/off.

    dsrdState = parmLst[0]
    if dsrdState == '0':
        BL_PIN.off()
    elif dsrdState == '1':
        BL_PIN.on()
    return ['done2']
#############################################################################

def display_image(image):
    width, height = image.size
    pixels = list(image.getdata())
    print(pixels[0])

    # Start sending image data
    sendCmd(0x2A)  # Column Address Set
    sendDat([0x00])
    sendDat([0x00])
    #sendDat([0x01])
    #sendDat([0x3F])  # Set column address range (0-319)
    
    sendCmd(0x2B)  # Row Address Set
    sendDat([0x00])
    sendDat([0x00])
    #sendDat([0x00])
    #sendDat([0xEF])  # Set row address range (0-239)
    
    sendCmd(0x2C)  # Memory Write

    #rgb565 = [ ((c >> 19) & 0x1F) << 11 | ((c >> 10) & 0x3F) <<  5 | ((c >>  3) & 0x1F) for c in pixels ]
    # Convert pixel (R, G, B) to a 16-bit color (5 bits for R, 6 bits for G, 5 bits for B)
    rgb565 = []
    for pixel in pixels:
        r, g, b = pixel
        rgb565.append((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))


    data1 = [byte for el in rgb565 for byte in (el >> 8, el & 0xFF)]
    data  = data1[:320*240*2]

    # Send pixel data in RGB format
    #for pixel in pixels:
        # Convert pixel (R, G, B) to a 16-bit color (5 bits for R, 6 bits for G, 5 bits for B)
        #r, g, b = pixel
        #color = (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)
        #sendDat([(color >> 8) & 0xFF])  # High byte
        #sendDat([color & 0xFF])         # Low byte
    print('&&&&&&&&&&&&&&&&&')
    sendDat(data)
#############################################################################
hwReset()  # HW Reset
swReset()  # SW Reset and the display initialization.

def setWhite(parmLst = [0,0,320*240]):
    row      = int(parmLst[0])
    startCol = int(parmLst[1])
    numPix   = int(parmLst[2])
    BL_PIN.on()    # Turn on backlight.

    time.sleep(1)  # Allow display to initialize and show content.

    colors = [~0x000000, ~0xFFFFFF, ~0xFF0000, ~0x00FF00]
    #colors = [~0x000000]
    #colors = [~0x00FF00, ~0xFF0000, ~0xFFFFFF, ~0x000000]

    ## Method 1 - Write a pixel at a time.
    #kStart = time.time()
    #for c in colors:
    #
    #    rgb565 = ((c >> 19) & 0x1F) << 11 | \
    #             ((c >> 10) & 0x3F) <<  5 | \
    #             ((c >>  3) & 0x1F)
    #
    #    for row in range(80,240):
    #        for col in range(60,180):
    #            setPixel(row, col, rgb565)  
    #print( ' Execution Time: {:8.3f} sec'.\
    #       format( time.time() - kStart))
    ####################################################

    ## Method 2 - Write a row at a time.
    #kStart = time.time()
    #startCol = 0
    #numPix   = 240
    #for c in colors:
    #
    #    rgb565 = ((c >> 19) & 0x1F) << 11 | \
    #             ((c >> 10) & 0x3F) <<  5 | \
    #             ((c >>  3) & 0x1F)
    #
    #    for row in range(0,320):
    #        setRow(row, startCol, numPix, rgb565)  
    #print( ' Execution Time: {:8.3f} sec'.\
    #       format( time.time() - kStart))
    ####################################################

    # Method 3 - Write a block at a time.
    #row = 0
    #startCol = 0
    #numPix   = 320*240
    for c in colors:

        rgb565 = ((c >> 19) & 0x1F) << 11 | \
                 ((c >> 10) & 0x3F) <<  5 | \
                 ((c >>  3) & 0x1F)

        kStart = time.time()
        setRow(row, startCol, numPix, rgb565)
        print( ' Execution Time: {:8.3f} sec'.\
               format( time.time() - kStart))
        time.sleep(.5)

    #BL_PIN.off()   # Turn off backlight. 

    ####################################

    # Set the font path (make sure the font file is in the same directory or specify full path)
    font_path = 'Font00.ttf'
    try:
        font = ImageFont.truetype(font_path, 80)  # Set font size to 80
    except IOError:
        print('Font file not found. Please check the path.')
        return

    # Create an image with white background
    image = Image.new('RGB', (320, 240), (255, 255, 255))  # RGB mode with white background
    draw = ImageDraw.Draw(image)

    # Define the text to display (number "1")

    text = "1"
    bbox = draw.textbbox((0, 0), text, font=font)  # Get the bounding box of the text
    text_width = bbox[2] - bbox[0]  # Calculate width from bbox
    text_height = bbox[3] - bbox[1]  # Calculate height from bbox
    
    # Calculate position to center the text on the screen
    x_pos = (320 - text_width) // 2
    y_pos = (240 - text_height) // 2
    
    # Draw the text on the image (black text)
    draw.text((x_pos, y_pos), text, font=font, fill=(0, 0, 0))

    # Display the image on the LCD
    display_image(image)

    # Keep the image on the screen for a while (5 seconds)
    time.sleep(5)
    ####################################
    #spi.close()
    return ['done2']
#############################################################################

if __name__ == '__main__':
    setWhite()
