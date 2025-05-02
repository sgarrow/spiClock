import os
import pickle
import inspect

activeDigitStyle = 'whiteOnBlack'      # pylint: disable=C0103
dayDigitStyle    = 'orangeOnTurquoise' # pylint: disable=C0103
nightDigitStyle  = 'greyOnBlack'       # pylint: disable=C0103
#############################################################################
#############################################################################

def getDayStyle():
    return [dayDigitStyle]
def getNightStyle():
    return [nightDigitStyle]
def getActiveStyle():
    return [activeDigitStyle]
#############################################################################

def setStyleDriver(prmLst):

    # Returns a rps str and a digitStyleStr, like 'blackOnWhite'.
    # Just sets the name doesn't activate it, that's done by loadActiveStyle.
    whoCalledMeFuncNameStr = inspect.stack()[1][3]
    if whoCalledMeFuncNameStr   == 'setDayStyle':
        digitStyleStr = dayDigitStyle
    elif whoCalledMeFuncNameStr == 'setNightStyle':
        digitStyleStr = nightDigitStyle
    elif whoCalledMeFuncNameStr == 'setActiveStyle':
        digitStyleStr = activeDigitStyle
    else:
        digitStyleStr = 'ERROR' # Should never get here.

    if len(prmLst) > 0:
        dsrdStyleIdx = prmLst[0]
    else:
        rspStr  = ' Style not set.\n'
        rspStr += ' No style number specified.'
        return [rspStr, digitStyleStr]

    rspLst     = getAllStyles()
    funcRspStr = rspLst[0]
    styleDic   = rspLst[1]      # eg: {0: 'whiteOnBlack', 1: 'blackOnWhite'}.

    if len(styleDic) > 0:
        if dsrdStyleIdx.isnumeric() and int(dsrdStyleIdx) < len(styleDic):
            # if 'Style set' in rspStr: check is performed in setActiveStyle.
            rspStr  = ' Style set to {}.'.format(styleDic[int(dsrdStyleIdx)])
            digitStyleStr = styleDic[int(dsrdStyleIdx)] # eg: 'whiteOnBlack'.
        else:
            rspStr  = ' Style not set.\n'
            rspStr += ' Invalid style number ({}), try on of these (enter number):\n\n{}'.\
                format(dsrdStyleIdx, funcRspStr)
    else:
        rspStr  = ' Style not set.\n'
        rspStr += ' No styles found in directory spiClock/digitScreenStyles.'

    return rspStr, digitStyleStr
#############################################################################

def setDayStyle(prmLst):
    global dayDigitStyle   # pylint: disable=W0603
    rspStr, dayDigitStyle = setStyleDriver(prmLst)
    return [rspStr, dayDigitStyle]
#############################################################################

def setNightStyle(prmLst):
    global nightDigitStyle  # pylint: disable=W0603
    rspStr, nightDigitStyle = setStyleDriver(prmLst)
    return [rspStr, dayDigitStyle]
#############################################################################

def setActiveStyle(prmLst):
    global activeDigitStyle # pylint: disable=W0603
    lcdCq = prmLst[1]
    rspStr, activeDigitStyle = setStyleDriver(prmLst)
    if 'Style set' in rspStr:
        lcdCq.put(activeDigitStyle)     # Send cmd to lcdUpdateProc.
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
    try:
        with open(fullFileName, 'rb') as f:
            digitDict = pickle.load(f)
    except FileNotFoundError:
        rspStr = ' ERROR: Could not load file {}.'.format(fullFileName)
        digitDict = {}
    else:
        rspStr = ' SUCCESS: File {} loaded'.format(activeStyle)

    return [rspStr, digitDict]
#############################################################################
