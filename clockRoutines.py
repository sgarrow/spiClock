import time
import datetime        as dt
import multiprocessing as mp
import cfgDict         as cd
import spiRoutines     as sr
import clockProcess    as cp
import lcdProcess      as lp
#############################################################################
#############################################################################

procPidDict = {'clockCntrProc': None, 'lcdUpdateProc': None}

def startLcdUpdateProc( qLst, digitDict ):
    procLst = []

    for _ in range(1):
        # Cannot access return value from proc directly.
        lcdProc = mp.Process(
               target = lp.lcdUpdateProc,
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
               target = cp.clockCntrProc,
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

    rsp = cd.loadCfgDict()
    #rspStr += rsp[0]
    cfgDict = rsp[1]
    try:
        digitDict = cfgDict['digitScreenDict']['blackOnWhite']
    except KeyError as e:
        rspStr += ' startClock KeyError: {}'.format(str(e))
        return [rspStr]

    if procPidDict['lcdUpdateProc'] is None:
        kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
        sr.hwReset()           # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey) # SW Reset and the display initialization.
        sr.setBkLight([1])     # Turn on backlight.
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
        sr.hwReset()           # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey) # SW Reset and the display initialization.
        sr.setBkLight([0])     # Turn off backlight.
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
    pass
    #lcdCqMain = mp.Queue()    # LCD Cmd Q. mp queue must be used here.
    #lcdRqMain = mp.Queue()    # LCD Rsp Q. mp queue must be used here.
    #clkCqMain = mp.Queue()    # CLK Cmd Q. mp queue must be used here.
    #clkRqMain = mp.Queue()    # CLK Rsp Q. mp queue must be used here.
    #
    #keyLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    #displayID = keyLst[-1] # pylint: disable=C0103
    #
    #resp = startClk(
    #                [
    #                  [ ],
    #                  [ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ]
    #                ]
    #              )
    #print(resp)
    #
    #if 'make screens' not in resp[0]:
    #    for _ in range(10):
    #        time.sleep(1.2)
    #    stopClk([ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ] )
    #    time.sleep(2)
    #    sr.hwReset()           # HW Reset
    #    sr.swReset(displayID)  # SW Reset and the display initialization.
    #    sr.setBkLight([0])     # Turn off backlight.
