import os
import pickle
from PIL import Image, ImageDraw, ImageFont # pylint: disable=E0401
#############################################################################
#############################################################################

def makeColoredPRSLstsOfBytes(c):

    # Creates and returns a pixel, a row and a screens worth of LCD data of
    # the specified color.
    #
    # Only called by functions in testRoutines.py.

    # red       green     blue      white     black
    # 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF, 0x000000

    rgb565 = ((c>>19) & 0x1F) << 11 | ((c>>10)&0x3F) << 5 | ((c>>3)&0x1F)
    pLst   = [ rgb565 >> 8, rgb565 & 0xFF ]
    rLst   = pLst * 240
    sLst   = rLst * 320

    return pLst,rLst,sLst
#############################################################################

def makePilTextImage(text, textColor, backgroundColor):

    # Creates and returns a screens worth of LCD data.  The LCD data is
    # created by the PIL module.  The LCD image created is typically a
    # colored digit ('0'-'9') on colored background.
    #
    # Called by mkDigPikFile(), below, to make the digits for the clock.
    #
    # Also called by functions in testRoutines.py.

    font = ImageFont.truetype('fonts/Font00.ttf' , 300)  # Set font size to 80

    # Create an RGB image with white background.
    image = Image.new('RGB', (240, 320), backgroundColor)
    draw  = ImageDraw.Draw(image)

    # Define a bounding box.
    #
    #
    #  bbox[0],bbox[1]     bbox[2],bbox[1]
    #    +-------------------+
    #    |                   |
    #    |                   |
    #    |                   |
    #    |                   |
    #    +-------------------+
    #  bbox[0],bbox[0]     bbox[0],bbox[0]
    #
    bbox = draw.textbbox( (0, 0), text, font = font )
    textWidth  = bbox[2] - bbox[0]  # Calculate width  from bbox.
    textHeight = bbox[3] - bbox[1]  # Calculate height from bbox.

    # Calculate position to center the text on the screen.
    #xPos = ( 320 - textWidth  ) // 2 orig
    #yPos = ( 240 - textHeight ) // 2 orig
    xPos = ( 240 - textWidth  ) // 2    # Move left/right
    yPos = ( 320 - textHeight ) // 2    # Move up/down

    #print( 'upperLeft  (x,y) = ({:3},{:3}))'.format( bbox[0] + xPos, bbox[1] + yPos-100 ))
    #print( 'lowerRight (x,y) = ({:3},{:3}))'.format( bbox[2] + xPos, bbox[3] + yPos-100 ))
    #
    #print('textWidth  = {}'.format( textWidth  ))
    #print('textHeight = {}'.format( textHeight ))
    #print('xPos       = {}'.format( xPos       ))
    #print('yPos       = {}'.format( yPos       ))

    draw.text((xPos, yPos-100), text, font = font, fill = textColor )


    #draw.rectangle( ( bbox[0] + xPos,
    #                  bbox[1] + yPos-100,
    #                  bbox[2] + xPos,
    #                  bbox[3] + yPos-100 ),
    #
    #                  outline='red' )

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

    # Creates and returns a screens worth of LCD data.  The LCD data is
    # created from an RGB image.
    #
    # Only called by functions in testRoutines.py.

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

    # Creates and returns a screens worth of LCD data.  The LCD data is
    # created from a jpg image.
    #
    # Only called by functions in testRoutines.py.

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

def mkDigPikFile( styleName, textLst, textColor, backgroundColor ):

    # Makes a dict & saves it to a pik file in the digitScreenStyles subdir.
    # The dict keys are (typically) '0'-'9' and the corresponding vals are a
    # whole screens worth of data containing the corresponding key image, in
    # the specfied textColor, on the specified background color.
    #
    # This func is called by this module's 'main'.  So when this module is
    # run stand-alone on the command line the default digit styles are all
    # created.
    #
    # This func is called by mkUserDigPikFile which is available to the user
    # (client), giving users the ablity to create their own digit styles.
    #
    # This function is also called by functions in testRoutines.py.

    print('making',styleName)

    digitScreenDict2 = {}
    for t in textLst:
        tData = makePilTextImage( t, textColor, backgroundColor )
        digitScreenDict2[t] = tData

    fName = 'digitScreenStyles/{}.pickle'.format(styleName)
    with open(fName, 'wb') as handle:
        pickle.dump(digitScreenDict2, handle)
    print(' {} saved.'.format(fName))

    return ['{} made.'.format(styleName)]
#############################################################################

