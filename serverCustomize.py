import multiprocessing as mp
import cmdVectors      as cv # Contains vectors to "worker" functions.
import spiRoutines as sr

#############################################################################

def getMultiProcSharedDict():
    manager = mp.Manager()
    styleDict = manager.dict({
        'activeDigitStyle': 'whiteOnBlack',
        'dayDigitStyle'   : 'orangeOnTurquoise',
        'nightDigitStyle' : 'ltRedOnBlack',
        'nightTime'       : [ 2, 1, 0, 0, 0, 0 ],
        'dayTime'         : [ 0, 7, 0, 0, 0, 0 ],
        'alarmTime'       : [ 0, 0, 0, 0, 0, 0 ], 
    })
    styleDictLock = mp.Lock()
    return styleDict, styleDictLock
#############################################################################

def ksCleanup(styleDict, styleDictLock):
    rspStr  = ''
    rspStr += cv.vector('pc',  styleDict, styleDictLock) + '\n'
    rspStr += '\n\n' + cv.vector('sb 0', styleDict, styleDictLock) + '\n'
    return rspStr
#############################################################################

def hwInit():
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    sr.hwReset()           # HW Reset. Common pin to all dislays.
    for theKey in kLst:
        sr.swReset(theKey) # SW Reset and display initialization.
    print('LCD hw and sw has been reset.')
