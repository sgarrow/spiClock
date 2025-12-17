import time
import utils             as ut
import makeScreen        as ms
import spiRoutines       as sr
import styleMgmtRoutines as sm

kLst      = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
displayID = kLst[-1]  # Test will be run on this display only.
sendFuncs = [ sr.sendDatToSt7789, sr.sendDat2ToSt7789 ]
#############################################################################
#############################################################################

def clkRunning():
    rspStr = ut.getActThrds()
    running = 'clockCntrProc' in rspStr[0] or 'lcdUpdateProc' in rspStr[0]
    return running
#############################################################################

def initHw():
    # Set the desired display to scLSD and initialize that display.
    sr.hwReset()        # HW Reset on all displays.
    for did in kLst:
        sr.swReset(did) # SW Reset and the display init on 1 display.
    sr.setBkLight([1])  # Turn on (all) backlights.
    return
#############################################################################

def runTest1():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rPixLst,rRowLst,rScrLst = ms.makeColoredPRSLstsOfBytes(0xFF0000) # pylint: disable=W0612
    gPixLst,gRowLst,gScrLst = ms.makeColoredPRSLstsOfBytes(0x00FF00) # pylint: disable=W0612

    rspStr = 'Begin test 1 - Fill 1% of screen w/ solid colors one pixel at a time.\n'
    pixLst    = [ rPixLst, gPixLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        x = [sr.setOnePixel(displayID, row, col, pl, sf)\
              for row in range(32) for col in range(24)] # pylint: disable=W0612
        rspStr += ' Fill 1% Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setOnePixel', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest2():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x0000FF) # pylint: disable=W0612
    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF) # pylint: disable=W0612

    rspStr = '\nBegin test 2 - Fill entire screen w/ solid colors one row at a time.\n'
    pixLst    = [ bRowLst, wRowLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        for row in range(320):
            sr.setOneRow(displayID, row, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setOneRow', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest3():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rPixLst,rRowLst,rScrLst = ms.makeColoredPRSLstsOfBytes(0xFF0000) # pylint: disable=W0612
    gPixLst,gRowLst,gScrLst = ms.makeColoredPRSLstsOfBytes(0x00FF00) # pylint: disable=W0612
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x0000FF) # pylint: disable=W0612
    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF) # pylint: disable=W0612

    barLst = []
    for _ in range(8):
        for coloredBar in [rRowLst,gRowLst,bRowLst,wRowLst]:
            for _ in range(10):
                barLst.extend(coloredBar)

    rspStr = '\nBegin test 3 - Fill entire screen w/ solid colors in one shot.\n'
    pixLst    = [ rScrLst, gScrLst, barLst, barLst[::-1] ]
    for sf,pl in zip( sendFuncs*2, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest4():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = '\nBegin test 4 - Fill entire screen w/ constructed PIL images in one shot.\n'
    data1  = ms.mkPilTxtImg('A', (0,0,0), (255,255,255) )
    data2  = ms.mkPilTxtImg('B', (0,0,0), (255,255,255) )
    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest5():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = '\nBegin test 5 - Fill entire screen w/ constructed JPG images in one shot.\n'
    data1  = ms.makePilJpgPicImage('pics/240x320a.jpg')
    data2  = ms.makePilJpgPicImage('pics/240x320b.jpg')
    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest6():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = '\nBegin test 6 - Reset all displays and fill with white and turn off backlight.\n'

    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF) # pylint: disable=W0612

    for dId in kLst:
        sr.setEntireDisplay(dId, wScrLst, sr.sendDat2ToSt7789)
    time.sleep(2)

    sr.setBkLight([0])    # Turn off backlight.
    rspStr = ' Reset all hardware, filled with white, turned off backlight.'
    return [rspStr]
#############################################################################
def runTest7(prmLst):
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    lcdCq    = prmLst[0]
    styleDic = prmLst[1]
    styleLk  = prmLst[2]

    # Performs 1 test on ALL displays.
    # Displays all characters stored in the digitScreenDict on all displays.
    # digitScreenDict is made by running 'python3 makescreen.py' from the RPi\
    # command line.

    kLst            = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    textLst         = ['0','1','2','3','4','5','6','7','8','9']

    rspLst     = sm.getAllStyles()
    #funcRspStr = rspLst[0]
    allStyleDic   = rspLst[1]

    sr.hwReset()              # HW Reset
    for displayID in kLst:
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBkLight([1])        # Turn on backlight.

    rspStr = ''
    for styleIdx in allStyleDic:
        rspLst = sm.setActStyle([str(styleIdx),styleDic,styleLk,lcdCq])
        rspLst = sm.loadActiveStyle(styleDic, styleLk)
        digitScreenDict = rspLst[1]
        for txt in textLst[5:]:
            for displayID in kLst:
                data = digitScreenDict[txt]
                kStart = time.perf_counter()
                sr.setEntireDisplay(displayID, data, sr.sendDat2ToSt7789)
                delta = time.perf_counter()-kStart
                if delta > .008:
                    rspStr += ' LCD update time {:.6f} sec. {} {} {}.\n'.\
                        format(delta, allStyleDic[styleIdx], txt, displayID)

    time.sleep(1)

    # Re-init all displays so the clock will be able to run after this test.
    # Note ALL displays are initialized at boot time by main in server.py.
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    sr.hwReset()          # HW Reset
    for dId in kLst:
        sr.swReset(dId)   # SW Reset and the display initialization.
    sr.setBkLight([0])    # Turn off backlight.
    ###########################################

    return [rspStr]
#############################################################################

if __name__ == '__main__':
    import multiprocessing as mp
    mnLcdCq = mp.Queue() # LCD Cmd Q. mp queue must be used here.
    mnLcdRq = mp.Queue() # LCD Rsp Q. mp queue must be used here.
    mnClkCq = mp.Queue() # CLK Cmd Q. mp queue must be used here.
    mnClkRq = mp.Queue() # CLK Rsp Q. mp queue must be used here.

    resp = runTest1()
    print(resp[0])
    #print('T2')
    #resp = runTest7(mnLcdCq)
    #print(resp[0])

    #time.sleep(2)

    #print('T3')
    #resp = runTest3()
    #print(resp[0])
    #print('done')
