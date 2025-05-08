import time
import styleMgmtRoutines as sm
import spiRoutines       as sr
import makeScreen        as ms
#############################################################################
#############################################################################

def runTest1():
    # Performs 6 different tests a single LCD - the scLSD display.
    # Test 1 - Fill  1% of screen w/ solid colors one at a time.
    # Test 2 - Fill entire screen w/ solid colors one row at a time.
    # Test 3 - Fill entire screen w/ solid colors in one shot.
    # Test 4 - Fill entire screen w/ mixed colors in one shot.
    # Test 5 - Fill entire screen w/ constructed PIL test images in one shot.
    # Test 6 - Fill entire screen w/ constructed PIL RGB/JPG images in one shot.

    # Set the desired display to scLSD and initialize that display.
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    displayID = kLst[-1]
    sr.hwReset()          # HW Reset
    sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBkLight([1])    # Turn on backlight.
    ###########################################

    rPixLst,rRowLst,rScrLst = ms.makeColoredPRSLstsOfBytes(0xFF0000) # pylint: disable=W0612
    gPixLst,gRowLst,gScrLst = ms.makeColoredPRSLstsOfBytes(0x00FF00) # pylint: disable=W0612
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x0000FF) # pylint: disable=W0612
    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF) # pylint: disable=W0612
    kPixLst,kRowLst,kScrLst = ms.makeColoredPRSLstsOfBytes(0x000000) # pylint: disable=W0612

    barLst = []
    for _ in range(8):
        for coloredBar in [rRowLst,gRowLst,bRowLst,wRowLst]:
            for _ in range(10):
                barLst.extend(coloredBar)

    sendFuncs = [ sr.sendDatToSt7789, sr.sendDat2ToSt7789 ]

    rspStr = 'Begin test 1.1 - Fill 1% of screen w/ solid colors one at a time.\n'
    pixLst    = [ rPixLst, gPixLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        x = [sr.setOnePixel(displayID, row, col, pl, sf)\
              for row in range(32) for col in range(24)] # pylint: disable=W0612
        rspStr += ' Fill 1% Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setOnePixel', sf.__name__, time.time() - kStart )
    ##################################################

    rspStr += '\nBegin test 1.2 - Fill entire screen w/ solid colors one row at a time.\n'
    pixLst    = [ bRowLst, wRowLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        for row in range(320):
            sr.setOneRow(displayID, row, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setOneRow', sf.__name__, time.time() - kStart )
        time.sleep(.5)
    ###################################################

    rspStr += '\nBegin test 1.3 - Fill entire screen w/ solid colors in one shot.\n'
    pixLst    = [ rScrLst, gScrLst, barLst, barLst[::-1] ]
    for sf,pl in zip( sendFuncs*2, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    ####################################################

    rspStr += '\nBegin test 1.4 - Fill entire screen w/ constructed PIL images in one shot.\n'
    #                                textColor backgroundColor
    data1  = ms.makePilTextImage('1', (0,0,0), (255,255,255) )
    data2  = ms.makePilTextImage('2', (0,0,0), (255,255,255) )
    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    ####################################################

    rspStr += '\nBegin test 1.5 - Fill entire screen w/ constructed RGB/JPG images in one shot.\n'
    data1  = ms.makePilJpgPicImage('pics/240x320a.jpg')
    data2  = ms.makePilJpgPicImage('pics/240x320b.jpg')
    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    ####################################################

    sr.setEntireDisplay(displayID, wScrLst, sr.sendDat2ToSt7789)
    sr.setBkLight([0]) # Turn off backlight.

    return [rspStr]
#############################################################################
def runTest2(prmLst):

    lcdCq    = prmLst[0]
    styleDic = prmLst[1]
    styleLk  = prmLst[2]

    # Performs 1 test on all displays.
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
        rspLst = sm.setActiveStyle([str(styleIdx),styleDic,styleLk,lcdCq])
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

    sr.hwReset()              # HW Reset
    for displayID in kLst:
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBkLight([0])        # Turn off backlight.

    return [rspStr]
#############################################################################

def runTest3():
    rspStr = ' Not Implemented'
    #for b in range(255,0,-5):
    #    r = sr.writeDisplayBrightness(b)[0] + '\n'
    #    print(r)
    #    rspStr += r
    return [rspStr]
#############################################################################

def runTest4():

    dspIdLst = [ 'hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD' ]
    sr.hwReset()              # HW Reset
    for displayID in dspIdLst:
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBkLight([1])        # Turn on backlight.

    picLst   = [ 'pics/240x320a.jpg', 'pics/240x320b.jpg', 'pics/240x320c.jpg',
                 'pics/240x320d.jpg', 'pics/240x320e.jpg', 'pics/240x320f.jpg' ]

    for displayID, pic in zip( dspIdLst, picLst ):
        data = ms.makePilJpgPicImage(pic)
        sr.setEntireDisplay( displayID, data, sr.sendDat2ToSt7789 )

    return ['done']
#############################################################################

if __name__ == '__main__':
    import multiprocessing as mp
    mnLcdCq = mp.Queue() # LCD Cmd Q. mp queue must be used here.
    mnLcdRq = mp.Queue() # LCD Rsp Q. mp queue must be used here.
    mnClkCq = mp.Queue() # CLK Cmd Q. mp queue must be used here.
    mnClkRq = mp.Queue() # CLK Rsp Q. mp queue must be used here.

    #resp = runTest1()
    #print(resp[0])
    print('T2')
    resp = runTest2(mnLcdCq)
    print(resp[0])

    #time.sleep(2)

    #print('T3')
    #resp = runTest3()
    #print(resp[0])
    #print('done')
