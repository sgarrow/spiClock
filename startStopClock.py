import time
import multiprocessing as mp
import clockProcess    as cp
import spiRoutines     as sr
import lcdProcess      as lp

procPidDict = {'clockCntrProc': None, 'lcdUpdateProc': None}
#####################################################################
######################################################################

def isClockRunning():
    return procPidDict['clockCntrProc'] is not None and \
           procPidDict['lcdUpdateProc'] is not None
######################################################################

def startLcdUpdateProc( qLst, styleDict, styleDictLock ):
    # Cannot access return value from proc directly.
    lcdProc = mp.Process(
           target = lp.lcdUpdateProc,
           args   = ( 'lcdUpdateProc', # Process Name.
                      qLst,          # [lcdCq,lcdRq,clkCq,clkRq]
                      styleDict,
                      styleDictLock))
    lcdProc.daemon = True
    lcdProc.start()
    return lcdProc.pid
######################################################################

def startClockCntrProc( qLst, startTime, styleDict, styleDictLock):
    # Cannot access return value from proc directly.
    clkProc = mp.Process(
           target = cp.clockCntrProc,
           args   = ( 'clockCntrProc', # Process Name.
                      qLst,            # [lcdCq,lcdRq,clkCq,clkRq]
                      startTime,       # start time.
                      styleDict,
                      styleDictLock))
    clkProc.daemon = True
    clkProc.start()
    return clkProc.pid
######################################################################

def startClk(prmLst):
    startTime = prmLst[0]
    qLst      = prmLst[1] # [ lcdCq, lcdRq, clkCq, clkRq ]
    styleDict, styleDictLock = prmLst[2], prmLst[3]
    rspStr    = ''

    lcdRq = prmLst[1][1]

    # Ensure all the queues are empty before starting any processes
    # that put() and/or get() from them.
    for q in qLst:
        try:
            while True:
                q.get_nowait()
        except mp.queues.Empty:
            pass
    ########################

    if procPidDict['lcdUpdateProc'] is None:
        kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
        sr.hwReset()           # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey) # SW Reset & display initialization.
        sr.setBkLight([1])     # Turn on backlight.
        pid = startLcdUpdateProc( qLst, styleDict, styleDictLock )
        rspStr = lcdRq.get() + '\n'
        if 'ERROR' not in rspStr:
            procPidDict['lcdUpdateProc'] = pid
    else:
        rspStr += ' lcdUpdateProc already started.'
    ########################

    if procPidDict['clockCntrProc'] is None:
        if procPidDict['lcdUpdateProc'] is not None:
            pid = startClockCntrProc( qLst, startTime, styleDict, styleDictLock )
            rspStr += ' clockCntrProc started.'
            procPidDict['clockCntrProc'] = pid
        else:
            rspStr += ' ERROR: clockCntrProc not started\n'
            rspStr += ' ERROR: because lcdUpdateProc is not running.'
    else:
        rspStr += ' clockCntrProc already started.'

    ########################
    return [rspStr]
######################################################################

def stopClk(prmLst):
    qLst   = prmLst
    lcdCq  = qLst[0]
    lcdRq  = qLst[1]
    clkCq  = qLst[2]
    clkRq  = qLst[3]
    rspStr = ''

    if procPidDict['clockCntrProc'] is not None:
        clkCq.put('stop')                   # Queue Put.
        clkRsp = clkRq.get()                # Queue Get Block.
        print(' stopClk: clkRq.get = {}'.format(clkRsp))
        procPidDict['clockCntrProc'] = None
        rspStr += ' clockCntrProc stopped.'
    else:
        rspStr += ' clockCntrProc not running.'

    # There may be a stale response in the lcdRq that was
    # meant for clockCntrProc which was killed above.
    if procPidDict['lcdUpdateProc'] is not None:
        lcdCq.put('stop')                   # Queue Put.
        matchStr = 'exiting'
        while True:
            try:
                time.sleep(.1)
                lcdRsp = lcdRq.get_nowait() # Queue Get - No Wait.
                print(' stopClk: lcdRq.get = {}'.format(lcdRsp))
                if matchStr in lcdRsp:
                    break
            except mp.queues.Empty:
                pass
        procPidDict['lcdUpdateProc'] = None
        kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
        sr.hwReset()           # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey) # SW Reset & display initialization.
        sr.setBkLight([0])     # Turn off backlight.
        rspStr += ' lcdUpdateProc stopped.'
    else:
        rspStr += ' lcdUpdateProc not running.'

    return [rspStr]
######################################################################

def ctrlBright(prmLst):

    rspStr = ''
    try:
        dsrdBrightness = int(prmLst[0])
    except ValueError:
        rspStr += ' ERROR: Non-integer input ({})'.format(prmLst[0])

    if rspStr == '' and not 0 <= dsrdBrightness <=255:
        rspStr += ' ERROR: Input not in range 0-255 ({})'.format(prmLst[0])

    if rspStr == '':
        rspStr = sr.writeDisplayBrightness(dsrdBrightness)[0]

    return [rspStr]
######################################################################

if __name__ == '__main__':
    lcdCqMain = mp.Queue() # LCD Cmd Q. mp queue must be used here.
    lcdRqMain = mp.Queue() # LCD Rsp Q. mp queue must be used here.
    clkCqMain = mp.Queue() # CLK Cmd Q. mp queue must be used here.
    clkRqMain = mp.Queue() # CLK Rsp Q. mp queue must be used here.

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
        sr.hwReset()           # HW Reset
        sr.swReset(displayID)  # SW Reset & display initialization.
        sr.setBkLight([0])     # Turn off backlight.
