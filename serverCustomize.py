import socket                # For creating and managing sockets.
import time
import multiprocessing as mp
import cmdVectors      as cv # Contains vectors to "worker" functions.
import spiRoutines     as sr
import makeScreen      as ms
specialCmds = ['up']
#############################################################################

def getMultiProcSharedDict():
    manager = mp.Manager()
    styleDict = manager.dict({
        'activeDigitStyle': 'greyOnBlack', # This style cannot be deleted.
        'dayDigitStyle'   : 'greyOnBlack',
        'nightDigitStyle' : 'greyOnBlack',
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
    print(' LCD hw and sw has been reset.')
#############################################################################

def displayLanIp(inLanIp):
    if inLanIp:
        lanIpLst   = inLanIp.split('.')
    else:
        lanIpLst   = [ '?', '?', '?', '?' ]

    verND      = cv.getVer()
    verNDSplit = verND[0].split('-')
    verN       = [ x.strip() for x in verNDSplit[0].split('.') ]

    print(' LAN IP  as list: {}'.format( lanIpLst ))
    print(' SW  VER as list: {}'.format( verN     ))

    grey  = (128,128,128)
    black = (255,255,255)

    data1 = ms.mkPilTxtImg('LAN\nSW',                                black,grey,fontSize =80)
    data2 = ms.mkPilTxtImg('IP\nVER',                                black,grey,fontSize =80)
    data3 = ms.mkPilTxtImg('{}\n  {}'.format(lanIpLst[0],verN[0][0]),black,grey,fontSize =80)
    data4 = ms.mkPilTxtImg('{}\n  {}'.format(lanIpLst[1],verN[0][1]),black,grey,fontSize =80)
    data5 = ms.mkPilTxtImg('{}\n{}'.format(  lanIpLst[2],verN[1]   ),black,grey,fontSize =80)
    data6 = ms.mkPilTxtImg('{}\n{}'.format(  lanIpLst[3],verN[2]   ),black,grey,fontSize =80)
    pixLst= [ data1, data2, data3, data4, data5, data6]
    kLst = ['hrMSD','hrLSD','mnMSD','mnLSD','scMSD','scLSD']
    sr.setBkLight([1])    # Turn on (all) backlights.
    for did,pl in zip(kLst,pixLst):
        sr.setEntireDisplay(did, pl, sr.sendDat2ToSt7789)
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
                #print('     {:6} of {:6} bytes'.\
                #    format(totBytesRecvd, inNumBytes))
    if response == '':
        response = ' Srvr rcvd file {:>20}. {:4,d} pkts. {:7,d} bytes. {:5.3f} sec.\n'.\
            format(outFile, packetNum, totBytesRecvd, totRcvTime)

    return response
#############################################################################
