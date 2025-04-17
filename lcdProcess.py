import os
import time
import pickle
import makeScreen  as ms
import spiRoutines as sr
#############################################################################
#############################################################################

def lcdUpdateProc( procName, qLst ):
    debug = True
    if debug: print(' {} {}'.format(procName, 'starting'))

    lcdCq, lcdRq = qLst[0], qLst[1]  # clkCq, clkRq = qLst[2], qLst[3]

    rspLst = ms.loadActiveStyle()
    digitDict = rspLst[1]

    # timeDict, which is placed in my cmdQ, has the same key names as the
    # displayIdDict. The displayIdDict is used by the functions in the
    # spiRoutines.py module to determine the CS pin to use.
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']

    while True:

        data = lcdCq.get()   # Block here. Get digit/stop from clk/user.
        kStart = time.perf_counter()
        print('lcdUpdateProc', ms.getActiveStyle()[0])


        gotStop  = False
        gotTime  = False
        if isinstance(data,str):
            if data == 'stop':
                print('got stop')
                gotStop = True
            else:
                dirPath = 'digitScreenStyles'
                fullFileName = os.path.join(dirPath, data+'.pickle')
                with open(fullFileName, 'rb') as f:
                    digitDict = pickle.load(f)

        elif isinstance(data,dict):
            if 'hrMSD' in data:
                print('got timeDict')
                gotTime = True
                timeDict = data
        else:
            print('ERROR')

        if gotStop:
            break
        if not gotTime:
            continue

        hours   = timeDict['hrMSD']['value'] * 10 + timeDict['hrLSD']['value']
        minutes = timeDict['mnMSD']['value'] * 10 + timeDict['mnLSD']['value']
        seconds = timeDict['scMSD']['value'] * 10 + timeDict['scLSD']['value']
        hmsStr  = '{:02}{:02}{:02}'.format(hours,minutes,seconds)

        displaysUpdatedStr = ' updated:'
        hmsChangeStr = ''
        for theKey in kLst:
            if timeDict[theKey]['updated']:

                #digit   = str(timeDict[theKey]['value'])
                #spiData = digitDict[digit]
                #sr.setEntireDisplay(theKey, spiData, sr.sendDat2ToSt7789)

                sr.setEntireDisplay(theKey,
                                    digitDict[str(timeDict[theKey]['value'])],
                                    sr.sendDat2ToSt7789)

                displaysUpdatedStr += ' {}'.format(theKey)
                hmsChangeStr += '1'
            else:
                hmsChangeStr += '0'

        # Put rsp back to clk.
        lcdRq.put( ' LCD update time {:.6f} sec. {} {} {}.'.\
                format( time.perf_counter()-kStart, hmsStr,
                        hmsChangeStr, displaysUpdatedStr ))

    lcdRq.put(' {} {}'.format(procName, 'exiting'))  # Put rsp back to user.
#############################################################################

if __name__ == '__main__':
    pass