def mkUserDigPikFile(parmLst):

    # User interface to mkDigPikFile, see comment therein.

    if len(parmLst) < 7:
        print('too few parms')
        return ['done']
    if not all( s.isdigit() for s in parmLst[1:] ):
        print('non digit detected')
        return ['done']
    sixNums = [ int(ii) for ii in parmLst[1:] ]
    if not all(x < 256 for x in sixNums):
        print('> 255 detected')
        return ['done']

    textLst = ['0','1','2','3','4','5','6','7','8','9']
    st  = parmLst[0]
    tc  = ( sixNums[0],sixNums[1],sixNums[2] )
    bc  = ( sixNums[3],sixNums[4],sixNums[5] )
    rsp = mkDigPikFile(st, textLst, tc, bc)

    return rsp
#############################################################################

# The active digit style is what the clock will use.  This module global
# variable can be read and changed by the user and system internals via the
# get/set functions, below.

activeDigitStyle = 'whiteOnBlack' # pylint: disable=C0103

def getActiveStyle():           ######################
    return [activeDigitStyle]

def setActiveStyle(prmLst):     ######################
    global activeDigitStyle

    if len(prmLst) > 0:
        dsrdDigitStyle = prmLst[0]
        #lcdCq, lcdRq, clkCq, clkRq = qLst[1][0], qLst[1][1], qLst[1][2], qLst[1][3]
        lcdCq = prmLst[1][0]
    else:
        rspStr  = ' Digit Style not set.\n'
        rspStr += ' No style specified.'
        return [rspStr, activeDigitStyle]

    rspLst     = getAllStyles()
    funcRspStr = rspLst[0]
    styleLst   = rspLst[1]

    if len(styleLst) > 0:
        if dsrdDigitStyle in styleLst:
            rspStr  = ' Digit Style set to {}.'.format(dsrdDigitStyle)
            activeDigitStyle = dsrdDigitStyle
            lcdCq.put(activeDigitStyle)     # Send cmd to lcdUpdateProc.
        else:
            rspStr  = ' Digit Style not set.\n'
            rspStr += ' Invalid style ({}), try on of these:\n\n{}'.\
                format(dsrdDigitStyle, funcRspStr)
    else:
        rspStr  = ' Digit Style not set.\n'
        rspStr += ' No styles found in directory spiClock/digitScreenStyles.'

    return [rspStr, activeDigitStyle]
#############################################################################

def getAllStyles():

    # Basically just returns a list of all files in digitScreenStyles subdir.
    # Can be called by the user (client) and also called by functions in
    # testRoutines.py and by setActiveStyle(), above.  If the user specifies
    # a non-existant style the a list of available styles is given to them.

    dPath = 'digitScreenStyles'
    try:
        fileNameLst = os.listdir(dPath)
    except FileNotFoundError:
        fileNameLstNoExt = []
        rspStr = ' Directory {} not found.'.format(dPath)
    else:
        fileNameLstNoExt = [os.path.splitext(file)[0] for file in fileNameLst]
        rspStr  = ' '
        rspStr += ' \n '.join(fileNameLstNoExt)

    return [rspStr,fileNameLstNoExt]
#############################################################################

def loadActiveStyle():

    # Loads the dictionary (of digits/data) from the assocoated pickle file.
    # Called at clock startup (lcdUpdateProc start).  Also called when the
    # clock is alreadt running but the user changes the active style.

    activeStyle = getActiveStyle()
    dirPath = 'digitScreenStyles'
    fullFileName = os.path.join(dirPath, activeStyle[0]+'.pickle')
    print(fullFileName)
    with open(fullFileName, 'rb') as f:
        digitDict = pickle.load(f)
    rspStr = ' {} loaded'.format(activeStyle)
    return [rspStr, digitDict]
#############################################################################

if __name__ == '__main__':

    black     = (   0,   0,   0 )
    white     = ( 255, 255, 255 )
    orange    = ( 239, 144,   1 )
    turquoise = (  18, 151, 128 )
    txtLst   = ['0','1','2','3','4','5','6','7','8','9']

    styleNames = [ 'whiteOnBlack',      'blackOnWhite',
                   'orangeOnTurquoise', 'turquoiseOnOrange']
    txtColors  = [ white, black, orange,    turquoise ]
    backColors = [ black, white, turquoise, orange    ]

    for style,tColor,bColor in zip(styleNames, txtColors, backColors):
        resp = mkDigPikFile(style, txtLst, tColor, bColor)
        print(resp)

    mnDirPath = 'digitScreenStyles' # pylint: disable=C0103
    try:
        for fileName in os.listdir(mnDirPath):
            mnFullFileName = os.path.join(mnDirPath, fileName)
            if os.path.isfile(mnFullFileName):
                print('Processing file: {}'.format(mnFullFileName))
                with open(mnFullFileName, 'rb') as fn:
                    styleDict = pickle.load(fn)
                    print(styleDict.keys())
    except FileNotFoundError:
        print(f"Error: Directory '{mnDirPath}' not found.")
    except Exception as e: # pylint: disable=W0718
        print(f"An error occurred: {e}")
