import socket                # For creating and managing sockets.
import time
import multiprocessing as mp
import cmdVectors      as cv # Contains vectors to "worker" functions.
import spiRoutines as sr
specialCmds = ['up']
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
#############################################################################

def specialCmdHndlr(inParms, clientSocket):

    response = ''

    inFileName    = inParms[1].split('/')[-1]
    inNumBytes    = int(inParms[2])
    outFile       = 'pics/{}'.format(inFileName)
    packetNum     = 0
    totRcvTime    = 0
    totBytesRecvd = 0

    with open(outFile, 'wb') as f:

        while totBytesRecvd < inNumBytes:
            kStart = time.time() # recv timeout = 3 sec.

            try:
                data = clientSocket.recv(1024) # Broke if msg>1024.
            except socket.timeout:
                response = 'unexpected socket timeout'
                break
            else:
                f.write( data )
                elapsedTime    = time.time()-kStart
                totBytesRecvd += len(data)
                packetNum     += 1
                totRcvTime    += elapsedTime
                #print('Time to rcv/save data pkt {:4} = {:08.6f}'.\
                #    format(packetNum, elapsedTime))
                #print('     {} of {} bytes\n'.\
                #    format(totBytesRecvd, inNumBytes))
    if response == '':
        response = ' Server received file {} in {:,d} packets ({:,d} bytes) in {:6.3f} sec.\n'.\
            format(outFile, packetNum, totBytesRecvd, totRcvTime)

    return response
#############################################################################

