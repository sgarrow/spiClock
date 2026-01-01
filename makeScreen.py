import os
import time
import pickle
from PIL import Image, ImageDraw, ImageFont # pylint: disable=E0401
import styleMgmtRoutines as sm
import startStopClock    as cr
import spiRoutines       as sr
import utils             as ut
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

def mkPilTxtImg( text, textColor, backgroundColor,
                 yOffset= 100, fontSize= 300, fontName= 'fonts/Font00.ttf'):

    # Creates and returns a screens worth of LCD data.  The LCD data is
    # created by the PIL module.  The LCD image created is typically a
    # colored digit ('0'-'9') on colored background.
    #
    # Called by mkDigPikFile(), below, to make the digits for the clock.
    #
    # Also called by functions in testRoutines.py.

    font = ImageFont.truetype( fontName , fontSize )
    # Create an RGB image with specified background color.
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
    xPos = ( 240 - textWidth  ) // 2    # Move left/right
    yPos = ( 320 - textHeight ) // 2    # Move up/down

    #print( 'upperLeft  (x,y) = ({:3},{:3}))'.format( bbox[0] + xPos, bbox[1] + yPos-100 ))
    #print( 'lowerRight (x,y) = ({:3},{:3}))'.format( bbox[2] + xPos, bbox[3] + yPos-100 ))
    #
    #print('textWidth  = {}'.format( textWidth  ))
    #print('textHeight = {}'.format( textHeight ))
    #print('xPos       = {}'.format( xPos       ))
    #print('yPos       = {}'.format( yPos       ))

    draw.text((xPos, yPos-yOffset), text, font = font, fill = textColor )


    #draw.rectangle( ( bbox[0] + xPos,
    #                  bbox[1] + yPos-100,
    #                  bbox[2] + xPos,
    #                  bbox[3] + yPos-100 ),
    #
    #                  outline='red' )
    #
    #draw.rectangle( ( bbox[0] + xPos,
    #                  bbox[1] + yPos-50,
    #                  bbox[2] + xPos,
    #                  bbox[3] + yPos-50 ),
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
    # This func is called by mkDigPikFile which is available to the user
    # (client), giving users the ablity to create their own digit styles.
    #
    # This function is also called by functions in testRoutines.py.

    #print('making',styleName)

    digitScreenDict2 = {}
    for ii,t in enumerate(textLst):
        if t in ['0','1','2','3','4','5','6','7','8','9']:
            tData = mkPilTxtImg( t, textColor, backgroundColor )
        else:
            tData = mkPilTxtImg( t, textColor, backgroundColor,
                                 fontName = 'fonts/NotoSerifTC-Light.ttf',
                                 fontSize = 200, yOffset = 75 )

        digitScreenDict2[str(ii)] = tData

    fName = 'digitScreenStyles/{}.pickle'.format(styleName)
    with open(fName, 'wb') as handle:
        pickle.dump(digitScreenDict2, handle)
    #print(' {} saved.'.format(fName))

    fName = 'digitScreenStyles/{}.RGB.txt'.format(styleName)
    with open(fName, 'w', encoding='utf-8') as handle:
        tmpStr = ' '.join(map(str, textColor)) +  ' '
        handle.write( tmpStr )
        tmpStr = ' '.join(map(str, backgroundColor))
        handle.write( tmpStr )
    #print(' {} saved.'.format(fName))

    return ['{} made.'.format(styleName)]
#############################################################################

def mkUsrDigPikF( parmLst ):

    # User interface to mkDigPikFile, see comment therein.

    #kStart = time.perf_counter()

    usage = ''' ERROR: {}
 Required Parameters: styleName R G B R G B
 Example: redOnBlue 255 0 0 0 0 255
 The first parm is the name of the style.
 Next 3 parms are the RGB values used for the digit
 Last 3 parms are the RGB values used for the background.'''

    if len(parmLst) != 7:
        return [usage.format('Incorrect number of parameters.')]
    if not all( s.isdigit() for s in parmLst[1:] ):
        return [usage.format('Non-digit detected.')]

    sixNums = [ int(ii) for ii in parmLst[1:] ]

    if not all(x < 256 for x in sixNums):
        return [usage.format('> 255 detected.')]

    textLst = ['0','1','2','3','4','5','6','7','8','9']
    st  = parmLst[0]
    tc  = ( sixNums[0],sixNums[1],sixNums[2] )
    bc  = ( sixNums[3],sixNums[4],sixNums[5] )
    rsp = mkDigPikFile(st, textLst, tc, bc)
    #exeTime = time.perf_counter()-kStart # pylint: disable=W0612
    #print('Time spent updating counter = {:10.6f}'.format(exeTime))

    return rsp
