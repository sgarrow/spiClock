'''
This is the user interface to the server.  All of the files in this project
must be on the RPi except this one although it may/can also be on the RPi.

This file can be run on the Rpi, a PC or a phone.
'''

try:
    import readline  # pylint: disable=W0611
except (ModuleNotFoundError, AttributeError):
    pass
    #print('\n Exception importing readline. ok to continue.\n')

from PIL import Image
import os
import sys
import socket
import time
import select
import threading
import queue
import cfg
#############################################################################

def readBinFileInChunks(inFile, chunkSize=4096):
    with open(inFile, 'rb') as f:
        while True:
            outChunk = f.read(chunkSize)
            if not outChunk:  # An empty bytes object indicates the end of the file
                break
            yield outChunk
#############################################################################

def printSocketInfo(cSocket):
    sndBufSize = cSocket.getsockopt( socket.SOL_SOCKET, socket.SO_SNDBUF )
    rcvBufSize = cSocket.getsockopt( socket.SOL_SOCKET, socket.SO_RCVBUF )
    print( ' sndBufSize', sndBufSize ) # 64K
    print( ' rcvBufSize', rcvBufSize ) # 64K
#############################################################################

def getUserInput( uiToMainQ, aLock ):
    userInput = ''
    while True:
        with aLock:  # If I take just this out then after a command I get a
                     # get a prompt printed, then the rsp printed then need
                     # an extra return to get a prompt again.
            prompt = '\n Choice (m=menu, close) -> '
            userInput = input( prompt )
            uiToMainQ.put(userInput)
            if userInput in ['ks','close']:
                break
        time.sleep(.01) # Gives 'main' a chance to run.
        if userInput == 'up':
            time.sleep(.5) # Gives 'main' a chance to run.
#############################################################################

if __name__ == '__main__':

    arguments  = sys.argv
    scriptName = arguments[0]
    userArgs   = arguments[1:]
    uut        = userArgs[0]
    cfgDict    = cfg.getCfgDict(uut)

    if cfgDict is None:
        print('  Client could not connect to server.')
        print('  Missing or (malformed) cfg file or missing cmd line arg')
        print('  usage1: python client.py uut (uut = spr or clk).')
        print('  usage2: python    gui.py uut (uut = spr or clk).')
        sys.exit()

    # Each client will connect to the server with a new address.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #connectType = input(' ssh, lan, internet (s,l,i) -> ')
    connectType = 'l' # pylint: disable=C0103

    #             {'s':'localhost','l':'lanAddr','i':'routerAddr'}
    connectDict = {'s':'localhost','l':cfgDict['myLan'],'i':cfgDict['myIP']}
    PORT = int(cfgDict['myPort'])
    try:
        clientSocket.connect((connectDict[connectType], PORT ))
    except ConnectionRefusedError:
        print('\n ConnectionRefusedError.  Ensure server is running.\n')
        sys.exit()
    except socket.timeout:
        print('\n TimeoutError.  Ensure server is running.\n')
        sys.exit()

    printSocketInfo(clientSocket)

    # Validate password
    pwd = cfgDict['myPwd']
    clientSocket.send(pwd.encode())
    time.sleep(.5)
    response = clientSocket.recv(1024)
    rspStr   = response.decode()
    print('\n{}'.format(rspStr))
    pwdIsOk = 'Accepted' in rspStr
    #######

    threadLock  = threading.Lock()
    Ui2MainQ    = queue.Queue()
    inputThread = threading.Thread( target = getUserInput,
                                    args   = (Ui2MainQ,threadLock),
                                    daemon = True )
    inputThread.start()

    rspStr = ''
    longExeTimeMsgs = ['mus', 'ks'] # These cmds take long time on server.
    normWaitTime = 0.6
    longWaitTime = 1.6
    while pwdIsOk:
        # Get and send a message from the Q to the server.
        try:
            message = Ui2MainQ.get()
            waitTime = normWaitTime
            if any(word in message for word in longExeTimeMsgs):
                waitTime = longWaitTime

        except queue.Empty:
            pass                    # No message to send.

        else:
            if message == 'up':     # Send special message.
                fileA = 'pics/SHG07393.JPG'
                fileA = 'pics/240x320a.jpg'
                file = fileA.replace('\\','/')
                try:
                    fStat = os.stat(file)
                    fSizeBytes = fStat.st_size
                    message += ' {} {}'.format(fSizeBytes, file)
                    clientSocket.send(message.encode())
                    time.sleep(.1)
                except FileNotFoundError:
                    print(' Error: {} was not found.'.format(file))
                except OSError as e:
                    print(' Error accessing {}: {}'.format(file,e))
                else:
                    img = Image.open(file)
                    width, height = img.size
                    img.close()

                    print('\n {} width x height; size = '.format(file))
                    print('   {:,d} x {:,d} pixels; {:,d} bytes'.\
                        format(width, height, fSizeBytes))

                    if (width,height) != (240,320):
                        print('\n ERROR.  Image must be 240 x 320 pixels.')
                    else:
                        for chunk in readBinFileInChunks(file, chunkSize=1024):
                            clientSocket.send(chunk)

            else:                    # Send normal message.
                clientSocket.send(message.encode())

        # Reseive and print response from server.
        with threadLock:
            readyToRead, _, _ = select.select([clientSocket],[],[],waitTime)
            if readyToRead:
                rspStr = ''
                while readyToRead:
                    response = clientSocket.recv(1024)
                    rspStr += response.decode()
                    if 'RE: ks' in rspStr: # Early exit on ks cmd.
                        break
                    readyToRead,_, _=select.select([clientSocket],[],[],.25)
                print('\n{}'.format(rspStr))

        # Exit client on a close or ks cmd.
        if message == 'close' or 'RE: ks' in rspStr:
            break

    print('\n Client closing Socket')
    clientSocket.close()
