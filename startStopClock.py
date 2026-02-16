import time
import multiprocessing as mp
import lcdProcess      as lp
import spiRoutines     as sr
import clockProcess    as cp
from   utils import procPidDict
######################################################################
######################################################################

def startLcdUpdateProc( qLst, mpSharedDict, mpSharedDictLock ):
    # Cannot access return value from proc directly.
    lcdProc = mp.Process(
           target = lp.lcdUpdateProc,
           args   = ( 'lcdUpdateProc', # Process Name.
                      qLst,            # [lcdCq,lcdRq,clkCq,clkRq]
                      mpSharedDict,
                      mpSharedDictLock))
    lcdProc.daemon = True
    lcdProc.start()
    return lcdProc.pid
######################################################################

def startClockCntrProc( qLst, startTime, mpSharedDict, mpSharedDictLock):
    # Cannot access return value from proc directly.
    clkProc = mp.Process(
           target = cp.clockCntrProc,
           args   = ( 'clockCntrProc', # Process Name.
                      qLst,            # [lcdCq,lcdRq,clkCq,clkRq]
                      startTime,       # start time.
                      mpSharedDict,
                      mpSharedDictLock))
    clkProc.daemon = True
    clkProc.start()
    return clkProc.pid
######################################################################

def startClk(prmLst):
    ''' 
 Starts the clock using the active color scheme (style).

 There are 3 possible usages of this command:

   Usage type 1: sc
   Usage type 2: sc 12 13 14
   Usage type 3: sc 12 13 14 x

 1 - Starts the clock immediately using as an initial time a value
     obtained by a call to a native python function datetime.now.

 2 - Delays starting the clock until datetime.now() returns the
     time specified.  In the above example that time is 12 13 14
     but any time can be specified.  If an invalid start time is
     specified (e.g.,12 13 65 or 12 13 ab) then a start time of
     23 59 59 is used.

 In practice usage types 1 and 2 are basically the same.  The
 difference is in the potential accuracy of the start time.

 In type 1, if a call is made to datetime.now() just before the
 second changes then the clock will be off by essentially 1 sec.

 In type 2 a call is made to .now() every 0.2 seconds until a
 match is detected to the value it returns and the specified time.

 Thus, the max start time error between type 1 and 2 are 1 sec and
 0.2 sec, respectively.

 3 - Starts the clock immediately using as an initial time the
     eXact time specified (this need not have any relationship to
     the actual time). If an invalid start time is specified, then
     a start time of 23 59 59 is used.  This usage is provided to
     cover the case where the Raspberry Pi (RPi) is not connected
     to a wireless LAN (internet).  More on this below.

 The RPi does not have a Real Time Clock (RTC).

 At boot time, assuming no internet connection, the RPi starts its
 internal, SW based, time tracking function (that datetime.now()
 accesses) with a start time that is equal to the time it saved 
 on its last power off event.

 So, say the RPi is on, has a correct value for the time and isn't
 connected to the internet. Say it's 1 o'clock, after 1 hour of on
 time the RPi will correctly know it's 2 o'clock. Now say the RPi
 is turned off for 4 hours. When the RPi is turned back on it will
 think it's 2 o'clock when it's really it's 6 o'clock!

 If an internet connection IS available at boot time then the RPi
 starts its internal time tracking function with an initial value
 obtained from the internet.

 Note that this spiClock's SW only accesses the RPi's
 internal time tracking function (via the call to datetime.now)at
 clock start time (when the sc command is first entered).  After
 that this clock keeps track of the time all on its own using the
 python sleep(1 second) native internal function.

 Note that the sleep function dithers around the specified time
 (nominally 1 sec.) by +/- 1 milli-second. This may not sound like
 much but can cause an accumulating error of up to 1.5 minutes per
 day.  To compensate for this a high precision counter is used to
 measure the actual sleep time and the nominal sleep time is
 adjusted accordingly.  This adjustment is made every 20 seconds.

 When the clock is started two new processes (running on thier own
 core) are started.  So when the clock is running three separate
 cores are being used.  One core runs the server (Main Process),
 another runs the clock counter (Clock Process) and the third
 controls the displays (LCD Process).  These three processes
 communicate with each other using four of Python's awesome
 multiprocessing-communication-queues.  Two queues are used for
 sending commands and the two are used for receiving responses.
 =================================================================
 '''
    startTime = prmLst[0]
    qLst      = prmLst[1] # [ lcdCq, lcdRq, clkCq, clkRq ]
    mpSharedDict, mpSharedDictLock = prmLst[2], prmLst[3]
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
        sr.setBkLight([1])     # Turn on backlight.
        pid = startLcdUpdateProc( qLst, mpSharedDict, mpSharedDictLock )
        rspStr = lcdRq.get() + '\n'
        if 'ERROR' not in rspStr:
            procPidDict['lcdUpdateProc'] = pid
    else:
        rspStr += ' lcdUpdateProc already started.'
    ########################
    if procPidDict['clockCntrProc'] is None:
        if procPidDict['lcdUpdateProc'] is not None:
            pid = startClockCntrProc( qLst, startTime, mpSharedDict, mpSharedDictLock )
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
    '''
 Stops the clock.

 Usage: pc

 Stopping the clock is done by terminating the Clock Process and
 the LCD Process.  These processes will have been started by the
 sc command.
 =================================================================
'''
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
        sr.setBkLight([0])                  # Turn off backlight.
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
