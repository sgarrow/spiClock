import time
import threading         as th
import startStopClock    as cr
import makeScreen        as ms
import spiRoutines       as sr
openSocketsLst = []     # Needed for processing close and ks commands.
#############################################################################
#############################################################################

def getActiveThrds():

    rspStr = ' Running Threads:\n'
    for t in th.enumerate():
        rspStr += '   {}\n'.format(t.name)

    rspStr += '\n Open Sockets:\n'
    for openS in openSocketsLst:
        rspStr += '   {}\n'.format(openS['ca'])

    rspStr += '\n Running Processes:\n'
    for k,v in cr.procPidDict.items():
        if v is not None:
            rspStr += '   {}\n'.format(k)
    return [rspStr]
#############################################################################

def displayPics(prmLst):
    startTimeLst,qs,styleDic,styleLk = prmLst[0], prmLst[1], prmLst[2], prmLst[3]
    rspStr = getActiveThrds()
    stoppedClock = False
    if 'clockCntrProc' in rspStr[0] or 'lcdUpdateProc' in rspStr[0]:
        print('stopping clock')
        cr.stopClk(qs)
        stoppedClock = True

    ##################################
    rspStr = getActiveThrds()
    if 'MainThread' not in rspStr[0]:
        print('reseting LCD')

        dspIdLst = [ 'hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD' ]
        sr.hwReset()              # HW Reset
        for displayID in dspIdLst:
            sr.swReset(displayID) # SW Reset and the display initialization.

    sr.setBkLight([1])            # Turn on backlight.

    picLst   = [ 'pics/240x320a.jpg', 'pics/240x320b.jpg', 'pics/240x320c.jpg',
                 'pics/240x320d.jpg', 'pics/240x320e.jpg', 'pics/240x320f.jpg' ]

    dspIdLst = [ 'hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD' ]

    for displayID, pic in zip( dspIdLst, picLst ):
        data = ms.makePilJpgPicImage(pic)
        sr.setEntireDisplay( displayID, data, sr.sendDat2ToSt7789 )
    time.sleep(3)
    ##################################

    if stoppedClock:
        print('starting clock')
        cr.startClk([startTimeLst,qs,styleDic,styleLk])

    return ['done']
#############################################################################
