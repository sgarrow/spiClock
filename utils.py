#############################################################################
import time
import threading         as th
import testRoutines      as tr
import startStopClock    as cr
openSocketsLst = []     # Needed for processing close and ks commands.
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

    tr.runTest4()
    time.sleep(3)

    if stoppedClock:
        print('starting clock')
        cr.startClk([startTimeLst,qs,styleDic,styleLk])

    return ['done']
#############################################################################
