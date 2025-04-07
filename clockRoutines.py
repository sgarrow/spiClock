import time
import datetime        as dt
import multiprocessing as mp
import cfgDict         as cd
import spiRoutines     as sr
#############################################################################
#############################################################################
def getStartTime( startTime ):
    if len(startTime) == 3:
        hours   = int(startTime[0])
        minutes = int(startTime[1])
        seconds = int(startTime[2])
        while True:
            time.sleep(.2)
            now    = dt.datetime.now()
            hour   = now.hour
            minute = now.minute
            second = now.second
            if (hours == hour and minute == minutes and second == seconds):
                break
    else:
        now    = dt.datetime.now()
        hour   = now.hour
        minute = now.minute
        second = now.second
        hours, minutes, seconds = hour, minute, second

    hrMSD = hours   // 10
    hrLSD = hours    % 10
    mnMSD = minutes // 10
    mnLSD = minutes  % 10
    scMSD = seconds // 10
    scLSD = seconds  % 10

    timeDict = { 'hrMSD' : { 'value' : hrMSD, 'updated' : True },
                 'hrLSD' : { 'value' : hrLSD, 'updated' : True },
                 'mnMSD' : { 'value' : mnMSD, 'updated' : True },
                 'mnLSD' : { 'value' : mnLSD, 'updated' : True },
                 'scMSD' : { 'value' : scMSD, 'updated' : True },
                 'scLSD' : { 'value' : scLSD, 'updated' : True }}

    return timeDict
#############################################################################
#############################################################################
def updateCntr(timeDict):

    prevDict = timeDict.copy()

    hours   = timeDict['hrMSD']['value'] * 10 + timeDict['hrLSD']['value']
    minutes = timeDict['mnMSD']['value'] * 10 + timeDict['mnLSD']['value']
    seconds = timeDict['scMSD']['value'] * 10 + timeDict['scLSD']['value']

    seconds += 1
    if seconds  == 60:
        seconds  = 0
        minutes += 1
    if minutes  == 60:
        minutes  = 0
        hours   += 1
    if hours    == 24:
        hours    = 0

    hrMSD = hours   // 10
    hrLSD = hours    % 10
    mnMSD = minutes // 10
    mnLSD = minutes  % 10
    scMSD = seconds // 10
    scLSD = seconds  % 10

    timeDict = {
    'hrMSD':{'value': hrMSD, 'updated': prevDict['hrMSD']['value'] != hrMSD},
    'hrLSD':{'value': hrLSD, 'updated': prevDict['hrLSD']['value'] != hrLSD},
    'mnMSD':{'value': mnMSD, 'updated': prevDict['mnMSD']['value'] != mnMSD},
    'mnLSD':{'value': mnLSD, 'updated': prevDict['mnLSD']['value'] != mnLSD},
    'scMSD':{'value': scMSD, 'updated': prevDict['scMSD']['value'] != scMSD},
    'scLSD':{'value': scLSD, 'updated': prevDict['scLSD']['value'] != scLSD}}

    return timeDict
#############################################################################
#############################################################################

def lcdUpdateProc( procName, qLst, digitDict ):
    print(' {} {}'.format(procName, 'starting'))

    lcdCq = qLst[0]
    lcdRq = qLst[1]
    #clkCq = qLst[2]
    #clkRq = qLst[3]

    # timeDict, which is placed in my cmdQ, has the same key names as the
    # displayIdDict. The displayIdDict is used by the functions in the
    # spiRoutines.py module to determine the CS pin to use.
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']

    while True:

        data = lcdCq.get()   # Block here. Get digit/stop from clk/user.
        kStart = time.perf_counter()

        if data == 'stop':
            break
        timeDict = data

        hours   = timeDict['hrMSD']['value'] * 10 + timeDict['hrLSD']['value']
        minutes = timeDict['mnMSD']['value'] * 10 + timeDict['mnLSD']['value']
        seconds = timeDict['scMSD']['value'] * 10 + timeDict['scLSD']['value']
        hmsStr  = '{:02}{:02}{:02}'.format(hours,minutes,seconds)

        displaysUpdatedStr = ' updated:'
        hmsChangeStr = ''
        for theKey in kLst:
            if timeDict[theKey]['updated']:

                #digit   = str(timeDict[theKey]['value'])
                #spiData = digitDict[digit]
                #sr.setEntireDisplay(theKey, spiData, sr.sendDat2ToSt7789)

                sr.setEntireDisplay(theKey,
                                    digitDict[str(timeDict[theKey]['value'])],
                                    sr.sendDat2ToSt7789)

                displaysUpdatedStr += ' {}'.format(theKey)
                hmsChangeStr += '1'
            else:
                hmsChangeStr += '0'

        # Put rsp back to clk.
        lcdRq.put( ' LCD update time {:.6f} sec. {} {} {}.'.\
                format(time.perf_counter()-kStart, hmsStr, hmsChangeStr, displaysUpdatedStr))

    lcdRq.put(' {} {}'.format(procName, 'exiting'))  # Put rsp back to user.