#############################################################################

def delUsrDigPikF( parmLst ):

    usage = ''' ERROR: {}
 Required Parameters: styleNumber
 Example: 5
 The parm is the index number of the style to delete.
{} '''

    rspLst      = sm.getAllStyles()
    funcRspStr  = rspLst[0]
    allStyleDic = rspLst[1]  # eg: {0: 'whiteOnBlack', 1: 'blackOnWhite'}.
    greyOnBlackKey = next((k for k, v in allStyleDic.items() if v == 'greyOnBlack'), None)

    if parmLst[0] == 'None' or len(parmLst[0]) != 1:
        return [usage.format(' Incorrect number of parameters.',funcRspStr)]
    if not all( s.isdigit() for s in parmLst[0] ):
        return [usage.format(' Non-digit detected in parameter.',funcRspStr)]

    dsrdStyleIdx,styleDict,styleDictLock,lcdCq = \
    int(parmLst[0][0]),parmLst[1],parmLst[2],parmLst[3]

    if dsrdStyleIdx not in allStyleDic:
        return [usage.format(' Parameter out of range.',funcRspStr)]

    if allStyleDic[dsrdStyleIdx] == 'greyOnBlack':
        return [usage.format(' Style greyOnBlack cannot be deleted.',funcRspStr)]


    rspStr = ''
    ads = sm.getActStyle( [styleDict, styleDictLock] )[0]
    dds = sm.getDayStyle(    [styleDict, styleDictLock] )[0]
    nds = sm.getNightStyle(  [styleDict, styleDictLock] )[0]

    if ads == allStyleDic[dsrdStyleIdx]:
        sm.setActStyle( [str(greyOnBlackKey), styleDict, styleDictLock,lcdCq] )
        rspStr += ' Active Style changed from {} to greyOnBlack.\n'.format(ads)
    if dds == allStyleDic[dsrdStyleIdx]:
        sm.setDayStyle( [str(greyOnBlackKey), styleDict, styleDictLock] )
        rspStr += ' Day Style changed from {} to greyOnBlack.\n'.format(dds)
    if nds == allStyleDic[dsrdStyleIdx]:
        sm.setNightStyle( [str(greyOnBlackKey), styleDict, styleDictLock] )
        rspStr += ' Night Style changed from {} to greyOnBlack.\n'.format(nds)

    fName = 'digitScreenStyles/{}.RGB.txt'.format(allStyleDic[dsrdStyleIdx] )
    os.remove(fName)
    fName = 'digitScreenStyles/{}.pickle'.format( allStyleDic[dsrdStyleIdx] )
    os.remove(fName)

    rspStr += ' Style {} deleted.'.format(allStyleDic[dsrdStyleIdx])
    return [rspStr]
#############################################################################

def removePic(parmLst):
    usage = ''' ERROR:
{}
 Required Parameters: picNumber
 The parm is the index number of the pic to delete.
{} '''

    rspStr    = ''
    picDicStr = ''
    dPath     = 'pics'
    nonDigitDetected = False

    if parmLst[0] == 'None' or len(parmLst) != 1:
        rspStr += ' Incorrect number of parameters.\n'
    if not all( s.isdigit() for s in parmLst[0] ):
        rspStr += ' Non-digit detected in parameter.\n'
        nonDigitDetected = True

    try:
        picDic= dict(enumerate(sorted(os.listdir(dPath))))
    except FileNotFoundError:
        rspStr += ' Directory {} not found.\n'.format(dPath)
    else:
        if len(picDic) == 0:
            rspStr += ' No pictures to remove.\n'
        else:
            for k,v in picDic.items():
                picDicStr += '\n {:2} - {}'.format(k,v)

    if not nonDigitDetected:
        dicIdx = int(parmLst[0])
        if dicIdx > len(picDic):
            rspStr += ' Parameter out of range.'

    if rspStr != '':
        return [usage.format(rspStr,picDicStr)]

    fName = '{}/{}'.format(dPath,picDic[dicIdx] )
    os.remove(fName)
    rspStr = '{} removed'.format(fName )
    return [rspStr]
#############################################################################
#############################################################################

