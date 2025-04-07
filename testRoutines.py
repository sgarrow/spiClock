import time
import spiRoutines as sr
import makeScreen  as ms
import cfgDict     as cd
#############################################################################

def runTest():

    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    displayID = kLst[-1]
    sr.hwReset()          # HW Reset
    sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBackLight([1])  # Turn on backlight.

    rPixLst,rRowLst,rScrLst = ms.makeColoredPRSLstsOfBytes(0xFF0000) # pylint: disable=W0612
    gPixLst,gRowLst,gScrLst = ms.makeColoredPRSLstsOfBytes(0x00FF00) # pylint: disable=W0612
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x0000FF) # pylint: disable=W0612
    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF) # pylint: disable=W0612
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x000000) # pylint: disable=W0612

    sendFuncs = [ sr.sendDatToSt7789, sr.sendDat2ToSt7789 ]

    # Test 1 - Fill w/ solid color via setOneRow using both sendFuncs.
    #          Use a different color for each screen fill.
    print('Begin test 1')

    pixLst    = [ rPixLst, gPixLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        for row in range(32):
            for col in range(24):
                sr.setOnePixel(displayID, row, col, pl, sf)
        print( ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec'.\
            format( 'setOnePixel', sf.__name__, time.time() - kStart ))
    ##################################################

    # Test 2 - Fill w/ solid color via setOneRow using both sendFuncs.
    #          Use a different color for each screen fill.
    print('Begin test 2')
    pixLst    = [ bRowLst, wRowLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        for row in range(320):
            sr.setOneRow(displayID, row, pl, sf)
        print( ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec'.\
            format( 'setOneRow', sf.__name__, time.time() - kStart ))
        time.sleep(1)
    ###################################################

    # Test 3 - Fill w/ solid color via setEntireDisplay sendFuncs.
    #          Use a different color for each screen fill.
    print('Begin test 3')
    pixLst    = [ rScrLst, gScrLst ]
    pixLst    = [ rScrLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(displayID, pl, sf)
        print( ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec'.\
            format( 'setEntireDisplay', sf.__name__, time.time() - kStart ))
        time.sleep(1)
    ####################################################

    # Test 4 - Fill w/ PIL text image.
    print('Begin test 4')
    for text in ['1','2','3','4','5']:
        textColor       = (  0,  0,  0)
        backgroundColor = (255,255,255)
        data = ms.makePilTextImage(text, textColor, backgroundColor)
        sr.setEntireDisplay(displayID, data, sr.sendDat2ToSt7789)
        time.sleep(1)

    # Test 5 - Fill w/ rgb image.
    print('Begin test 5')
    data = ms.makePilRgbPicImage('pics/240x320.rgb')
    sr.setEntireDisplay(displayID, data, sr.sendDat2ToSt7789)
    time.sleep(3)

    # Test 6 - Fill w/ jpeg image.
    print('Begin test 6')
    data = ms.makePilJpgPicImage('pics/240x320.jpg')
    sr.setEntireDisplay(displayID, data, sr.sendDat2ToSt7789)
    time.sleep(3)

    sr.setEntireDisplay(displayID, wScrLst, sr.sendDat2ToSt7789)
    sr.setBackLight([0]) # Turn off backlight.

    return ['Test Complete']
#############################################################################
def runTest2():

    cfgDict         = cd.loadCfgDict()
    digitScreenDict = cfgDict['digitScreenDict']
    kLst            = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    textLst         = ['0','1','2','3','4','5','6','7','8','9']

    sr.hwReset()              # HW Reset
    for displayID in kLst:    # pylint: disable=C0103
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBackLight([1])      # Turn on backlight.

    for style in digitScreenDict.keys():
        for k in textLst:
            for displayID in kLst:  # pylint: disable=C0103
                data = digitScreenDict[style][k]
                sr.setEntireDisplay(displayID, data, sr.sendDat2ToSt7789)

    sr.hwReset()              # HW Reset
    for displayID in kLst:    # pylint: disable=C0103
        sr.swReset(displayID) # SW Reset and the display initialization.
    sr.setBackLight([0])      # Turn off backlight.

    return ['Test Complete']
#############################################################################
if __name__ == '__main__':
    #barLst = []
    #for _ in range(8):
    #    for coloredBar in [rRowLst,gRowLst,bRowLst,wRowLst]:
    #        for barWidth in range(10):
    #            barAllLst.extend(coloredBar)
    runTest()
