import pickle
import pprint as pp

#############################################################################
def loadCfgDict():
    try:
        with open('cfgDict.pickle', 'rb') as f:
            cfgDict = pickle.load(f)
        print(' pickle loaded from file')
    except FileNotFoundError as e:
        print(' loadCfgDict FileNotFoundError:', str(e))
        print(' returning an empty dictionary')
        cfgDict = {}
    return cfgDict
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

def runTest():

    cfgDict = loadCfgDict()

    ppStr = pp.pformat(cfgDict.keys())
    print(' {}'.format(ppStr))

    try:
        ppStr = pp.pformat(cfgDict['digitScreenDict'].keys())
        print(' {}'.format(ppStr))
    except KeyError as e:
        print(' runTest KeyError:', str(e))
#############################################################################

if __name__ == '__main__':
    runTest()
