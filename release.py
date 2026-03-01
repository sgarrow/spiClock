from pathlib import Path
import subprocess as sp
import datetime   as dt
import pprint     as pp # pylint: disable=W0611
import sys
import re
#############################################################################

def mapTo2D(  flatList, numCols ):
    # mapTo2D( [1,2,3,4,5,6,7,8], 2 ) = [[1,2],[3,4],[5,6],[7,8]]
    twoD = [flatList[ii:ii+numCols] for ii in range(0,len(flatList),numCols)]
    return twoD
#############################################################################

def printPathInfo(spiClockD,sprinkler2D,sharedD):
    print()
    print( ' spiClockDir   = {}'.format(spiClockD   ))
    print( '   spiClockDir.name   = {}'.format(spiClockD.name   ))
    print( '   spiClockDir.stem   = {}'.format(spiClockD.stem   ))
    print( '   spiClockDir.suffix = {}'.format(spiClockD.suffix ))
    print( '   spiClockDir.anchor = {}'.format(spiClockD.anchor ))
    print( '   spiClockDir.parent = {}'.format(spiClockD.parent ))
    print( ' sprinkler2Dir = {}'.format(sprinkler2D ))
    print( ' sharedDir     = {}'.format(sharedD     ))
    print()
#############################################################################

def moveOrCopyFiles( src, dst, fLst, moveOrCopy ):

    if moveOrCopy not in ['Mov','Copy']:
        print(' moveOrCopy has invalid value.')
        return
    print('   {}ing from \n     {} to \n     {}.'.format( moveOrCopy, src, dst ))

    for file in fLst:
        s =  src / file  # A Path join. All 3 vars type Path.
        d =  dst / file  # A Path join. All 3 vars type Path.
        # Move/Copy if source exists and is a file.
        try:
            if not s.exists():
                raise FileNotFoundError( ' {} not found.'.format(s) )
            if not s.is_file():
                raise IsADirectoryError( ' {} is not a file.'.format(s) )
        except Exception as e:
            print( ' Error: {}'.format(e) )
        else:
            if moveOrCopy == 'Mov':
                s.replace(d)
                print( '       Moved {}.'.format(file))
            elif moveOrCopy == 'Copy':
                d.write_bytes(s.read_bytes())
                print( '       Copied {}.'.format( file))
#############################################################################

def tstMoveOrCopyFiles():
    clkDir   = Path( r'C:\01-home\14-python\temp\tstClkDir' )
    sprDir   = Path( r'C:\01-home\14-python\temp\tstSprDir' )
    shrDir   = Path( r'C:\01-home\14-python\temp\tstShrDir' )
    dsts     = [clkDir, sprDir]
    fLstStr  = [ 'd1.txt', 'd2.txt', 'd3.txt' ]
    fLstPath = [ Path(x) for x in fLstStr ]

    print( '\n Moving files.' )
    #                src     dst     fLst       cmd
    moveOrCopyFiles( clkDir, shrDir, fLstPath, 'Mov' )

    x = input( 'Press Return to Continue.' )

    print( '\n Copying files.' )
    for dstn in dsts:
        #                src      dst   fLst       cmd
        moveOrCopyFiles( shrDir,  dstn, fLstPath, 'Copy' )
#############################################################################

def getVerNums( fName, numChanged, numTracked ):
    curVStr   = None
    newVStrwV = None
    try:
        pcntChange = int((numChanged/numTracked) * 100.0)
    except ZeroDivisionError:
        return curVStr, -1, newVStrwV

    fileWithVerNum = Path( fName )

    try:
        txt = fileWithVerNum.read_text(encoding='utf-8').split('\n')
    except (FileNotFoundError, IsADirectoryError):
        return curVStr, -2, newVStrwV

    verFound = False
    for line in txt:
        if 'VER =' in line:
            curVStr     = \
            line.split('=')[1].split('-')[0].replace('\'','').strip() # v1.6.46
            curVLstwV   = [ x.strip() for x in curVStr.split('.') ]    # ['v1','6','46']
            curVLstwoV  = [curVLstwV[0][1:]] + curVLstwV[1:]          # ['1','6', '46']
            curVIntLst  = [int(x) for x in curVLstwoV]                # [1,6,46]
            verFound = True
            break

    if not verFound:
        return curVStr, -3, newVStrwV

    newVIntLst = curVIntLst[:]
    if pcntChange > 66:
        newVIntLst[0] = newVIntLst[0]+1
        newVIntLst[1] = 0
        newVIntLst[2] = 0
    elif pcntChange > 33:
        newVIntLst[1] = newVIntLst[1]+1
        newVIntLst[2] = 0
    else:
        newVIntLst[2] = newVIntLst[2]+1

    newVStrLst = [ str(x) for x in newVIntLst ]
    newVStr    = '.'.join(newVStrLst)
    newVStrwV = 'v' + newVStr

    return curVStr, pcntChange, newVStrwV
