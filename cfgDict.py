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
    pp.pprint(cfgDict)

    cfgDict = saveCfgDict(cfgDict)
    pp.pprint(cfgDict)

    cd = loadCfgDict()
    pp.pprint(cfgDict)

    clkCalDict = { 'oneSecCalPerMeanOfFilteredErr':   0.9999175032631296,
                   'oneSecCalPerMeanOfRawErr':        0.9999046755618737,
                   'oneSecCalPerMedianOfFilteredErr': 0.9999175071716309,
                   'oneSecCalPerMedianOfRawErr':      0.9999175071716309
                 }

    cfgDict = updateCfgDict( cfgDict, clkCalDict=clkCalDict)
    cfgDict = saveCfgDict(cfgDict)
    pp.pprint(cfgDict)

    cd = loadCfgDict()
    pp.pprint(cfgDict)
#############################################################################

if __name__ == '__main__':
    runTest()