def repeatListToMatchLength(listToRepeat, targetList):
    """
    Repeats a list until its length matches the length of a target list.
    Args:
        listToRepeat: The list to be repeated.
        targetList: The list whose length should be matched.
    Returns:
        A new list that is a repeated version of listToRepeat,
        truncated or extended to match the length of targetList.
    """
    if not listToRepeat:
        return []

    targetLength = len(targetList)
    repeatedList = (listToRepeat * (targetLength // len(listToRepeat))) + \
                    listToRepeat[:targetLength % len(listToRepeat)]
    return repeatedList
#################################################################

def displayPics(prmLst):

    dPath  = 'pics'
    picLst = sorted(os.listdir(dPath))
    if len(picLst) == 0:
        return [' No pics found.']

    startTimeLst,qs,styleDic,styleLk = prmLst[0], prmLst[1], prmLst[2], prmLst[3]
    rspStr = ut.getActThrds()
    dspIdLst = [ 'hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD' ]
    lenDspIdLst = len(dspIdLst)
    stoppedClock = False
    if 'clockCntrProc' in rspStr[0] or 'lcdUpdateProc' in rspStr[0]:
        #print('stopping clock')
        cr.stopClk(qs)
        stoppedClock = True

    ##################################
    rspStr = ut.getActThrds()
    if 'MainThread' not in rspStr[0]:
        #print('reseting LCD')

        sr.hwReset()              # HW Reset
        for displayID in dspIdLst:
            sr.swReset(displayID) # SW Reset and the display initialization.

    sr.setBkLight([1])            # Turn on backlight.

    # Shortest list is list to repeat.
    if len(picLst) < len(dspIdLst):
        #                                 (lstToRepeat, targetLst)
        picLst   = repeatListToMatchLength(picLst,      dspIdLst )
    else:
        #                                 (lstToRepeat, targetLst)
        dspIdLst = repeatListToMatchLength(dspIdLst,    picLst   )

    for ii,(d,p) in enumerate(zip(dspIdLst, picLst)):
        slept = False
        data = makePilJpgPicImage('{}{}{}'.format(dPath,'/',p))
        sr.setEntireDisplay( d, data, sr.sendDat2ToSt7789 )
        #print(d,p)
        if  (ii+1) % lenDspIdLst == 0:
            time.sleep(3)
            slept = True
    if not slept:
        time.sleep(3)
    ##################################

    if stoppedClock:
        #print('starting clock')
        cr.startClk([startTimeLst,qs,styleDic,styleLk])

    return ['done']
#############################################################################

if __name__ == '__main__':

    black     = (   0,   0,   0 )
    grey      = ( 128, 128, 128 )
    white     = ( 255, 255, 255 )
    orange    = ( 239, 144,   1 )
    turquoise = (  18, 151, 128 )
    lightRed  = (  96,   0,   0 )
    txtLst   = ['0','1','2','3','4','5','6','7','8','9']
    chineseTxtLst = [ '\u58de', '\u52d2', '\u5ff5', '\u64e6', '\u6b3e',
                      '\u79aa', '\u4f7f', '\u63e1', '\u6a5f', '\u760b']


    # greyOnBlack is default style and can not be deleted.
    styleNames = [ 'whiteOnBlack',      'blackOnWhite',
                   'orangeOnTurquoise', 'turquoiseOnOrange',
                   'greyOnBlack',       'ltRedOnBlack']
    txtColors  = [ white, black, orange,    turquoise, grey,  lightRed ]
    backColors = [ black, white, turquoise, orange,    black, black ]

    for style,tColor,bColor in zip(styleNames, txtColors, backColors):
        resp = mkDigPikFile(style, txtLst, tColor, bColor)
        print(resp)

    resp = mkDigPikFile('chinese', chineseTxtLst, black, white)

    print(resp)

    mnDirPath = 'digitScreenStyles' # pylint: disable=C0103
    try:
        for fileName in os.listdir(mnDirPath):
            if fileName.endswith('pickle'):
                mnFullFileName = os.path.join(mnDirPath, fileName)
                if os.path.isfile(mnFullFileName):
                    print('Processing file: {}'.format(mnFullFileName))
                    with open(mnFullFileName, 'rb') as fn:
                        mnStyleDict = pickle.load(fn)
                        print(mnStyleDict.keys())
    except FileNotFoundError:
        print(f"Error: Directory '{mnDirPath}' not found.")
    except Exception as e: # pylint: disable=W0718
        print(f"An error occurred: {e}")
#############################################################################