#############################################################################

def runCommand( cmdLst ):
    #print( '\n Running command: {}\n'.format(' '.join(cmdLst)))
     # If check is true, and the process exits with a non-zero exit code,
     # a CalledProcessError exception will be raised. Attributes of that
     # exception hold the arguments, the exit code, and stdout and stderr
     # if they were captured.
    error = False
    try:
        result = sp.run(
            cmdLst,
            capture_output = True,
            text           = True,
            shell          = False,
            check          = True,
        )
        return error, result.stdout.strip(), result.stderr.strip()
    except sp.CalledProcessError as e:
        error = True
        return error, e.stderr.strip(),      e.stderr.strip()
#############################################################################

def runCommandTst():
    #cmdLst = [ 'git', 'ls-files' ]
    cmdLst = [ 'cmd', '/c', 'dir' ]
    err, stdOut, stdErr = runCommand(cmdLst)
    print( 'err = \n', err, '\nstdout = \n', stdOut, '\nstderr = \n',stdErr )
    return err, stdOut, stdErr
    #################################
def getAllTrackedFs():
    allTrackedFiles = []
    cmdLst = [ 'git', 'ls-files' ]
    err, stdOut,stdErr = runCommand(cmdLst)
    if not err:
        stdOutLines = stdOut.split('\n')
        allTrackedFiles = [line.split()[0] for line in stdOutLines]
    return err, stdOut, stdErr, allTrackedFiles
    #################################
def getChangedTrackedFs():
    changedTrackedFiles = []
    cmdLst = [ 'git', 'status', '--porcelain' ]
    err, stdOut,stdErr = runCommand(cmdLst)
    if not err:
        stdOutLines = stdOut.split('\n')
        changedTrackedFiles = \
            [line.split()[1] for line in stdOutLines if line.split()[0]=='M']
    return err, stdOut, stdErr, changedTrackedFiles
    #################################
def getUntrackedFs():
    untrackedFiles = []
    cmdLst = [ 'git', 'status', '--porcelain' ]
    err, stdOut,stdErr = runCommand(cmdLst)
    if not err:
        stdOutLines = stdOut.split('\n')
        untrackedFiles = \
            [line.split()[1] for line in stdOutLines if line.split()[0]=='??']
    return err, stdOut, stdErr, untrackedFiles
    #################################
def getExpectedUntrackedFs():
    err, stdOut, stdErr = False, '', ''
    expectedUntrackedFiles   = \
        [ 'cfg.cfg',   'cfg.py',    'client.py',   'gui.py',
          'fileIO.py', 'server.py', 'swUpdate.py', 'utils.py' ]
    return err, stdOut, stdErr, expectedUntrackedFiles
    #################################
def getUnexpectedUntrackedFs( untracked, expectedUntracked ):
    err, stdOut, stdErr = False, '', ''
    unexpectedUntrackedFiles = list(set(untracked) - set(expectedUntracked))
    return err, stdOut, stdErr, unexpectedUntrackedFiles
#############################################################################

