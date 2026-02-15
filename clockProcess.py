import time
import datetime          as dt
import styleMgmtRoutines as sm
#############################################################################
#############################################################################

def getStartTime( parmLst ): # ['12', '34', '56', 'x']

    dfltHours, dfltMinutes, dfltSeconds = 23,59,58
    usingDefault = False

    containsX = any('x' in s for s in parmLst)
    logStr, sixNums = sm.checkTime( parmLst )

    if len(parmLst) == 0:          # Parms entered?
        now = dt.datetime.now()    # Parms not entered, use dt.datetime.
        hours, minutes, seconds = now.hour, now.minute, now.second
        #print(' time set to dt.datetime.now = {}.'.format(dt.datetime.now()))

    else:

        if 'ERROR' not in logStr:  # Parms entered, use them if they're ok.
            hours   = sixNums[0]*10 + sixNums[1]
            minutes = sixNums[2]*10 + sixNums[3]
            seconds = sixNums[4]*10 + sixNums[5]
            #print(' time set to parms = {:2}:{:2}:{:2}'.format(hours, minutes, seconds))
        else:                      # Parms not ok, use defaults.
            hours, minutes, seconds = dfltHours, dfltMinutes, dfltSeconds
            #print(' time set to default = 23:59:58')
            usingDefault = True

        if not containsX:          # Parm to use eXact entered?
            if not usingDefault:   # yes, sync to dt.datetime.
                #print(' syncing')
                while True:
                    time.sleep(.2)
                    now = dt.datetime.now()
                    if ( hours   == now.hour   and \
                         minutes == now.minute and \
                         seconds == now.second):
                        #print(' sync complete')
                        break
            else:
                pass               # No, don't sync. Use eXact time entered.
                #print(' cannot sync when using defaults')

    # Initialize/return timeDict for use in updating LCD (via Q in clockCntrProc)
    timeDict = { 'hrMSD' : { 'value' : hours   // 10 , 'updated' : True },
                 'hrLSD' : { 'value' : hours    % 10 , 'updated' : True },
                 'mnMSD' : { 'value' : minutes // 10 , 'updated' : True },
                 'mnLSD' : { 'value' : minutes  % 10 , 'updated' : True },
                 'scMSD' : { 'value' : seconds // 10 , 'updated' : True },
                 'scLSD' : { 'value' : seconds  % 10 , 'updated' : True }}

    return timeDict
#############################################################################

# Test data
# Started 11-Jun-25
# Stopped 05-Sep-25
# Num Days On 86
# Clock Slow by 12 Sec.
# Clock looses 1 second every 86/12 = 7.17 days.
# 7.17 days = 7.17 * 24 * 60 * 60 = 619,488 seconds.
# Clock looses 1 second every 619,488 seconds.
# Every 619,488 seconds schedule adding an extra second.

def updateCntr(timeDict,mpSharedDict,mpSharedDictLock):
    # Update timeDict which was previoulsy initialized via getStartTime.
    kStart = time.perf_counter()
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

    rspLst = sm.getDayTime([mpSharedDict,mpSharedDictLock])
    dTime = rspLst[1]
    rspLst = sm.getNightTime([mpSharedDict,mpSharedDictLock])
    nTime = rspLst[1]

    if   [ hrMSD, hrLSD, mnMSD, mnLSD, scMSD, scLSD ] == dTime:
        style = sm.getDayStyle([mpSharedDict,mpSharedDictLock])[0]
    elif [ hrMSD, hrLSD, mnMSD, mnLSD, scMSD, scLSD ] == nTime:
        style = sm.getNightStyle([mpSharedDict,mpSharedDictLock])[0]
    else:
        style = None

    # Update/return timeDict for use in updating LCD (via Q in clockCntrProc)
    timeDict = {
    'hrMSD':{'value': hrMSD, 'updated': prevDict['hrMSD']['value'] != hrMSD},
    'hrLSD':{'value': hrLSD, 'updated': prevDict['hrLSD']['value'] != hrLSD},
    'mnMSD':{'value': mnMSD, 'updated': prevDict['mnMSD']['value'] != mnMSD},
    'mnLSD':{'value': mnLSD, 'updated': prevDict['mnLSD']['value'] != mnLSD},
    'scMSD':{'value': scMSD, 'updated': prevDict['scMSD']['value'] != scMSD},
    'scLSD':{'value': scLSD, 'updated': prevDict['scLSD']['value'] != scLSD}}

    exeTime = time.perf_counter()-kStart # pylint: disable=W0612
    #print('Time spent updating counter = {:10.6f}'.format(exeTime))
    return timeDict,style
#############################################################################
#############################################################################

def clockCntrProc( procName, qLst, startTime, mpSharedDict, mpSharedDictLock ):

    lcdCq, lcdRq, clkCq, clkRq = qLst[0], qLst[1], qLst[2], qLst[3]
    calTime          =  1
    dsrNumDataPoints = 20
    actNumDataPoints =  0
    cumSumLoopTime   =  0
    #cumSumError      =  0

    timeDict = getStartTime(startTime)
    lcdCq.put(timeDict)               # Send cmd to lcdUpdateProc.

    while True:
        kStart = time.perf_counter()
        time.sleep( calTime )         # Nominally 1 sec.

        timeDict, style = updateCntr(timeDict,mpSharedDict,mpSharedDictLock)
        if style is not None:
            rspLst   = sm.getAllStyles()
            #fRspStr  = rspLst[0]
            mpSharedDict = rspLst[1]
            theKey   = [ k for k,v in mpSharedDict.items() if v == style ]
            rspLst   = sm.setActStyle([str(theKey[0]),mpSharedDict,mpSharedDictLock,lcdCq])

        lcdCq.put(timeDict)           # Send cmd to lcdUpdateProc.

        doBreak = False
        while not clkCq.empty():      # Get any stop cmd from user.
            cmd = clkCq.get_nowait()
            if cmd == 'stop':
                doBreak = True
                break
        if doBreak:
            break

        while not lcdRq.empty():      # Get all pending responses from LCD.
            lcdRq.get_nowait()
            #rsp = lcdRq.get_nowait()
            #print(rsp,flush=True) # Execution time.

        actNumDataPoints += 1
        actTime = time.perf_counter()-kStart
        if actNumDataPoints <= dsrNumDataPoints:
            cumSumLoopTime  += actTime

        else:
            calTime -= (cumSumLoopTime-(dsrNumDataPoints*1.0))/dsrNumDataPoints
            actNumDataPoints = 1
            cumSumLoopTime   = actTime

        #if actNumDataPoints == dsrNumDataPoints:
        #    hours   = timeDict['hrMSD']['value'] * 10 + timeDict['hrLSD']['value']
        #    minutes = timeDict['mnMSD']['value'] * 10 + timeDict['mnLSD']['value']
        #    seconds = timeDict['scMSD']['value'] * 10 + timeDict['scLSD']['value']
        #    now      = dt.datetime.now()
        #    currTime = now.strftime('%H:%M:%S')
        #    error = 1-actTime
        #    cumSumError += error
        #
        #    print(' {:02}:{:02}:{:02} =? {}'.\
        #            format( hours, minutes, seconds, currTime ))
        #
        #    print(' time (req,act) = ({:.6f}. {:.6f}) sec. Num points = {}.'.\
        #            format( calTime, actTime, actNumDataPoints ))
        #
        #    print(' Error = {:10.6f}. cumSumError = {:10.6f}.'.\
        #            format( error, cumSumError ))

    clkRq.put(' {} {}'.format(procName, 'exiting'))  # Put rsp back to user.
##############################################################################

if __name__ == '__main__':
    pass
