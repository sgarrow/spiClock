'''
This is the user interface to the server.  All of the files in this project
must be on the RPi except this one although it may/can also be on the RPi.

This file can be run on the Rpi, a PC or a phone.
'''

try:
    import readline         # So up arrow will recall last entered command.
    print(readline.backend) # This line just to eliminate a pylint error.
except (ModuleNotFoundError, AttributeError):
    print('\n Exception importing readline. ok to continue.\n')

import sys
import socket
import time
import select
import threading
import queue
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
            prompt = '\n Choice (m=menu, q=quit) -> '
            userInput = input( prompt )

        uiToMainQ.put(userInput)
        time.sleep(.01) # Gives 'main' a chance to run.
#############################################################################

if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #connectType = input(' ssh, lan, internet (s,l,i) -> ')
    connectType = 'l'
    #             {'s':'localhost','l':'lanAddr','i':'routerAddr'}
    connectDict = {'s':'localhost','l':'0.0.0.0','i':'00.00.00.00'}
    PORT = 0000
    try:
        clientSocket.connect((connectDict[connectType], PORT ))
    except ConnectionRefusedError:
        print('\n ConnectionRefusedError.  Ensure server is running.\n')
        sys.exit()
    except socket.timeout:
        print('\n TimeoutError.  Ensure server is running.\n')
        sys.exit()

    printSocketInfo(clientSocket)

    # Validate pWord
    #pwd = input( ' Enter password -> ')
    pwd = 'tempPW' # pylint: disable=C0103
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
    while pwdIsOk:
        try:
            message = Ui2MainQ.get()
        except queue.Empty:
            pass
        else:
            clientSocket.send(message.encode())

        with threadLock:  # Same story.
            readyToRead, _, _ = select.select([clientSocket], [], [], None)
            if readyToRead:
                rspStr = ''
                while readyToRead:
                    response = clientSocket.recv(1024)
                    rspStr += response.decode()

                    if 'RE: ks' in rspStr:
                        break

                    readyToRead,_, _=select.select([clientSocket],[],[],.25)
                print('\n{}'.format(rspStr))

        if message == 'close' or 'RE: ks' in rspStr:
            break

    print('\n Client closing Socket')
    clientSocket.close()
