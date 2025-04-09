import pickle
import pprint as pp

#############################################################################
def loadCfgDict():
    rspStr = ''
    try:
        with open('cfgDict.pickle', 'rb') as f:
            cfgDict = pickle.load(f)
        rspStr += ' loadCfgDict: pickle loaded from file'
    except FileNotFoundError as e:
        rspStr += ' loadCfgDict: {}\n'.format(str(e))
        rspStr += ' loadCfgDict: returning an empty dictionary'
        cfgDict = {}
    #print(rspStr)
    return [rspStr, cfgDict]
#############################################################################

def saveCfgDict(cfgDict):
    with open('cfgDict.pickle', 'wb') as handle:
        pickle.dump(cfgDict, handle)
    print(' pickle saved to file')
    return cfgDict
#############################################################################

def updateCfgDict(cfgDict, **kwargs):
    cfgDict.update(kwargs)
    print(' pickle updated')
    return cfgDict
#############################################################################

def readCfgDict():

    rspStr = ''
    rsp = loadCfgDict()
    rspStr += rsp[0]
    cfgDict = rsp[1]

    ppStr = pp.pformat(list(cfgDict.keys()))
    rspStr += '\n cfgDict keys:'
    rspStr += ' {}\n'.format(ppStr)

    try:
        ppStr = pp.pformat(list(cfgDict['digitScreenDict'].keys()))
        rspStr += ' digitScreenDict keys:'
        rspStr += ' {}\n'.format(ppStr)
    except KeyError as e:
        rspStr += ' readCfgDict KeyError: {}\n'.format(str(e))
    return [rspStr]
#############################################################################

if __name__ == '__main__':
    resp = readCfgDict()
    print(resp[0])
