from PIL import Image
import time
import os
#############################################################################

def readBinFileInChunks(inFile, chunkSize=4096):
    with open(inFile, 'rb') as f:
        while True:
            outChunk = f.read(chunkSize)
            if not outChunk:  # An empty bytes object indicates the end of the file
                break
            yield outChunk
#############################################################################

def uploadPic(clientSocket,cmd,file,rspStr):

    try:
        fStat = os.stat(file)
    except FileNotFoundError:
        return ' {}\n ERROR: File {} was not found.\n'.format(rspStr, file)
    except OSError as e:
        return ' {}\n ERROR: Could not access file {}: {}\n'.format(rspStr, file,e)
    else:
        fSizeBytes = fStat.st_size
        message = '{} {} {}'.format(cmd, file, fSizeBytes )
        clientSocket.send(message.encode())
        time.sleep(.1)

    img = Image.open(file)
    width, height = img.size
    img.close()

    rspStr += '\n File {} is {}x{} pixels, {} bytes.\n'.\
        format(file, width, height, fSizeBytes)

    if (width,height) != (240,320):
        rspStr += ' ERROR.  Image must be 240x320 pixels.\n'

    if 'ERROR' in rspStr:
        return rspStr

    numPacketsSent = 0
    numBytesSent   = 0
    for chunk in readBinFileInChunks(file, chunkSize=1024):
        clientSocket.send(chunk)
        numPacketsSent += 1
        numBytesSent += len(chunk)
    rspStr += ' Client sent file {} in {:,d} packets ({:,d} bytes).\n'.\
        format(file, numPacketsSent, numBytesSent)

    return rspStr
#############################################################################

def processSpecialCmd(funcName, clientSocket, inMsgLst):
    rspStr = ''

    if funcName != 'uploadPic':
        return ' Invalid funcName {}'.format(funcName)

    if len(inMsgLst) < 2:
        return 'ERROR: Too few command line parms.'

    cmd       = inMsgLst[0].strip() # up
    fileSpec  = inMsgLst[1].replace('\\','/')
    hasStar   = '*' in fileSpec
    fileParts = fileSpec.split('/')
    filePath  = '/'.join(fileParts[:-1])

    if hasStar:
        try:
            picLst = sorted(os.listdir(filePath))
        except FileNotFoundError:
            return ' ERROR: Directory {} was not found.'.format(filePath)
        except OSError as e:
            return ' ERROR: Could not access directory {}: {}'.format(file,e)
        fileLst = [ '{}/{}'.format(filePath, x) for x in picLst if x.endswith('.jpg')]
    else:
        fileLst = [fileSpec]

    for f in fileLst:
        rspStr += uploadPic(clientSocket,cmd,f,rspStr)
        time.sleep(1)
    return rspStr
#############################################################################

