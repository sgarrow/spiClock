import os

#############################################################################

def readCfgDict():

    dPath = 'digitScreenStyles'
    try:
        fileNameLst = os.listdir(dPath)
    except FileNotFoundError:
        fileNameLstNoExt = []
        rspStr += ' Directory {} not found.'.format(dPath)
    else:
        fileNameLstNoExt = [os.path.splitext(file)[0] for file in fileNameLst]
        rspStr  = ' '
        rspStr += ' \n '.join(fileNameLstNoExt)

    return [rspStr,fileNameLstNoExt]
#############################################################################

if __name__ == '__main__':
    resp = readCfgDict()
    print(resp[0])
