import time
import spiRoutines as sr
import makeScreen  as ms
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
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x000000) # pylint: disable=W0612

    barLst = []
    for _ in range(8):
        for coloredBar in [rRowLst,gRowLst,bRowLst,wRowLst]:
            for _ in range(10):
                barLst.extend(coloredBar)
    barRevLst = barLst[::-1]

    sendFuncs = [ sr.sendDatToSt7789, sr.sendDat2ToSt7789 ]

    rspStr  = ''
    rspStr += 'Begin test 1.1 - Fill 1% of screen w/ solid colors one at a time.\n'
    pixLst    = [ rPixLst, gPixLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        for row in range(32):
            for col in range(24):
                sr.setOnePixel(displayID, row, col, pl, sf)
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
    pixLst    = [ rScrLst, gScrLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    ####################################################

    rspStr += '\nBegin test 1.4 - Fill entire screen w/ mixed colors in one shot.\n'
    pixLst    = [ barLst, barRevLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    ####################################################

    rspStr += '\nBegin test 1.5 - Fill entire screen w/ constructed PIL images in one shot.\n'
    textColor       = (  0,  0,  0)
    backgroundColor = (255,255,255)
    data1  = ms.makePilTextImage('1', textColor, backgroundColor)
    data2  = ms.makePilTextImage('2', textColor, backgroundColor)
    pixLst = [ data1, data2 ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        rspStr += ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec\n'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart )
        time.sleep(1)
    ####################################################

    rspStr += '\nBegin test 1.6 - Fill entire screen w/ constructed RGB/JPG images in one shot.\n'
    data1  = ms.makePilRgbPicImage('pics/240x320.rgb')
    data2  = ms.makePilJpgPicImage('pics/240x320.jpg')
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
def runTest2():

    # Performs 1 test on all displays.
    # Displays all characters stored in the digitScreenDict on all displays.
    # digitScreenDict is made by running 'python3 makescreen.py' from the RPi\
    # command line.

    kLst            = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    textLst         = ['0','1','2','3','4','5','6','7','8','9']

    rspLst     = ms.getAllStyles()
    funcRspStr = rspLst[0]
    styleLst   = rspLst[1]

    sr.hwReset()              # HW Reset
    for displayID in kLst:    # pylint: disable=C0103
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBkLight([1])        # Turn on backlight.

    rspStr = ''
    for style in styleLst:
        rspLst = ms.setActiveStyle([style])
        rspLst = ms.loadActiveStyle()
        digitScreenDict = rspLst[1]
        for k in textLst:
            for displayID in kLst:  # pylint: disable=C0103
                data = digitScreenDict[k]
                kStart = time.perf_counter()
                sr.setEntireDisplay(displayID, data, sr.sendDat2ToSt7789)
                delta = time.perf_counter()-kStart
                if delta > .008:
                    rspStr += ' LCD update time {:.6f} sec. {} {} {}.\n'.\
                        format(delta, style, k, displayID)

    sr.hwReset()              # HW Reset
    for displayID in kLst:    # pylint: disable=C0103
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBkLight([0])        # Turn off backlight.

    return [rspStr]
#############################################################################
if __name__ == '__main__':
    resp = runTest1()
    print(resp[0])
    resp = runTest2()
    print(resp[0])
