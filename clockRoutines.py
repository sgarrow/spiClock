import time
import datetime        as dt
import multiprocessing as mp
import cfgDict         as cd
import spiRoutines     as sr
import makeScreen      as ms
#############################################################################
#############################################################################
def getStartTime( startTime ):
    if len(startTime) == 3:
        hours   = int(startTime[0])
        minutes = int(startTime[1])
        seconds = int(startTime[2])
        while True:
            time.sleep(.2)
            now = dt.datetime.now()
            hour   = now.hour
            minute = now.minute
            second = now.second
            if (hours == hour and minute == minutes and second == seconds):
                break
    else:
        now = dt.datetime.now()
        hour   = now.hour
        minute = now.minute
        second = now.second
        hours, minutes, seconds = hour, minute, second

    return hours, minutes, seconds
#############################################################################
#############################################################################
def updateCntr(hours, minutes, seconds):
    seconds += 1
    if seconds  == 60:
        seconds  = 0
        minutes += 1
    if minutes  == 60:
        minutes  = 0
        hours   += 1
    if hours    == 24:
        hours    = 0
    return hours, minutes, seconds
#############################################################################
#############################################################################

def lcdUpdateProc( procName, qLst, digitDict ):

    print(' {} {}'.format(procName, 'starting')) # <-- Debug.

    lcdCq = qLst[0]
    lcdRq = qLst[1]
    #clkCq = qLst[2]
    #clkRq = qLst[3]

    sr.setBackLight([1])     # Turn on backlight.
    sr.hwReset()             # HW Reset
    sr.swReset()             # SW Reset and the display initialization.

    while True:

        digit = lcdCq.get() # Block here. Get digit/stop from clk/user.

        if digit == 'stop':
            break

        kStart = time.perf_counter()
        data   = digitDict[digit]
        sr.setEntireDisplay(data, sr.sendDat2ToSt7789)

        lcdRq.put( ' LCD update time {:.6f} sec.'.\
                format(time.perf_counter()-kStart)) # Put rsp back to clk.

    sr.setBackLight([0])     # Turn off backlight.
    sr.hwReset()             # HW Reset
    sr.swReset()             # SW Reset and the display initialization.

    lcdRq.put(' {} {}'.format(procName, 'exiting'))  # Put rsp back to user.
#############################################################################

def clockCntrProc( procName, qLst, startTime ):
    print(' {} {}'.format(procName, 'starting')) # <-- Debug.

    lcdCq, lcdRq, clkCq, clkRq = qLst[0], qLst[1], qLst[2], qLst[3]
    hours, minutes, seconds    = getStartTime(startTime)

    calTime          =  1
    dsrNumDataPoints = 20
    actNumDataPoints =  0
    cumSumLoopTime   =  0

    while True:
        kStart = time.perf_counter()
        time.sleep( calTime )

        hours, minutes, seconds = updateCntr(hours, minutes, seconds)

        secLSD = str(seconds % 10)
        lcdCq.put(secLSD)             # Send cmd to LCD.
        try:
            rsp = lcdRq.get_nowait()  # Get rsp from LCD.
            print(rsp)                # <-- Debug. Comment out in production.
        except mp.queues.Empty:
            pass

        actNumDataPoints += 1
        actTime = time.perf_counter()-kStart
        if actNumDataPoints <= dsrNumDataPoints:
            cumSumLoopTime  += actTime

        else:
            calTime -= (cumSumLoopTime-(dsrNumDataPoints*1.0))/dsrNumDataPoints
            actNumDataPoints = 1
            cumSumLoopTime   = actTime

        if seconds == 0:
            now      = dt.datetime.now()
            currTime = now.strftime('%H:%M:%S')
            print(' {:02}:{:02}:{:02} =? {}'.\
                format( hours, minutes, seconds, currTime ))
            print( ' time (req,act) = ({:.6f}, {:.6f}) sec. Num points = {}.'.\
                    format(calTime,actTime,actNumDataPoints))

        try:
            cmd = clkCq.get_nowait()  # Get any stop cmd from user.
            if cmd == 'stop':
                break
        except mp.queues.Empty:
            pass

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

    resp = startClk(
                    [
                      [ ],
                      [ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ]
                    ]
                  )
    print(resp)

    while 'make screens' not in resp[0]:
        try:
            #print('main looping')
            time.sleep(1)
        except KeyboardInterrupt as e:
            print(' clockRoutines main KeyboardInterrupt:', str(e))
            stopClk([ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ] )
            time.sleep(2)
            sr.setBackLight([0])     # Turn off backlight.
            sr.hwReset()             # HW Reset
            sr.swReset()             # SW Reset and the display initialization.
            break
