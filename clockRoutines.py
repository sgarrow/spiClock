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
            print(now)
            hour   = now.hour
            minute = now.minute
            second = now.second
            if (hours == hour and minute == minutes and second == seconds):
                break
    else:
        now = dt.datetime.now()
        print(now)
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

    print(' {} {}'.format(procName, 'starting'))

    lcdCq = qLst[0]
    lcdRq = qLst[1]
    clkCq = qLst[2]
    clkRq = qLst[3]

    sr.setBackLight([1])     # Turn on backlight.
    sr.hwReset()             # HW Reset
    sr.swReset()             # SW Reset and the display initialization.

    while True:

        digit = lcdCq.get() # Block here. Get digit/stop from clk/user.

        if digit == 'stop':
            print(' lcdUpdateProc: lcdCq.get = {}'.format(digit))
            break

        kStart = time.perf_counter()
        data   = digitDict[digit]
        sr.setEntireDisplay(data, sr.sendDat2ToSt7789)

        lcdRq.put( ' lcdUpdateProc: lcdRq.put updateAnLCD time {:.6f} sec.'.\
                format(time.perf_counter()-kStart)) # Put rsp back to clk.

    sr.setBackLight([0])     # Turn off backlight.
    sr.hwReset()             # HW Reset
    sr.swReset()             # SW Reset and the display initialization.

    lcdRq.put(' lcdUpdateProc: lcdRq.put exiting.')  # Put rsp back to user.
#############################################################################

def clockCntrProc( procName, qLst, startTime ):
    print(' {} {}'.format(procName, 'starting'))

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
        except mp.queues.Empty:
            pass
        else:
            print(' clockCntrProc: lcdRq.get_nowait = {}'.format(rsp))

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
            print(' clockCntrProc: clkCq.get_nowait = {}'.format(cmd))
            if cmd == 'stop':
                break
        except mp.queues.Empty:
            pass

    clkRq.put(' clockCntrProc: clkRq.put exiting')
##############################################################################

def startLcdUpdateProc( qLst, digitDict ):
    procLst = []
    for _ in range(1):
        # Cannot access return value from proc directly.
        proc = mp.Process(
               target = lcdUpdateProc,
               args   = ( 'lcdUpdateProc',  # Process Name.
                          qLst,             # [lcdCq,lcdRq,clkCq,clkRq]
                          digitDict ))      # Dict of LCD Display Data.

        proc.daemon = True
        proc.start()
        procLst.append(proc)
    #for p in procLst:
    #    p.join()
#############################################################################

def startClockCntrProc( qLst, startTime ):
    #print(f"Process is alive after join(2): {process.is_alive()}")
    procLst = []
    for _ in range(1):
        # Cannot access return value from proc directly.
        proc = mp.Process(
               target = clockCntrProc,
               args   = ( 'clockCntrProc',  # Process Name.
                          qLst,             # [lcdCq,lcdRq,clkCq,clkRq]
                          startTime ))      # start time.
        proc.daemon = True
        proc.start()
        procLst.append(proc)
    #for p in procLst:
    #    p.join()
#############################################################################

def startClk(prmLst):
    startTime = prmLst[0]
    qLst      = prmLst[1]

    try:
        cfgDict   = cd.loadCfgDict()
        digitDict = cfgDict['digitScreenDict']['blackOnWhite']
    except KeyError as e:
        print(' startClock KeyError:', str(e))
        return ['make screens.']

    startLcdUpdateProc( qLst, digitDict )
    time.sleep(1)
    startClockCntrProc( qLst, startTime )
    return ['clock started.']
#############################################################################

def stopClk(prmLst):
    qLst  = prmLst
    lcdCq = qLst[0]
    lcdRq = qLst[1]
    clkCq = qLst[2]
    clkRq = qLst[3]

    clkCq.put('stop')
    clkRsp = clkRq.get()
    print(' stopClk: clkRq.get = {}'.format(clkRsp))


    # There may be a stale response in the lcdRq that was meant for 
    # clockCntrProc which was killed above.
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

    return ['clock stopped.']
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
            sleep(3)
            sr.setBackLight([0])     # Turn off backlight.
            sr.hwReset()             # HW Reset
            sr.swReset()             # SW Reset and the display initialization.
            break
