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
        lanIp   = inLanIp.split('.')
    else:
        lanIp   = [ '?', '?', '?', '?' ]

    verStrLst = cv.getVer()
    verStr    = verStrLst[0]
    verLines  = verStr.split('\n')
    appVerStr = verLines[0]
    srvVerStr = verLines[1]

    appVerSplit = appVerStr.split('=')
    #appVerName  = appVerSplit[0]
    appVerNum   = appVerSplit[1].split(' - ')[0]
    #appVerDt    = appVerSplit[1].split(' - ')[1]

    srvVerSplit = srvVerStr.split('=')
    #srvVerName  = srvVerSplit[0]
    srvVerNum   = srvVerSplit[1].split(' - ')[0]
    #srvVerDt    = srvVerSplit[1].split(' - ')[1]

    appV = [ x.strip() for x in appVerNum.split('.') ]
    srvV = [ x.strip() for x in srvVerNum.split('.') ]
    print()

    print(' LAN IP  as list: {}'.format( lanIp  ))
    print(' APP VER as list: {}'.format( appV ))
    print(' SRV VER as list: {}'.format( srvV ))

    grey  = (128,128,128)
    blk   = (255,255,255)

    d1= ms.mkPilTxtImg('\nLAN\nApp\nSrv', blk,grey,fontSize =50)
    d2= ms.mkPilTxtImg('\nIP\nVer\nVer',  blk,grey,fontSize =50)

    d3= ms.mkPilTxtImg('\n{}\n  {}\n  {}'.format( lanIp[0], appV[0][0],
                                          srvV[0][0]), blk,grey,fontSize=50)

    d4= ms.mkPilTxtImg('\n{}\n  {}\n  {}'.format( lanIp[1], appV[0][1],
                                          srvV[0][1]), blk,grey,fontSize=50)

    d5= ms.mkPilTxtImg('\n{}\n{}\n{}'.format( lanIp[2],appV[1],srvV[1]),
                                              blk,grey,fontSize =50)

    d6= ms.mkPilTxtImg('\n{}\n{}\n{}'.format( lanIp[3],appV[2],srvV[2]),
                                              blk,grey,fontSize =50)

    pixLst= [ d1, d2, d3, d4, d5, d6]
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
