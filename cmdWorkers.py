import pprint as pp
import time
import datetime
import statistics
import cfgDict as cd
#############################################################################

# On the second Sunday in March, clocks are set ahead one hour at 2:00 a.m.
# local standard time (which becomes 3:00 a.m. local Daylight Saving Time).
# On the first Sunday in November, clocks are set back one hour at 2:00 a.m.
# local Daylight Saving Time (which becomes 1:00 a.m. local standard time).

def startClk(prmLst):

    hours   = int(prmLst[0])
    minutes = int(prmLst[1])
    seconds = int(prmLst[2])

    cfgDict = cd.loadCfgDict()
    try:
        calibratedOneSecTime = cfgDict['clkCalDict']['calibrated1Sec'][cfgDict['clkCalDict']['keyToRunWith']]
    except:
        calibratedOneSecTime = 1
    print(' calibratedOneSecTime  = {:11.6f}'.format(calibratedOneSecTime))

    while True:
        now = datetime.datetime.now()
        print(now)
        #year = now.year
        #month = now.month
        #day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        #microsecond = now.microsecond
    
        if ( hours  == hour and minute == minutes and second == seconds ):
            break

        #time.sleep(.001)
        time.sleep(.2)

    print(calibratedOneSecTime)

    while True:

        if seconds % 15 == 0:
            now = datetime.datetime.now()
            currTime = now.strftime("%H:%M:%S")
            print('{:02}:{:02}:{:02} =? {}'.\
                format( hours, minutes, seconds, currTime ))
        time.sleep( calibratedOneSecTime ) # rawMedianCalOneSec 
        seconds += 1
    
        if seconds  == 60:
            seconds  = 0
            minutes += 1
        if minutes  == 60:
            minutes  = 0
            hours   += 1
        if hours    == 24:
            hours    = 0
#############################################################################

def median_filter(data, window_size):
    if window_size % 2 == 0:
        raise ValueError("Window size must be odd")

    temp_list = []
    for i in range(len(data)):
        start = max(0, i - window_size // 2)
        end = min(len(data), i + window_size // 2 + 1)
        window = sorted(data[start:end])
        temp_list.append(window[len(window) // 2])
    return temp_list
#############################################################################

def calClk(prmLst):
    global rawMeanCalOneSec
    global rawMedianCalOneSec
    global filtMeanCalOneSec
    global filtMedianCalOneSec
    calTime = int(prmLst[0])

    print(' Collecting Data: ...')
    myLst   = []
    for ii in range(calTime):
        kStart = time.time()
        time.sleep(1)
        myLst.append( 1-(time.time()-kStart) )
        print('{:10.6f}'.format((time.time()- kStart)))
    myLst2 = median_filter( myLst, len(myLst) )

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
        for ii in range(calTime):
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
    rspStr  = pp.pformat(cfgDict)

    return[rspStr]
#############################################################################
