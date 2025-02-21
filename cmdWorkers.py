import time
import datetime
import statistics
#############################################################################

def updateCfgData(inDict, **kwargs):
    inDict.update(kwargs)
    with open('pickle/configData.pickle', 'wb') as f:
        pickle.dump(inDict, f)
    return inDict

# initSapStateMachineInfo()

# def initSapStateMachineInfo():
#     sapStateMachineInfo = {
#     'sapState'   : 0,
#     'profNames'  : [],
#     }
#     with open('pickle/sapStateMachineInfo.pickle', 'wb') as handle:
#         pickle.dump(sapStateMachineInfo, handle)
#     return sapStateMachineInfo

# stateMachInfo = updateSapStateMachineInfo(stateMachInfo,sapState=2)


#############################################################################

# On the second Sunday in March, clocks are set ahead one hour at 2:00 a.m.
# local standard time (which becomes 3:00 a.m. local Daylight Saving Time).
# On the first Sunday in November, clocks are set back one hour at 2:00 a.m.
# local Daylight Saving Time (which becomes 1:00 a.m. local standard time).

rawMeanCalOneSec    =  1
rawMedianCalOneSec  =  1
filtMeanCalOneSec   =  1
filtMedianCalOneSec =  1

def startClk(prmLst):

    global rawMeanCalOneSec
    global rawMedianCalOneSec
    global filtMeanCalOneSec
    global filtMedianCalOneSec

    hours   = prmLst[0]
    minutes = prmLst[1]
    seconds = prmLst[2]

    try:
        with open('pickle/configData.pickle', 'rb') as f:
            cfgDataDict = pickle.load(f)
            calibratedOneSecTime = cfgDataDict['calibratedOneSecTime']
        with open('pickle/configData.pickle', 'wb') as f:
            pickle.dump(cfgDataDict, f )
    except:
        calibratedOneSecTime = 1

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
    
        if hours == hour and minute == minutes and second == seconds:
            break
        time.sleep(.001)

    print(calibratedOneSecTime)

    while True:

        if seconds == 0:
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
    calTime = prmLst[0]
    myLst   = []
    for ii in range(calTime):
        kStart = time.time()
        time.sleep(1)
        #print('{:10.6f}'.format((time.time()- kStart)))
        myLst.append( 1-(time.time()- kStart) )
    myLst2 = median_filter( myLst, len(myLst) )

    rawMean    = statistics.mean(   myLst  )
    rawMedian  = statistics.median( myLst  )
    filtMean   = statistics.mean(   myLst2 )
    filtMedian = statistics.median( myLst2 )

    rawMeanCalOneSec    = 1 + rawMean
    rawMedianCalOneSec  = 1 + rawMedian
    filtMeanCalOneSec   = 1 + filtMean
    filtMedianCalOneSec = 1 + filtMedian

    cfgDataDict = {'calibratedOneSecTime':  rawMedianCalOneSec }
    with open('pickle/configData.pickle', 'wb') as f:
        pickle.dump(cfgDataDict, f )

    rspStr =  '\n'
    rspStr += ' Uncalibrated Sleep 1 Second Error Statistics: \n'
    rspStr += '  rawMean    = {:10.6f} uSec \n'.format(rawMean   *1000000)
    rspStr += '  rawMedian  = {:10.6f} uSec \n'.format(rawMedian *1000000)
    rspStr += '  filtMean   = {:10.6f} uSec \n'.format(filtMean  *1000000)
    rspStr += '  filtMedian = {:10.6f} uSec \n'.format(filtMedian*1000000)

    rspStr += '\n Calibrated Sleep 1 Second Effective Times: \n'
    rspStr += '  rawMeanCalOneSec    = {:12.9f} \n'.format(rawMeanCalOneSec   )
    rspStr += '  rawMedianCalOneSec  = {:12.9f} \n'.format(rawMedianCalOneSec )
    rspStr += '  filtMeanCalOneSec   = {:12.9f} \n'.format(filtMeanCalOneSec  )
    rspStr += '  filtMedianCalOneSec = {:12.9f} \n'.format(filtMedianCalOneSec)
    
    rspStr += '\n Testing Effective Times: ... \n\n'

    pLst =[' Sleep 1 rawMean    cal\'d: \n',' Sleep 1 rawMedian  cal\'d: \n',
           ' Sleep 1 filtMean   cal\'d: \n',' Sleep 1 filtMedian cal\'d: \n']

    cLst =[ rawMeanCalOneSec,   rawMedianCalOneSec,
           filtMeanCalOneSec,  filtMedianCalOneSec ]

    for p,c in zip(pLst, cLst):
        myLst = []
        for ii in range(calTime//20):
            kStart = time.time()
            time.sleep(c)
            #print('{:10.6f}'.format((time.time()- kStart)))
            myLst.append(1-(time.time()- kStart))
        
        rawMean   = statistics.mean(   myLst )
        rawMedian = statistics.median( myLst )

        rspStr += p
        rspStr += '  rawMean   = {:10.6f} uSec   \n'.format(rawMean  * 1000000)
        rspStr += '  rawMedian = {:10.6f} uSec \n\n'.format(rawMedian* 1000000)

    return[rspStr]
#############################################################################
