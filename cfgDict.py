import pickle
import pprint as pp

#############################################################################
def loadCfgDict():
    try:
        with open('cfgDict.pickle', 'rb') as f:
            cfgDict = pickle.load(f)
        print('loaded from file')
    except:
        cfgDict = {}
        print('not loaded from file')
    return cfgDict
#############################################################################

def saveCfgDict(cfgDict):
    with open('cfgDict.pickle', 'wb') as handle:
        pickle.dump(cfgDict, handle)
    print('saved to file')
    return cfgDict
#############################################################################

def updateCfgDict(cfgDict, **kwargs):
    cfgDict.update(kwargs)
    print('updated')
    return cfgDict
#############################################################################

def runTest():

    cfgDict = loadCfgDict()
    pp.pprint(cfgDict.keys())
    pp.pprint(cfgDict['digitScreenDict'].keys())
#############################################################################

if __name__ == '__main__':
    runTest()
