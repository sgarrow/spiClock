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

def startLcdUpdateProc( qLst ):
    procLst = []

    for _ in range(1):
        # Cannot access return value from proc directly.
        lcdProc = mp.Process(
               target = lp.lcdUpdateProc,
               args   = ( 'lcdUpdateProc', # Process Name.
                          qLst ))          # [lcdCq,lcdRq,clkCq,clkRq]

        lcdProc.daemon = True
        lcdProc.start()
        procPidDict['lcdUpdateProc'] = lcdProc.pid
        procLst.append(lcdProc)
######################################################################

def startClockCntrProc( qLst, startTime ):
    procLst = []
    for _ in range(1):
        # Cannot access return value from proc directly.
        clkProc = mp.Process(
               target = cp.clockCntrProc,
               args   = ( 'clockCntrProc', # Process Name.
                          qLst,            # [lcdCq,lcdRq,clkCq,clkRq]
                          startTime ))     # start time.
        clkProc.daemon = True
        clkProc.start()
        procPidDict['clockCntrProc'] = clkProc.pid
        procLst.append(clkProc)
######################################################################

def startClk(prmLst):
    startTime = prmLst[0]
    qLst      = prmLst[1]
    rspStr    = ''

    if procPidDict['lcdUpdateProc'] is None:
        kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
        sr.hwReset()           # HW Reset. Common pin to all dislays.
        for theKey in kLst:
            sr.swReset(theKey) # SW Reset & display initialization.
        sr.setBkLight([1])     # Turn on backlight.
        startLcdUpdateProc( qLst )
        rspStr += ' lcdUpdateProc started.'
    else:
        rspStr += ' lcdUpdateProc already started.'

    if procPidDict['clockCntrProc'] is None:
        startClockCntrProc( qLst, startTime )
        rspStr += ' clockCntrProc started.'
    else:
        rspStr += ' clockCntrProc already started.'
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

def controlBrightness(prmLst):

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
