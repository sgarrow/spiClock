import time
import datetime          as dt
import styleMgmtRoutines as sm
############################################################################
#############################################################################

def getStartTime( startTime ):
    #print(startTime)
    if len(startTime) > 2:
        try:
            hours   = min(int(startTime[0]), 23)
            minutes = min(int(startTime[1]), 59)
            seconds = min(int(startTime[2]), 59)
        except ValueError:
            #print('starttime exception, set to 23 59 58.')
            hours   = 23
            minutes = 59
            seconds = 58
        else:
            #print('syncing provided time w/ dt.datetime.now.')
            if len(startTime) == 3:
                while True:
                    time.sleep(.2)
                    now    = dt.datetime.now()
                    hour   = now.hour
                    minute = now.minute
                    second = now.second
                    if (hours==hour and minute==minutes and second==seconds):
                        break
            else:
                #print('starttime set to provided time.')
                hour   = hours
                minute = minutes
                second = seconds

    else:
        #print('starttime is dt.datetime.now.')
        now    = dt.datetime.now()
        hour   = now.hour
        minute = now.minute
        second = now.second
        hours, minutes, seconds = hour, minute, second

    timeDict = { 'hrMSD' : { 'value' : hours   // 10 , 'updated' : True },
                 'hrLSD' : { 'value' : hours    % 10 , 'updated' : True },
                 'mnMSD' : { 'value' : minutes // 10 , 'updated' : True },
                 'mnLSD' : { 'value' : minutes  % 10 , 'updated' : True },
                 'scMSD' : { 'value' : seconds // 10 , 'updated' : True },
                 'scLSD' : { 'value' : seconds  % 10 , 'updated' : True }}

    return timeDict
#############################################################################

def updateCntr(timeDict,styleDic,styleLk):

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

    setDayStyleTime   = [ 0, 7, 0, 0, 0, 0 ] # 7:00 AM
    setNightStyleTime = [ 2, 1, 0, 0, 0, 0 ] # 9:00 PM
    if   [ hrMSD, hrLSD, mnMSD, mnLSD, scMSD, scLSD ] == setDayStyleTime:
        style = sm.getDayStyle([styleDic,styleLk])[0]
    elif [ hrMSD, hrLSD, mnMSD, mnLSD, scMSD, scLSD ] == setNightStyleTime:
        style = sm.getNightStyle([styleDic,styleLk])[0]
    else:
        style = None

    timeDict = {
    'hrMSD':{'value': hrMSD, 'updated': prevDict['hrMSD']['value'] != hrMSD},
    'hrLSD':{'value': hrLSD, 'updated': prevDict['hrLSD']['value'] != hrLSD},
    'mnMSD':{'value': mnMSD, 'updated': prevDict['mnMSD']['value'] != mnMSD},
    'mnLSD':{'value': mnLSD, 'updated': prevDict['mnLSD']['value'] != mnLSD},
    'scMSD':{'value': scMSD, 'updated': prevDict['scMSD']['value'] != scMSD},
    'scLSD':{'value': scLSD, 'updated': prevDict['scLSD']['value'] != scLSD}}

    return timeDict,style
#############################################################################
#############################################################################

def clockCntrProc( procName, qLst, startTime, styleDict, styleDictLock ):

    lcdCq, lcdRq, clkCq, clkRq = qLst[0], qLst[1], qLst[2], qLst[3]
    calTime          =  1
    dsrNumDataPoints = 20
    actNumDataPoints =  0
    cumSumLoopTime   =  0
    cumSumError      =  0

    timeDict = getStartTime(startTime)
    lcdCq.put(timeDict)               # Send cmd to lcdUpdateProc.

    while True:
        kStart = time.perf_counter()
        time.sleep( calTime )         # Nominally 1 sec.

        timeDict, style = updateCntr(timeDict,styleDict,styleDictLock)
        if style is not None:
            rspLst   = sm.getAllStyles()
            #fRspStr  = rspLst[0]
            styleDic = rspLst[1]
            theKey   = [ k for k,v in styleDic.items() if v == style ]
            rspLst   = sm.setActiveStyle([str(theKey[0]),styleDict,styleDictLock,lcdCq])

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
