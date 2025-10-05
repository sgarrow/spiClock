import sys
import datetime        as dt
import multiprocessing as mp
import threading       as th

import time
import startStopClock  as cr
import makeScreen      as ms
import spiRoutines     as sr

openSocketsLst = []    # Needed for processing close and ks commands.
#############################################################################

def getMultiProcSharedDict():
    manager = mp.Manager()
    styleDict = manager.dict({
        'activeDigitStyle': 'whiteOnBlack',
        'dayDigitStyle'   : 'orangeOnTurquoise',
        'nightDigitStyle' : 'ltRedOnBlack',
        'nightTime'       : [ 2, 1, 0, 0, 0, 0 ],
        'dayTime'         : [ 0, 7, 0, 0, 0, 0 ],
        'alarmTime'       : [ 0, 0, 0, 0, 0, 0 ], 
    })
    styleDictLock = mp.Lock()
    return styleDict, styleDictLock
#############################################################################

def getActThrds():
    rspStr = ' Running Threads:\n'
    for t in th.enumerate():
        rspStr += '   {}\n'.format(t.name)

    rspStr += '\n Open Sockets:\n'
    for ii,openS in enumerate(openSocketsLst):

        rspStr+='   Socket {} Object Information \n'.format(ii)
        rspStr+='     Remote Addr, Port: {}\n'.format(openS['cs'].getpeername())
        rspStr+='      Local Addr, Port: {}\n'.format(openS['cs'].getsockname())
        rspStr+='       File descriptor: {}\n'.format(openS['cs'].fileno()     )
        rspStr+='              Protocol: {}\n'.format(openS['cs'].proto        )
        rspStr+='                Family: {}\n'.format(openS['cs'].family       )
        rspStr+='                  Type: {}\n'.format(openS['cs'].type         )

        rspStr+='   Socket {} Address Information \n'.format(ii)
        rspStr+='               Address: {}\n\n'.format(openS['ca'])

    rspStr += '\n Running Processes:\n'
    for k,v in cr.procPidDict.items():
        if v is not None:
            rspStr += '   {}\n'.format(k)
    return [rspStr]
#############################################################################

def readFileWrk(parmLst, inFile):
    usage = ' Usage rlf [ numLines [start ["matchStr"]] ].'

    # Get total Lines in file.
    try:
        with open( inFile, 'r',encoding='utf-8') as f:
            numLinesInFile = sum(1 for line in f)
    except FileNotFoundError:
        return ' Could not open file {} for reading'.format(inFile)

    # Get/Calc number of lines to return (parmLst[0]).
    try:
        numLinesToRtnA = int(parmLst[0])
    except ValueError:
        return ' Invalid number of lines to read.\n' + usage

    numLinesToRtn = min( numLinesToRtnA, numLinesInFile )
    numLinesToRtn = max( numLinesToRtn,  1 ) # Don't allow reading 0 lines.

    # Get/Calc startIdx (parmLst[1]).
    if len(parmLst) > 1:
        try:
            startIdx = max(int(parmLst[1]),0)
        except ValueError:
            return ' Invalid startIdx.\n' + usage

        if startIdx > numLinesInFile:
            startIdx = max(numLinesInFile - numLinesToRtn, 0)
    else:
        startIdx = max(numLinesInFile - numLinesToRtn, 0)

    # Calc endIdx.
    endIdx = max(startIdx + numLinesToRtn - 1, 0)
    endIdx = min(endIdx, numLinesInFile-1)

    # Build matchStr.
    matchStr = ''
    if len(parmLst) > 2 and parmLst[2].startswith('\"'):
        for el in parmLst[2:]:
            matchStr += (' ' + el) # Adds a starting space, remove below.
            if el.endswith('\"'):
                break
        matchStr = matchStr[1:].replace('\"', '') # [:1] Removes.

    rspStr  = ' numLinesInFile = {:4}.\n'.format( numLinesInFile )
    rspStr += '  numLinesToRtn = {:4}.\n'.format( numLinesToRtn  )
    rspStr += '       startIdx = {:4}.\n'.format( startIdx       )
    rspStr += '         endIdx = {:4}.\n'.format( endIdx         )
    rspStr += '       matchStr = {}.\n\n'.format( matchStr       )

    with open( inFile, 'r',encoding='utf-8') as f:
        for idx,line in enumerate(f):
            if startIdx <= idx <= endIdx:
                if matchStr != '' and matchStr in line:
                    rspStr += ' {:4} - {}'.format(idx,line)
                elif matchStr == '':
                    rspStr += ' {:4} - {}'.format(idx,line)

    return rspStr
#############################################################################

def clearFileWrk(inFile):
    now = dt.datetime.now()
    cDT    = '{}'.format(now.isoformat( timespec = 'seconds' ))
    with open(inFile, 'w',encoding='utf-8') as f:
        f.write( 'File cleared on {} \n'.format(cDT))
    return ' {} file cleared.'.format(inFile)
#############################################################################

def readFile(parmLst):
    fName = parmLst[0]
    linesToRead = parmLst[1]
    sys.stdout.flush()
    rspStr = readFileWrk(linesToRead, fName)
    return [rspStr]
#############################################################################

def clearFile(parmLst):
    fName = parmLst[0]
    sys.stdout.flush()
    rspStr = clearFileWrk(fName)
    return [rspStr]
#############################################################################

def writeFile(fName, inStr):
    with open(fName, 'a', encoding='utf-8') as f:
        f.write( inStr )
        f.flush()
##########################################t###################################

def displayPics(prmLst):
    startTimeLst,qs,styleDic,styleLk = prmLst[0], prmLst[1], prmLst[2], prmLst[3]
    rspStr = getActThrds()
    stoppedClock = False
    if 'clockCntrProc' in rspStr[0] or 'lcdUpdateProc' in rspStr[0]:
        #print('stopping clock')
        cr.stopClk(qs)
        stoppedClock = True

    ##################################
    rspStr = getActThrds()
    if 'MainThread' not in rspStr[0]:
        #print('reseting LCD')

        dspIdLst = [ 'hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD' ]
        sr.hwReset()              # HW Reset
        for displayID in dspIdLst:
            sr.swReset(displayID) # SW Reset and the display initialization.

    sr.setBkLight([1])            # Turn on backlight.

    picLst   = [ 'pics/240x320a.jpg', 'pics/240x320b.jpg', 'pics/240x320c.jpg',
                 'pics/240x320d.jpg', 'pics/240x320e.jpg', 'pics/240x320f.jpg' ]

    dspIdLst = [ 'hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD' ]

    for displayID, pic in zip( dspIdLst, picLst ):
        data = ms.makePilJpgPicImage(pic)
        sr.setEntireDisplay( displayID, data, sr.sendDat2ToSt7789 )
    time.sleep(3)
    ##################################

    if stoppedClock:
        #print('starting clock')
        cr.startClk([startTimeLst,qs,styleDic,styleLk])

    return ['done']
#############################################################################

