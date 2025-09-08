import os
import pickle
import inspect
#import pprint as pp
#############################################################################
#############################################################################

def fixDocString(func):
    func.__doc__ = func.__doc__.replace('<boiler>',
        ' \n The style naming convention is textColorOnBackgroundColor.  For\n'
        ' example whiteOnBlack means that white digits are displayed on a\n'
        ' black background.\n'
        ' =================================================================')
    return func
#############################################################################

def fixDocString2(func):
    func.__doc__ = func.__doc__.replace('<boiler2>',
        ' \n The 1 is just an example, can be any number up to the number of\n'
        ' styles available. If no number is specified an error message is\n'
        ' displayed along with a list of styles and the associated numbers.')
    return func
#############################################################################

def getDayTime(prmLst):
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        dayTime = styleDict['dayTime']

    logStr = ' Day Time is {}{}:{}{}:{}{}.'.\
    format( dayTime[0], dayTime[1], dayTime[2], 
            dayTime[3], dayTime[4], dayTime[5])

    return [logStr, dayTime]
#############################################################################

def getNightTime(prmLst):
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        nightTime = styleDict['nightTime']

    logStr = ' Night Time is {}{}:{}{}:{}{}.'.\
    format( nightTime[0], nightTime[1], nightTime[2], 
            nightTime[3], nightTime[4], nightTime[5])

    return [logStr,nightTime]
#############################################################################

def checkTime(timeStrLst):
    logStr = ''
    numLst = []

    timeStr   = ''.join(timeStrLst)
    numStrLst = [ ''.join(x) for x in timeStr if x.isdigit()]

    if len(numStrLst) != 6:
        logStr += ' ERROR. num digits not six (is {}).\n'.format(len(numStrLst))
    else:
        numLst = [ int(x) for x in numStrLst ]
        if numLst[0]*10 + numLst[1] > 23: logStr += ' ERROR. hour > 23.\n'
        if numLst[2]*10 + numLst[3] > 59: logStr += ' ERROR. min  > 59.\n'
        if numLst[4]*10 + numLst[5] > 59: logStr += ' ERROR. sec  > 59.\n'

    if logStr != '':
        logStr += ' Example time entry - 18:59:30\n'
    return logStr, numLst
#############################################################################

def setDayTime(prmLst):
    timeLst, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    logStr, sixNums = checkTime( timeLst )

    if 'ERROR' not in logStr:
        with styleDictLock:
            styleDict['dayTime'] = sixNums

        logStr += ' Day Time set to {}{}:{}{}:{}{}.'.\
        format( sixNums[0], sixNums[1], sixNums[2], 
                sixNums[3], sixNums[4], sixNums[5])
    else:
        logStr += ' Day Time not set.'

    return [logStr]
#############################################################################

def setNightTime(prmLst):
    timeLst, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    logStr, sixNums = checkTime( timeLst )

    if 'ERROR' not in logStr:
        with styleDictLock:
            styleDict['nightTime'] = sixNums

        logStr += ' Night Time set to {}{}:{}{}:{}{}.'.\
        format( sixNums[0], sixNums[1], sixNums[2], 
                sixNums[3], sixNums[4], sixNums[5])
    else:
        logStr += ' Night Time not set.'

    return [logStr]
#############################################################################
@fixDocString
def getDayStyle(prmLst):
    '''
 Displays the name of the color style the clock will automatically
 switch to at 'day time'.  The current value of 'day time' can
 be get/set via gdt and sdt commands.

 Usage: gds
<boiler>
'''
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        dayDigitStyle = styleDict['dayDigitStyle']
    return [dayDigitStyle]
#############################################################################

@fixDocString
def getNightStyle(prmLst):
    '''
 Displays the name of the color style the clock will automatically
 switch to at 'night time'.  The current value of 'night time' can
 be get/set via gnt and snt commands.

 Usage: gns
<boiler>
'''
    styleDict, styleDictLock = prmLst[0], prmLst[1]
    with styleDictLock:
        nightDigitStyle = styleDict['nightDigitStyle']
    return [nightDigitStyle]
#############################################################################

@fixDocString
def getActiveStyle(prmLst):
    '''
 Displays the name of the color style the clock is currently
 using.  

 Usage: gas
<boiler>
'''
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

@fixDocString2
@fixDocString
def setDayStyle(prmLst):
    '''
 Sets the color style the clock will automatically 
 switch to at 07 00 00.

 Usage 1: sds 1
 Usage 2: sds
<boiler2>
<boiler>
'''
    #dsrdStyleIdx, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    rspStr, dayDigitStyle = setStyleDriver(prmLst)
    return [rspStr, dayDigitStyle]
#############################################################################

@fixDocString2
@fixDocString
def setNightStyle(prmLst):
    '''
 Sets the color style the clock will automatically 
 switch to at 21 00 00.

 Usage 1: sns 1
 Usage 2: sns
<boiler2>
<boiler>
'''
    #dsrdStyleIdx, styleDict, styleDictLock = prmLst[0], prmLst[1], prmLst[2]
    rspStr, nightDigitStyle = setStyleDriver(prmLst)
    return [rspStr, nightDigitStyle]
#############################################################################

@fixDocString2
@fixDocString
def setActiveStyle(prmLst):
    '''
 Sets the color style the clock will switch to immediately.

 Usage 1: sas 1
 Usage 2: sas
<boiler2>
<boiler>
'''
    #dsrdStyleIdx,styleDict,styleDictLock,lcdCq=prmLst[0],prmLst[1],prmLst[2],prmLst[3]
    lcdCq = prmLst[3]
    rspStr, activeDigitStyle = setStyleDriver(prmLst)
    if 'Style set' in rspStr:
        lcdCq.put('loadActiveStyle')     # Send cmd to lcdUpdateProc.
    return [rspStr, activeDigitStyle]
#############################################################################

@fixDocString
def getAllStyles():
    '''
 Displays a list of styles and their associated numbers and RGB values.
 Usage 1: gAs
<boiler>
'''
    # Returns a list of all files in digitScreenStyles subdir.  Can be called
    # by the user (client) and also called by functions in testRoutines.py
    # and by setActiveStyle(), above.  If the user specifies a non-existant
    # style the a list of available styles is given to them.
    dPath= 'digitScreenStyles'
    try:
        fileNameLst = os.listdir(dPath)
    except FileNotFoundError:
        pikFileNameDicNoExt = []
        rspStr = ' Directory {} not found.'.format(dPath)
    else:
        rspStr  = ''
        pikFileNameLstNoExt = [ os.path.splitext(file)[0] for file \
                                in fileNameLst if file.endswith('pickle')]
        rgbFileNameLst      = [ f for f in fileNameLst if f.endswith('txt')]

        pikFileNameDicNoExt = dict(enumerate(pikFileNameLstNoExt))
        rgbFileNameDic      = dict(enumerate(rgbFileNameLst))

        rgbValuesDict       = {}
        for rgbs in rgbFileNameDic.values():
            with open(dPath+'/'+rgbs, 'r',encoding='utf-8') as f:
                line = f.readline()
            rgbValuesDict[rgbs] = line

        for k,v in pikFileNameDicNoExt.items():
            rspStr += ' {:2} - {:18}'.format(k,v)
            for k1,v1 in rgbValuesDict.items():
                if v in k1:
                    words = v1.split()
                    for w in words:
                        rspStr += '{:>4}'.format(w)
                    rspStr += '\n'
                    break

    return [rspStr,pikFileNameDicNoExt]
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