def getFileLstDict():
    fDict = {
        'trackedFs'            : 
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':getAllTrackedFs         },

        'changedTrackedFs'     :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':getChangedTrackedFs     },

        'untrackedFs'          :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':getUntrackedFs          },

        'expectedUntrackedFs'  :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':getExpectedUntrackedFs  },

        'unexpectedUntrackedFs':
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':getUnexpectedUntrackedFs},

        'trackedPyFs'          :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':None                    },

        'changedTrackedPyFs'   :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':[], 'len':None,
        'func':None                    },
    }

    for k,v in fDict.items():
        if k in ['unexpectedUntrackedFs', 'trackedPyFs', 'changedTrackedPyFs']:
            continue
        s,o,e,l = v['func']()
        v['sts' ] = s
        v['stdO'] = o
        v['stdE'] = e
        v['fLst'] = l

    k = 'unexpectedUntrackedFs'
    s,o,e,l = fDict[k]['func'](fDict['untrackedFs'       ]['fLst'],
                              fDict['expectedUntrackedFs']['fLst'])
    fDict[k]['sts' ] = s
    fDict[k]['stdO'] = o
    fDict[k]['stdE'] = e
    fDict[k]['fLst'] = l

    fDict['trackedPyFs']['fLst']        = \
        [x for x in fDict['trackedFs'][       'fLst'] if x.endswith('.py')]
    fDict['changedTrackedPyFs']['fLst'] = \
        [x for x in fDict['changedTrackedFs']['fLst'] if x.endswith('.py')]

    for k,v in fDict.items():
        v['len'] = len(v['fLst'])
    return fDict
#############################################################################

def printFileLstDict(inFileListDict, pEn):
    #pp.pprint(inFileListDict)
    printOrder = [
        'trackedFs',    'trackedPyFs',         'changedTrackedPyFs',
        'untrackedFs',  'expectedUntrackedFs', 'changedTrackedFs',
        'unexpectedUntrackedFs'
    ]
    groupSize = 2  if pEn else 3
    width     = 50 if pEn else 25

    for el in printOrder:
        print( '\n   {} (len  = {}) = '.format(el, inFileListDict[el]['len']))
        if el == 'trackedFs' and not pEn:
            print( '   Not printed.  Use /p cmd line arg.')
            continue
        #pp.pprint(inFileListDict[el]['fLst'])
        d2FileList = mapTo2D( inFileListDict[el]['fLst'], groupSize )
        pStr = ''
        for group in d2FileList:
            pStr = [ '{}{}'.format((width-len(x))*' ',x) for x in group ]
            [print(x,end = '') for x in pStr] # pylint: disable=W0106
            print()
#############################################################################

def exitOnErrorsInFileLstDict(inFileListDict):
    print()
    doExit = False
    for k,v in inFileListDict.items():
        if v['sts']:
            print( ' {:23} error = {}'.format(k, v['sts']))
            erMsgLines = v['stdE'].split('\n')
            for errLine in  erMsgLines:
                print('     {}'.format(errLine))
            print()
            doExit = True
    if doExit:
        print( ' Exiting, RE: Error.\n' )
        sys.exit()
#############################################################################

def printStdOutOrStdErr( hasError, stdOut, stdErr ):

    if hasError:
        print( '   error = {}'.format(hasError))
        msgLines = stdErr.split('\n')
    else:
        msgLines = stdOut.split('\n')

    for theLine in  msgLines:
        print('     {}'.format(theLine))
    print()

    if hasError:
        print( ' Exiting, RE: Error.\n' )
        sys.exit()
#############################################################################


