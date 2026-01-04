import time
import os
from PIL import Image
#############################################################################

def readBinFileInChunks(inFile, chunkSize=4096):
    with open(inFile, 'rb') as f:
        while True:
            outChunk = f.read(chunkSize)
            if not outChunk:  # An empty bytes object indicates the end of the file
                break
            yield outChunk
#############################################################################

def uploadPic(clientSocket,cmd,file):
    try:
        fStat = os.stat(file)
    except FileNotFoundError:
        print(' \n ERROR: File {} was not found.\n'.format(file))
        return
    except OSError as e:
        print(' \n ERROR: Could not access file {}: {}\n'.format(file,e))
        return

    fSizeBytes    = fStat.st_size

    img           = Image.open(file)
    width, height = img.size
    img.close()

    print('\n File {} is {}x{} pixels, {} bytes.'.\
        format(file, width, height, fSizeBytes))

    if (width,height) != (240,320):
        print(' ERROR.  Image must be 240x320 pixels.\n')
        return

    message = '{} {} {}'.format(cmd, file, fSizeBytes )
    clientSocket.send(message.encode())
    time.sleep(.1)

    numPacketsSent = 0
    numBytesSent   = 0
    for chunk in readBinFileInChunks(file, chunkSize=1024):
        clientSocket.send(chunk)
        numPacketsSent += 1
        numBytesSent += len(chunk)
    print(' Client sent file {} in {:,d} packets ({:,d} bytes).'.\
        format(file, numPacketsSent, numBytesSent))

    return
#############################################################################

def processSpecialCmd(funcName, clientSocket, inMsgLst):

    if funcName != 'up':
        print(' Invalid funcName {}'.format(funcName))
        return

    if len(inMsgLst) < 2:
        print(' ERROR: Too few command line parms.')
        return

    cmd       = inMsgLst[0].strip() # up
    fileSpec  = inMsgLst[1].replace('\\','/')
    hasStar   = '*' in fileSpec
    fileParts = fileSpec.split('/')
    filePath  = '/'.join(fileParts[:-1])

    try:
        picLst = sorted(os.listdir(filePath))
    except FileNotFoundError:
        print(' ERROR: Directory {} was not found.'.format(filePath))
        return
    except OSError as e:
        print(' ERROR: Could not access directory {}:\n {}'.format(filePath,e))
        return

    if hasStar:
        fileLst = [ '{}/{}'.format(filePath, x) for x in picLst if x.endswith('.jpg')]
    else:
        fileLst = [fileSpec]

    #print(' processSpecialCmd fileLst = {}'.format(fileLst))

    for f in fileLst:
        uploadPic(clientSocket,cmd,f)
        time.sleep(.4)
    return
#############################################################################
