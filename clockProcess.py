import time
import datetime as dt
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

if __name__ == '__main__':
    pass