if __name__ == '__main__':

    #runCommandTst()
    #tstMoveOrCopyFiles()
    #sys.exit()

    arguments  = sys.argv
    scriptName = arguments[0]
    userArgs   = arguments[1:]
    prnEn      = (len(userArgs) > 0 and '/p' in userArgs)

    print( '\n Building Paths' )
    spiClockDir   = Path( r'C:\01-home\14-python\gitTrackedCode\spiClock' )
    sprinkler2Dir = Path( r'C:\01-home\14-python\gitTrackedCode\sprinkler2' )
    sharedDir     = Path( r'C:\01-home\14-python\gitTrackedCode\sharedClientServerCode' )
    #printPathInfo(spiClockDir,sprinkler2Dir,sharedDir)
    #########################################

    print( '\n Getting changed and untracked files.' )
    fLstDict = getFileLstDict()
    printFileLstDict( fLstDict, prnEn )
    exitOnErrorsInFileLstDict( fLstDict )
    #########################################

    if fLstDict['unexpectedUntrackedFs']['len'] > 0:
        print( '\n unexpected/untracked files present.')
        print( '   Continuing will not add them.')
        print( '   Add from cmd line like this <git add fName>')
        goOn = input( ' Continue (y/n)? -> ' )
        if goOn != 'y':
            sys.exit()

    if fLstDict['changedTrackedFs']['len'] == 0:
        print( ' No tracked/changed files present.' )
        print( ' Continuing will bump rev and thus cmdVectors.py will change.' )
        goOn = input( ' Continue (y/n)? -> ' )
        if goOn != 'y':
            sys.exit()
    #########################################

    print( '\n Getting curr/new Version Number and Date' )
    fileWithVerNumInIt = 'cmdVectors.py' # pylint: disable=C0103

    if fileWithVerNumInIt not in fLstDict['changedTrackedFs']['fLst']:
        print( '   Adding {} to changedTrackedFs'.format(fileWithVerNumInIt))
        fLstDict['changedTrackedFs']['fLst'].append('cmdVectors.py')
        fLstDict['changedTrackedFs']['len'] = fLstDict['changedTrackedFs']['len'] + 1

    curVerStr, pcntChanged, newVerStr = \
    getVerNums( fileWithVerNumInIt,
                fLstDict['changedTrackedPyFs']['len'],
                fLstDict['trackedPyFs']['len']
    )
    date = dt.datetime.now().strftime( '%d-%b-%Y' )
    print('   Percent of tracked .py files chanhged = {}%'.format(pcntChanged))
    print('   Old/New Version Numbers = {}/{}'.format(curVerStr, newVerStr))

    if pcntChanged == -1:
        print( '\n   Error getting ver num (divide by zero).\n')
    if pcntChanged == -2:
        print( '\n   Error getting ver num (file not found).\n')
    if pcntChanged == -3:
        print( '\n   Error getting ver num (search string not found).\n')
    if pcntChanged < 0:
        print( ' Exiting, RE: Error.\n' )
        sys.exit()
    #########################################

    print( '\n Updating app Version and Date in {}'.format(fileWithVerNumInIt) )
    fileToChangeVerNumIn = Path( fileWithVerNumInIt )
    text = fileToChangeVerNumIn.read_text(encoding='utf-8')
    new_text = re.sub( r"VER = .*", f"VER = '{newVerStr} - {date}'", text ) # pylint: disable=W1405
    fileToChangeVerNumIn.write_text(new_text, encoding='utf-8')
    #########################################

    print( '\n Adding appropriate files.' )
    cmdBaseLst = [ 'git', 'add' ]
    for f in fLstDict['changedTrackedFs']['fLst']:
        cmd = cmdBaseLst + [f]
        print('   {}'.format(' '.join(cmd)))
        hasErr, stdO, stdE = runCommand(cmd)
        printStdOutOrStdErr( hasErr, stdO, stdE )
    #########################################

    commitTxt = input( '\n Enter commit message -> ' )
    commitTxtWithQuotes = r'"{}"'.format(commitTxt)
    #########################################

    print( '\n Committing.' )
    cmd = [ 'git', 'commit', '--no-verify', '-m', commitTxtWithQuotes  ]
    print('   {}'.format(' '.join(cmd)))
    hasErr, stdO, stdE = runCommand(cmd)
    printStdOutOrStdErr( hasErr, stdO, stdE )
    #########################################

    #@rem only needed on first push
    #@rem git xx_branch -M main
    #@rem git remote add origin https://github.com/sgarrow/spiClock.git
    #########################################

    print( '\n Setting GitHub URL.' )
    cmd = ['git', 'remote', 'set-url', 'origin', 'https://github.com/sgarrow/spiClock.git']
    print('   {}'.format(' '.join(cmd)))
    hasErr, stdO, stdE = runCommand(cmd)
    printStdOutOrStdErr( hasErr, stdO, stdE )
    #########################################

    print( '\n Pushing to GitHub.' )
    cmd = ['git', 'push', '-u', 'origin', 'main'                                   ]
    print('   {}'.format(' '.join(cmd)))
    hasErr, stdO, stdE = runCommand(cmd)
    printStdOutOrStdErr( hasErr, stdO, stdE )
#############################################################################

    print( '\n Release Successful. \n' )
