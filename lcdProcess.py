import time
import datetime        as dt
import multiprocessing as mp
import cfgDict         as cd
import spiRoutines     as sr
#############################################################################
#############################################################################

def lcdUpdateProc( procName, qLst, digitDict ):
    print(' {} {}'.format(procName, 'starting'))

    lcdCq = qLst[0]
    lcdRq = qLst[1]
    #clkCq = qLst[2]
    #clkRq = qLst[3]

    # timeDict, which is placed in my cmdQ, has the same key names as the
    # displayIdDict. The displayIdDict is used by the functions in the
    # spiRoutines.py module to determine the CS pin to use.
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']

    while True:

        data = lcdCq.get()   # Block here. Get digit/stop from clk/user.
        kStart = time.perf_counter()

        if data == 'stop':
            break
        timeDict = data

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
                format(time.perf_counter()-kStart, hmsStr, hmsChangeStr, displaysUpdatedStr))

    lcdRq.put(' {} {}'.format(procName, 'exiting'))  # Put rsp back to user.
#############################################################################

if __name__ == '__main__':
    pass
    #lcdCqMain = mp.Queue()    # LCD Cmd Q. mp queue must be used here.
    #lcdRqMain = mp.Queue()    # LCD Rsp Q. mp queue must be used here.
    #clkCqMain = mp.Queue()    # CLK Cmd Q. mp queue must be used here.
    #clkRqMain = mp.Queue()    # CLK Rsp Q. mp queue must be used here.
    #
    #keyLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    #displayID = keyLst[-1] # pylint: disable=C0103
    #
    #resp = startClk(
    #                [
    #                  [ ],
    #                  [ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ]
    #                ]
    #              )
    #print(resp)
    #
    #if 'make screens' not in resp[0]:
    #    for _ in range(10):
    #        time.sleep(1.2)
    #    stopClk([ lcdCqMain,lcdRqMain,clkCqMain,clkRqMain ] )
    #    time.sleep(2)
    #    sr.hwReset()           # HW Reset
    #    sr.swReset(displayID)  # SW Reset and the display initialization.
    #    sr.setBkLight([0])     # Turn off backlight.
