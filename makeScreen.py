import time
from PIL import Image, ImageDraw, ImageFont
import cfgDict     as cd
import spiRoutines as sr
#############################################################################

def makeColoredPRSLstsOfBytes(c):

    # red       green     blue      white     black
    # 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF, 0x000000

    rgb565 = ((c>>19) & 0x1F) << 11 | ((c>>10)&0x3F) << 5 | ((c>>3)&0x1F)
    pLst   = [ rgb565 >> 8, rgb565 & 0xFF ]
    rLst   = pLst * 240
    sLst   = rLst * 320

    return pLst,rLst,sLst
#############################################################################

def makePilTextImage(text, textColor, backgroundColor):

    font = ImageFont.truetype('fonts/Font00.ttf' , 300)  # Set font size to 80

    # Create an RGB image with white background.
    image = Image.new('RGB', (240, 320), backgroundColor)
    draw  = ImageDraw.Draw(image)

    # Define a bounding box.
    bbox = draw.textbbox( (0, 0), text, font = font )
    textWidth  = bbox[2] - bbox[0]  # Calculate width  from bbox.
    textHeight = bbox[3] - bbox[1]  # Calculate height from bbox.

    # Calculate position to center the text on the screen.
    #xPos = ( 320 - textWidth  ) // 2 orig
    #yPos = ( 240 - textHeight ) // 2 orig
    xPos = ( 240 - textWidth  ) // 2    # Move left/right
    yPos = ( 320 - textHeight ) // 2    # Move up/down

    #print('textWidth  = {}'.format( textWidth  ))
    #print('textHeight = {}'.format( textHeight ))
    #print('xPos       = {}'.format( xPos       ))
    #print('yPos       = {}'.format( yPos       ))

    draw.text((xPos, yPos-100), text, font = font, fill = textColor )

    draw.rectangle( ( bbox[0] + xPos,
                      bbox[1] + yPos-100,
                      bbox[2] + xPos,
                      bbox[3] + yPos-100 ),

                      outline='red' )

    #width, height = image.size
    pixels = list(image.getdata())
    rgb565Lst = []

    for row in range(320):
        for col in range(240):
            pixel = pixels[row*240+col]
            r, g, b = pixel
            rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
            rgb565Lst.append(rgb565)

    byteLst = [byte for el in rgb565Lst for byte in (el >> 8, el & 0xFF)]

    return byteLst
#############################################################################

def makePilRgbPicImage(fName):
    rgb565Lst = []
    with open(fName, 'rb') as file:
        while True:
            # Read 3 bytes at a time (one pixel)
            pixelData = file.read(3)
            if not pixelData:
                break
            # Unpack the bytes into RGB values
            r, g, b = pixelData
            rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
            rgb565Lst.append(rgb565)
    byteLst = [byte for el in rgb565Lst for byte in (el >> 8, el & 0xFF)]
    return byteLst
#############################################################################

def makePilJpgPicImage(fName):
    with Image.open(fName) as img:
        rgbImage = img.convert('RGB')
    pixels = list(rgbImage.getdata())
    rgb565Lst = []
    for row in range(320):
        for col in range(240):
            pixel = pixels[row*240+col]
            r, g, b = pixel
            rgb565 = ((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3))
            rgb565Lst.append(rgb565)
    byteLst = [byte for el in rgb565Lst for byte in (el >> 8, el & 0xFF)]
    return byteLst
#############################################################################

def makeDigitScreens( screenDict, styleName,
                      txtLst, textColor, backgroundColor):
    print('making',styleName)
    screenDict[styleName] = {}
    for t in txtLst:
        screenDict[styleName][t] = \
        makePilTextImage( t, textColor, backgroundColor )
    return screenDict
#############################################################################

if __name__ == '__main__':

    #cfgDict = { 'digitScreenDict' : { 'whiteOnBlack': { '0': data,
    #                                                    '1': data
    #                                                  },
    #                                  'blackOnWhite': { '0': data,
    #                                                    '1': data
    #                                                  }
    #                                },
    #
    #            'someOtherDict'   : someOtherValue
    #          }

    white     = (   0,   0,   0 )
    black     = ( 255, 255, 255 )
    orange    = ( 239, 144,   1 )
    turquoise = (  18, 151, 128 )
    textLst = ['0','1','2','3','4','5','6','7','8','9']

    digitScreenDict = {}

    digitScreenDict = makeDigitScreens(
    digitScreenDict, 'whiteOnBlack',      textLst, white,     black     )

    digitScreenDict = makeDigitScreens(
    digitScreenDict, 'blackOnWhite',      textLst, black,     white     )

    digitScreenDict = makeDigitScreens(
    digitScreenDict, 'orangeOnTurquoise', textLst, orange,    turquoise )

    digitScreenDict = makeDigitScreens(
    digitScreenDict, 'turquoiseOnOrange', textLst, turquoise, orange    )


    cfgDict = cd.loadCfgDict()
    cfgDict = cd.updateCfgDict( cfgDict, digitScreenDict = digitScreenDict )
    cfgDict = cd.saveCfgDict( cfgDict )
    cd.runTest()
    #########################

    sr.setBackLight([1]) # Turn on backlight.
    sr.hwReset()         # HW Reset
    sr.swReset()         # SW Reset and the display initialization.

    digitScreenDict = cfgDict['digitScreenDict']

    for style in digitScreenDict.keys():
        for k in textLst:
            data = digitScreenDict[style][k]
            sr.setEntireDisplay(data, sr.sendDat2ToSt7789)
            time.sleep(.5)

    sr.setBackLight([0]) # Turn off backlight.
    sr.hwReset()         # HW Reset
