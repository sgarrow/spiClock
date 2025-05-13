def getClkCfgDict():
    cfgDict = {}
    with open('clk.cfg', 'r',encoding='utf-8') as f:
        fLines = f.readlines()
    for line in fLines:
        if '#' not in line:
            lSplit = line.split()
            cfgDict[lSplit[0]] = lSplit[-1]
    #for k,v in cfgDict.items():
    #    print(k,v,type(v))
    return cfgDict
#############################################################################
