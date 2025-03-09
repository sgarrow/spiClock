import time
import statistics
import pprint          as pp
import datetime        as dt
import multiprocessing as mp
import cfgDict         as cd
import spiRoutines     as sr
#############################################################################

def lcdUpdateProc( threadName, qLst, digitDict ):

    lcdCq = qLst[0]
    lcdRq = qLst[1]
    clkCq = qLst[2]
    clkRq = qLst[3]

    sr.setBackLight([1]) # Turn on backlight.
    sr.hwReset()         # HW Reset
    sr.swReset()         # SW Reset and the display initialization.

    while True:

        digit  = lcdCq.get() # Block here.
        kStart = time.perf_counter()
        data   = digitDict[digit]
        sr.setEntireDisplay(data, sr.sendDat2ToSt7789)

        lcdRq.put( ' updateAnLCD   loop time {:.6f} sec.'.\
                format(time.perf_counter()-kStart)
              )
#############################################################################

def clockCntrProc( threadName, qLst, clockDict, startTime ):

    lcdCq = qLst[0]
    lcdRq = qLst[1]
    clkCq = qLst[2]
    clkRq = qLst[3]

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
        hours, minutes, seconds = 0,0,0

    calTime = clockDict['calibrated1Sec'][clockDict['keyToRunWith']]
    print('ct = ',calTime)

    while True:

        kStart = time.perf_counter()
        try:
            #if seconds % 15 == 0:
            #    now = dt.datetime.now()
            #    currTime = now.strftime('%H:%M:%S')
            #    print('{:02}:{:02}:{:02} =? {}'.\
            #        format( hours, minutes, seconds, currTime ))
    
            time.sleep( calTime )
            seconds += 1
    
            if seconds  == 60:
                seconds  = 0
                minutes += 1
            if minutes  == 60:
                minutes  = 0
                hours   += 1
            if hours    == 24:
                hours    = 0
    
            secLSD = str(seconds % 10)
            lcdCq.put(secLSD)
    
            try:
                rsp = lcdRq.get_nowait()  # Non-blocking get
                print(rsp)
            except mp.queues.Empty:
                pass

        except Exception as e:
            print('clockCntrProc exception')
            print(e.message, e.args)
            break

        print( ' clockCntrProc loop time {:.6f} sec.'.\
                format(time.perf_counter()-kStart))
#############################################################################

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

def startClockCntrProc( qLst, clockDict, startTime ):
    procLst = []
    for _ in range(1):
        # Cannot access return value from proc directly.
        proc = mp.Process(
               target = clockCntrProc,
               args   = ( 'clockCntrProc',  # Process Name.
                          qLst,             # [lcdCq,lcdRq,clkCq,clkRq]
                          clockDict,        # Cal'd wait time.
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
        digitDict = cfgDict['digitScreenDict']
        clockDict = cfgDict['clkCalDict']
    except:
        return ['clock not started.']
    startLcdUpdateProc( qLst, digitDict )
    time.sleep(1)
    startClockCntrProc( qLst, clockDict,  startTime )
    return ['clock started.' ]
#############################################################################

def medianFilter(data, windowSize):
    if windowSize % 2 == 0:
        raise ValueError('Window size must be odd')

    tempList = []
    for i in range(len(data)):
        start = max(0, i - windowSize // 2)
        end = min(len(data), i + windowSize // 2 + 1)
        window = sorted(data[start:end])
        tempList.append(window[len(window) // 2])
    return tempList
#############################################################################

def calClk(prmLst):

    calTime = int(prmLst[0])
    print(' Collecting Data: ...')
    myLst   = []
    for _ in range(calTime):
        kStart = time.time()
        time.sleep(1)
        myLst.append( 1-(time.time()-kStart) )
        print('{:10.6f}'.format((time.time()- kStart)))
    myLst2 = medianFilter( myLst, len(myLst) )

    print(' Calculating Effective Times: ...')
    meanOfRawErr        = statistics.mean(   myLst  )
    medianOfRawErr      = statistics.median( myLst  )
    meanOfFilteredErr   = statistics.mean(   myLst2 )
    medianOfFilteredErr = statistics.median( myLst2 )

    oneSecCalPerMeanOfRawErr        = 1 + meanOfRawErr
    oneSecCalPerMedianOfRawErr      = 1 + medianOfRawErr
    oneSecCalPerMeanOfFilteredErr   = 1 + meanOfFilteredErr
    oneSecCalPerMedianOfFilteredErr = 1 + medianOfFilteredErr

    print(' Testing Effective Times: ... \n')

    pLst =[' Sleep 1 rawMean    cal\'d:',' Sleep 1 rawMedian  cal\'d:',
           ' Sleep 1 filtMean   cal\'d:',' Sleep 1 filtMedian cal\'d:']

    cLst =[ oneSecCalPerMeanOfRawErr,      oneSecCalPerMedianOfRawErr,
            oneSecCalPerMeanOfFilteredErr, oneSecCalPerMedianOfFilteredErr ]

    tstResults = []
    for p,c in zip(pLst, cLst):
        myLst = []
        print(p)
        for _ in range(calTime):
            kStart = time.time()
            time.sleep(c)
            myLst.append(1-(time.time()-kStart))
            print('{:10.6f}'.format((time.time()-kStart)))
        rawMean   = statistics.mean(myLst)
        print('  rawMean   = {:11.6f} uSec   \n'.format(rawMean  * 1000000))
        tstResults.append(rawMean  * 1000000)

    cfgDict    = cd.loadCfgDict()
    clkCalDict = { 'calibrated1Sec': {  # Values of a calibrated 1 second.
                                       'A_oneSecCalPerMeanOfRawErr':
                                        oneSecCalPerMeanOfRawErr,
                                       'B_oneSecCalPerMedianOfRawErr':
                                        oneSecCalPerMedianOfRawErr,
                                       'C_oneSecCalPerMeanOfFilteredErr':
                                        oneSecCalPerMeanOfFilteredErr,
                                       'D_oneSecCalPerMedianOfFilteredErr':
                                        oneSecCalPerMedianOfFilteredErr
                                     },

                   'testResults'   : {  # Avg err using above cal'd 1 sec.
                                       'A_oneSecCalPerMeanOfRawErr':
                                        tstResults[0],
                                       'B_oneSecCalPerMedianOfRawErr':
                                        tstResults[1],
                                       'C_oneSecCalPerMeanOfFilteredErr':
                                        tstResults[2],
                                       'D_oneSecCalPerMedianOfFilteredErr':
                                        tstResults[3]
                                     },
                   'keyToRunWith'  :   'TBS'
                 }
    # Find the key to the best test result.
    bestKey = ''
    bestVal = 1000.0
    for k,v in clkCalDict['testResults'].items():
        if abs(v) < bestVal:
            bestKey = k
            bestVal = abs(v)

    clkCalDict['keyToRunWith'] = bestKey

    cfgDict = cd.updateCfgDict( cfgDict, clkCalDict=clkCalDict)
    cfgDict = cd.saveCfgDict(cfgDict)
    rspStr  = pp.pformat(clkCalDict)

    return[rspStr]
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

    rsp = startClk([ [], [lcdCqMain,lcdRqMain,clkCqMain,clkRqMain] ])
    print([rsp])

    while True:
        try:
            print('main looping')
            time.sleep(10)
        except:
            sr.hwReset()         # HW Reset

