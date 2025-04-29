import os
import pickle
# The active digit style is what the clock will use.  This module global
# variable can be read and changed by the user and system internals via the
# get/set functions, below.

activeDigitStyle = 'whiteOnBlack' # pylint: disable=C0103

def getActiveStyle():           ######################
    return [activeDigitStyle]

def setActiveStyle(prmLst):     ######################
    global activeDigitStyle

    if len(prmLst) > 0:
        dsrdDigitStyleIdx = prmLst[0]
        #lcdCq, lcdRq, clkCq, clkRq = qLst[1][0], qLst[1][1], qLst[1][2], qLst[1][3]
        lcdCq = prmLst[1][0]
    else:
        rspStr  = ' Digit Style not set.\n'
        rspStr += ' No style number specified.'
        return [rspStr, activeDigitStyle]

    rspLst     = getAllStyles()
    funcRspStr = rspLst[0]
    styleDic   = rspLst[1]

    if len(styleDic) > 0:
        if dsrdDigitStyleIdx.isnumeric() and int(dsrdDigitStyleIdx) < len(styleDic):
            rspStr  = ' Digit Style set to {}.'.format(styleDic[int(dsrdDigitStyleIdx)])
            activeDigitStyle = styleDic[int(dsrdDigitStyleIdx)]
            lcdCq.put(activeDigitStyle)     # Send cmd to lcdUpdateProc.
        else:
            rspStr  = ' Digit Style not set.\n'
            rspStr += ' Invalid style number ({}), try on of these (enter number):\n\n{}'.\
                format(dsrdDigitStyleIdx, funcRspStr)
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
        rspStr  = ''
        fileNameLstNoExt = [os.path.splitext(file)[0] for file in fileNameLst]
        fileNameDicNoExt = dict(enumerate(fileNameLstNoExt))
        for k,v in fileNameDicNoExt.items():
            rspStr += ' {} - {}\n'.format(k,v)

    return [rspStr,fileNameDicNoExt]
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
