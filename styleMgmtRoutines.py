import os
import pickle
import inspect
#############################################################################
#############################################################################

def getDayStyle(prmLst):
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        dayDigitStyle = styleDict['dayDigitStyle']
    return [dayDigitStyle]

def getNightStyle(prmLst):
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        nightDigitStyle = styleDict['nightDigitStyle']
    return [nightDigitStyle]

def getActiveStyle(prmLst):
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        activeDigitStyle = styleDict['activeDigitStyle']
    return [activeDigitStyle]
#############################################################################

def setStyleDriver(prmLst):

    dsrdStyleIdx, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    # Returns a rps str and a digitStyleStr, like 'blackOnWhite'.
    # Just sets the name doesn't activate it, that's done by loadActiveStyle.
    whoCalledMe = inspect.stack()[1][3]
    with styleDictLock:
        if    whoCalledMe == 'setDayStyle':    digitStyleStr = styleDict['dayDigitStyle']
        elif  whoCalledMe == 'setNightStyle':  digitStyleStr = styleDict['nightDigitStyle']
        elif  whoCalledMe == 'setActiveStyle': digitStyleStr = styleDict['activeDigitStyle']
        else: digitStyleStr = 'ERROR' # Should never get here.

    rspLst      = getAllStyles()
    funcRspStr  = rspLst[0]
    allStyleDic = rspLst[1]      # eg: {0: 'whiteOnBlack', 1: 'blackOnWhite'}.

    if dsrdStyleIdx == 'None':
        rspStr  = ' Style not set.\n'
        rspStr += ' No style number specified.'
        rspStr += ' Invalid style number ({}), try on of these (enter number):\n\n{}'.\
            format(dsrdStyleIdx, funcRspStr)
        return [rspStr, digitStyleStr]

    if len(allStyleDic) > 0:
        if dsrdStyleIdx.isnumeric() and int(dsrdStyleIdx) < len(allStyleDic):
            # if 'Style set' in rspStr: check is performed in setActiveStyle.
            rspStr  = ' Style set to {}.'.format(allStyleDic[int(dsrdStyleIdx)])
            digitStyleStr = allStyleDic[int(dsrdStyleIdx)] # eg: 'whiteOnBlack'.
            with styleDictLock:
                if whoCalledMe   == 'setDayStyle':
                    styleDict['dayDigitStyle']    = allStyleDic[int(dsrdStyleIdx)]
                elif whoCalledMe == 'setNightStyle':
                    styleDict['nightDigitStyle']  = allStyleDic[int(dsrdStyleIdx)]
                elif whoCalledMe == 'setActiveStyle':
                    styleDict['activeDigitStyle'] = allStyleDic[int(dsrdStyleIdx)]
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
    #dsrdStyleIdx, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    rspStr, dayDigitStyle = setStyleDriver(prmLst)
    return [rspStr, dayDigitStyle]
#############################################################################

def setNightStyle(prmLst):
    #dsrdStyleIdx, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    rspStr, nightDigitStyle = setStyleDriver(prmLst)
    return [rspStr, nightDigitStyle]
#############################################################################

def setActiveStyle(prmLst):
    #dsrdStyleIdx,styleDict,styleDictLock,lcdCq=prmLst[0],prmLst[1],prmLst[2],prmLst[3]
    lcdCq = prmLst[3]
    rspStr, activeDigitStyle = setStyleDriver(prmLst)
    if 'Style set' in rspStr:
        lcdCq.put('loadActiveStyle')     # Send cmd to lcdUpdateProc.
    return [rspStr, activeDigitStyle]
#############################################################################

def getAllStyles():
    # Returns a list of all files in digitScreenStyles subdir.  Can be called
    # by the user (client) and also called by functions in testRoutines.py
    # and by setActiveStyle(), above.  If the user specifies a non-existant
    # style the a list of available styles is given to them.
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

def loadActiveStyle(styleDict, styleDictLock):
    # Loads the dictionary (of digits/data) from the assocoated pickle file.
    # Called at clock startup (lcdUpdateProc start).  Also called when the
    # clock is alreadt running but the user changes the active style.
    activeStyle = getActiveStyle([styleDict, styleDictLock])
    dirPath = 'digitScreenStyles'
    fullFileName = os.path.join(dirPath, activeStyle[0]+'.pickle')
    #print(fullFileName)
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
