import time
import utils             as ut
import makeScreen        as ms
import spiRoutines       as sr
import styleMgmtRoutines as sm

kLst       = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
sendFuncs  = [ sr.sendDatToSt7789, sr.sendDat2ToSt7789 ]
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
#############################################################################

def runTest1():
    if clkRunning():
        return [' Can\'t run a test while the clock is running. pc to stop lock']
    initHw()

    rPixLst,rRowLst,rScrLst = ms.makeColoredPRSLstsOfBytes(0xFF0000) # pylint: disable=W0612
    gPixLst,gRowLst,gScrLst = ms.makeColoredPRSLstsOfBytes(0x00FF00) # pylint: disable=W0612

    rspStr = ' Test 1: Fill 1% of screen w/ solid colors one pixel at a time.\n'
    pixLst    = [ rPixLst, gPixLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        x = [sr.setOnePixel(kLst[-1], row, col, pl, sf)\
              for row in range(32) for col in range(24)] # pylint: disable=W0612
        rspStr += '  Fill 1% Screen via {:16} using {:16} took {:6.3f} sec\n'.\
            format( 'setOnePixel', sf.__name__, time.time() - kStart )
    return [rspStr]
#############################################################################

def runTest2():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x0000FF) # pylint: disable=W0612
    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF) # pylint: disable=W0612

    rspStr = ' Test 2: Fill entire screen w/ solid colors one row at a time.\n'
    pixLst    = [ bRowLst, wRowLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        for row in range(320):
            sr.setOneRow(kLst[-1], row, pl, sf)
        rspStr += '  Fill Screen via {:16} using {:16} took {:6.3f} sec\n'.\
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

    rspStr = ' Test 3: Fill entire screen w/ solid colors in one shot.\n'
    pixLst    = [ rScrLst, gScrLst, barLst, barLst[::-1] ]
    for sf,pl in zip( sendFuncs*2, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(kLst[-1], pl, sf)
        rspStr += '  Fill Screen via {:16} using {:16} took {:6.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest4():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = ' Test 4: Fill entire screen w/ constructed PIL images in one shot.\n'

    txtColor = (0,0,0)
    bckColor = (255,255,255)

    data1  = ms.mkPilTxtImg( 'A', txtColor, bckColor )
    data2  = ms.mkPilTxtImg( 'B', txtColor, bckColor )

    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(kLst[-1], pl, sf)
        rspStr += '  Fill Screen via {:16} using {:16} took {:6.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(3)
    return [rspStr]
#############################################################################

def runTest5():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = ' Test 5: Fill entire screen w/ constructed JPG images in one shot.\n'
    data1  = ms.makePilJpgPicImage('pics/240x320a.jpg')
    data2  = ms.makePilJpgPicImage('pics/240x320b.jpg')
    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(kLst[-1], pl, sf)
        rspStr += '  Fill Screen via {:16} using {:16} took {:6.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    return [rspStr]
#############################################################################

def runTest6(prmLst):
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = ' Test 6 - Fill all screens with all digit styles.\n'

    lcdCq    = prmLst[0]
    styleDic = prmLst[1]
    styleLk  = prmLst[2]

    textLst         = ['0','1','2']
    rspLst     = sm.getAllStyles()
    #funcRspStr = rspLst[0]
    allStyleDic   = rspLst[1]

    rspStr = ''
    for styleIdx in allStyleDic:
        rspLst = sm.setActStyle([str(styleIdx),styleDic,styleLk,lcdCq])
        rspLst = sm.loadActiveStyle(styleDic, styleLk)
        digitScreenDict = rspLst[1]
        for txt in textLst:
            for did in kLst:
                data = digitScreenDict[txt]
                kStart = time.perf_counter()
                sr.setEntireDisplay(did, data, sr.sendDat2ToSt7789)
                delta = time.perf_counter()-kStart
                if delta > .008:
                    rspStr += ' LCD update time {:.6f} sec. {} {} {}.\n'.\
                        format(delta, allStyleDic[styleIdx], txt, did)
    return [rspStr]
#############################################################################
#NotoSerifTC-Light.ttf
def runTest7():
    if clkRunning():
        return [' Can\'t run a test while the clock is running.']
    initHw()

    rspStr = ' Test 6 - Fill all screens with chinese characters.\n'

    txtColor = (0,0,0)
    bckColor = (255,255,255)
    f1       = 'fonts/NotoSerifTC-Black.ttf'
    f2       = 'fonts/NotoSerifTC-Medium.ttf'
    f3       = 'fonts/NotoSerifTC-Light.ttf'
    textLst  = ['\u58de', '\u58de', '\u5ff5' , '\u5ff5', '\u6b3e', '\u6b3e']
    textLst  = ['\u58de','\u6b3e'] * 3
    textLst  = ['\u58de', '\u52d2', '\u5ff5' , '\u64e6', '\u6b3e', '\u79aa']
    fontLst  = [ f3,f3,f3,f3,f3,f3 ]
    rspStr = ''
    for did,txt,f in zip(kLst,textLst,fontLst):
        data = ms.mkPilTxtImg( txt, txtColor, bckColor, 
                               fontName = f,
                               fontSize = 200, yOffset = 75 )

        kStart = time.perf_counter()
        sr.setEntireDisplay(did, data, sr.sendDat2ToSt7789)
        delta = time.perf_counter()-kStart
        if delta > .008:
            rspStr += ' LCD update time {:.6f} sec. {} {}.\n'.\
                format(delta, txt, did)
    return [rspStr]
#############################################################################

if __name__ == '__main__':
    import multiprocessing as mp
    mnLcdCq = mp.Queue() # LCD Cmd Q. mp queue must be used here.

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