#############################################################################

def clockCntrProc( procName, qLst, startTime ):
    debug = True
    if debug: print(' {} {}'.format(procName, 'starting'))

    lcdCq, lcdRq, clkCq, clkRq = qLst[0], qLst[1], qLst[2], qLst[3]
    calTime          =  1
    dsrNumDataPoints = 20
    actNumDataPoints =  0
    cumSumLoopTime   =  0

    timeDict = getStartTime(startTime)
    lcdCq.put(timeDict)               # Send cmd to lcdUpdateProc.

    while True:
        kStart = time.perf_counter()
        time.sleep( calTime )

        timeDict = updateCntr(timeDict)

        #print(timeDict['scLSD']['value'])
        lcdCq.put(timeDict)           # Send cmd to lcdUpdateProc.

        doBreak = False
        while not clkCq.empty():      # Get any stop cmd from user.
            cmd = clkCq.get_nowait()
            if cmd == 'stop':
                doBreak = True
                break
        if doBreak:
            break

        while not lcdRq.empty():      # Get rsp from LCD.
            rsp = lcdRq.get_nowait()
            if debug: print(rsp,flush = True)      # execution time.

        actNumDataPoints += 1
        actTime = time.perf_counter()-kStart
        if actNumDataPoints <= dsrNumDataPoints:
            cumSumLoopTime  += actTime

        else:
            calTime -= (cumSumLoopTime-(dsrNumDataPoints*1.0))/dsrNumDataPoints
            actNumDataPoints = 1
            cumSumLoopTime   = actTime

        #if seconds == 0:
        #    now      = dt.datetime.now()
        #    currTime = now.strftime('%H:%M:%S')
        #    print(' {:02}:{:02}:{:02} =? {}'.\
        #        format( hours, minutes, seconds, currTime ))
        #    print( ' time (req,act) = ({:.6f}, {:.6f}) sec. Num points = {}.'.\
        #            format(calTime,actTime,actNumDataPoints))

    clkRq.put(' {} {}'.format(procName, 'exiting'))  # Put rsp back to user.
##############################################################################

procPidDict = {'clockCntrProc': None, 'lcdUpdateProc': None}

def startLcdUpdateProc( qLst, digitDict ):
    procLst = []

    for _ in range(1):
        # Cannot access return value from proc directly.
        lcdProc = mp.Process(
               target = lcdUpdateProc,
               args   = ( 'lcdUpdateProc',  # Process Name.
                          qLst,             # [lcdCq,lcdRq,clkCq,clkRq]
                          digitDict ))      # Dict of LCD Display Data.

        lcdProc.daemon = True
        lcdProc.start()
        procPidDict['lcdUpdateProc'] = lcdProc.pid
        procLst.append(lcdProc)
#############################################################################

def startClockCntrProc( qLst, startTime ):
    procLst = []
    for _ in range(1):
        # Cannot access return value from proc directly.
        clkProc = mp.Process(
               target = clockCntrProc,
               args   = ( 'clockCntrProc',  # Process Name.
                          qLst,             # [lcdCq,lcdRq,clkCq,clkRq]
                          startTime ))      # start time.
        clkProc.daemon = True
        clkProc.start()
        procPidDict['clockCntrProc'] = clkProc.pid
        procLst.append(clkProc)
#############################################################################

