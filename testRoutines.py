import time
import spiRoutines as sr
import makeScreen  as ms
#############################################################################

def runTest():

    sr.hwReset()         # HW Reset
    sr.swReset()         # SW Reset and the display initialization.
    sr.setBackLight([1]) # Turn on backlight.

    rPixLst,rRowLst,rScrLst = ms.makeColoredPRSLstsOfBytes(0xFF0000)
    gPixLst,gRowLst,gScrLst = ms.makeColoredPRSLstsOfBytes(0x00FF00)
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x0000FF)
    wPixLst,wRowLst,wScrLst = ms.makeColoredPRSLstsOfBytes(0xFFFFFF)
    bPixLst,bRowLst,bScrLst = ms.makeColoredPRSLstsOfBytes(0x000000)

    sendFuncs = [ sr.sendDatToSt7789, sr.sendDat2ToSt7789 ]

    # Test 1 - Fill w/ solid color via setOneRow using both sendFuncs.
    #          Use a different color for each screen fill.
    #print('Begin test 1')
    #
    #pixLst    = [ rPixLst, gPixLst ]
    #for sf,pl in zip( sendFuncs, pixLst ):
    #    kStart = time.time()
    #    for row in range(32):
    #        for col in range(24):
    #            sr.setOnePixel(row, col, pl, sf)
    #    print( ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec'.\
    #        format( 'setOnePixel', sf.__name__, time.time() - kStart ))
    ##################################################

    # Test 2 - Fill w/ solid color via setOneRow using both sendFuncs.
    #          Use a different color for each screen fill.
    #print('Begin test 2')
    #pixLst    = [ bRowLst, wRowLst ]
    #for sf,pl in zip( sendFuncs, pixLst ):
    #    kStart = time.time()
    #    for row in range(320):
    #        sr.setOneRow(row, pl, sf)
    #    print( ' Filling Screen via ( {:16} using {:16}) took {:7.3f} sec'.\
    #        format( 'setOneRow', sf.__name__, time.time() - kStart ))
    #    time.sleep(1)
    ###################################################

    # Test 3 - Fill w/ solid color via setEntireDisplay sendFuncs.
    #          Use a different color for each screen fill.
    print('Begin test 3')
    pixLst    = [ rScrLst, gScrLst ]
    pixLst    = [ rScrLst ]
    for sf,pl in zip( sendFuncs, pixLst ):
        kStart = time.time()
        sr.setEntireDisplay(pl, sf)
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
        sr.setEntireDisplay(data, sr.sendDat2ToSt7789)
        time.sleep(1)

    # Test 5 - Fill w/ rgb image.
    print('Begin test 5')
    rgb565Lst = []
    data = ms.makePilRgbPicImage('pics/240x320.rgb')
    sr.setEntireDisplay(data, sr.sendDat2ToSt7789)
    time.sleep(3)

    # Test 6 - Fill w/ jpeg image.
    print('Begin test 6')
    data = ms.makePilJpgPicImage('pics/240x320.jpg')
    sr.setEntireDisplay(data, sr.sendDat2ToSt7789)
    time.sleep(3)

    sr.setEntireDisplay(wScrLst, sr.sendDat2ToSt7789)
    sr.setBackLight([0]) # Turn off backlight.

    return ['Test Complete']
#############################################################################

if __name__ == '__main__':
    #barLst = []
    #for _ in range(8):
    #    for coloredBar in [rRowLst,gRowLst,bRowLst,wRowLst]:
    #        for barWidth in range(10):
    #            barAllLst.extend(coloredBar)
    runTest()