def startClk(prmLst):
    startTime = prmLst[0]
    qLst      = prmLst[1]
    rspStr    = ''

    try:
        cfgDict   = cd.loadCfgDict()
        digitDict = cfgDict['digitScreenDict']['blackOnWhite']
    except KeyError as e:
        rspStr += ' startClock KeyError:', str(e)
        return [rspStr]

    if procPidDict['lcdUpdateProc'] is None:
        kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
        sr.hwReset()             # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey)   # SW Reset and the display initialization.
        sr.setBackLight([1])     # Turn on backlight.
        startLcdUpdateProc( qLst, digitDict )
        rspStr += ' lcdUpdateProc started.'
    else:
        rspStr += ' lcdUpdateProc already started.'

    if procPidDict['clockCntrProc'] is None:
        startClockCntrProc( qLst, startTime )
        rspStr += ' clockCntrProc started.'
    else:
        rspStr += ' clockCntrProc already started.'
    return [rspStr]
#############################################################################

def stopClk(prmLst):
    qLst   = prmLst
    lcdCq  = qLst[0]
    lcdRq  = qLst[1]
    clkCq  = qLst[2]
    clkRq  = qLst[3]
    rspStr = ''

    if procPidDict['clockCntrProc'] is not None:
        clkCq.put('stop')
        clkRsp = clkRq.get()
        print(' stopClk: clkRq.get = {}'.format(clkRsp))
        procPidDict['clockCntrProc'] = None
        rspStr += ' clockCntrProc stopped.'
    else:
        rspStr += ' clockCntrProc not running.'


    # There may be a stale response in the lcdRq that was meant for
    # clockCntrProc which was killed above.
    if procPidDict['lcdUpdateProc'] is not None:
        lcdCq.put('stop')
        matchStr = 'exiting'
        while True:
            try:
                time.sleep(.1)
                lcdRsp = lcdRq.get_nowait()
                print(' stopClk: lcdRq.get = {}'.format(lcdRsp))
                if matchStr in lcdRsp:
                    break
            except mp.queues.Empty:
                pass
        procPidDict['lcdUpdateProc'] = None
        kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
        sr.hwReset()             # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey)   # SW Reset and the display initialization.
        sr.setBackLight([0])     # Turn off backlight.
        rspStr += ' lcdUpdateProc stopped.'
    else:
        rspStr += ' lcdUpdateProc not running.'

    return [rspStr]
#############################################################################

def getTimeDate( prnEn = True ):
    now = dt.datetime.now()

    dowStrLst = ['Monday', 'Tuesday', 'Wednesday',
                 'Thursday', 'Friday', 'Saturday', 'Sunday']

    year   = now.year
    month  = now.month
    day    = now.day
    hour   = now.hour
    minute = now.minute
    second = now.second
    dowNum = now.weekday() # Monday is 0.
    dowStr = dowStrLst[dowNum]

    rspStr  = ' {}\n'.format(now)
    rspStr += ' year   {:4}'.format(   year   )
    rspStr += ' month  {:4}'.format(   month  )
    rspStr += ' day    {:4}\n'.format( day    )
    rspStr += ' hour   {:4}'.format(   hour   )
    rspStr += ' minute {:4}'.format(   minute )
    rspStr += ' second {:4}\n'.format( second )
    rspStr += ' dow    {:4} ({})'.format( dowNum, dowStr )

    if prnEn:
        pass
        #print(rspStr)

    rtnDict = {'year':   year,   'month':  month,  'day':   day,
               'hour':   hour,   'minute': minute, 'second':second,
               'dowNum': dowNum, 'dowStr': dowStr,
               'now':    now}

    return [rspStr, rtnDict]
#############################################################################

if __name__ == '__main__':

    lcdCqMain = mp.Queue()    # LCD Cmd Q. mp queue must be used here.
    lcdRqMain = mp.Queue()    # LCD Rsp Q. mp queue must be used here.
    clkCqMain = mp.Queue()    # CLK Cmd Q. mp queue must be used here.
    clkRqMain = mp.Queue()    # CLK Rsp Q. mp queue must be used here.

    keyLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    displayID = keyLst[-1] # pylint: disable=C0103

    resp = startClk(
                    [
                      [ ],
                      [ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ]
                    ]
                  )
    print(resp)

    if 'make screens' not in resp[0]:
        for _ in range(10):
            time.sleep(1.2)
        stopClk([ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ] )
        time.sleep(2)
        sr.hwReset()             # HW Reset
        sr.swReset(displayID)    # SW Reset and the display initialization.
        sr.setBackLight([0])     # Turn off backlight.
