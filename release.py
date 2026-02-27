from pathlib import Path
import subprocess as sp
import datetime   as dt
import pprint     as pp
import sys
import re
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

    #print( '\n Moving shared files.' )
    #                src,         dst,       fLst,        cmd
    #moveOrCopyFiles( spiClockDir, sharedDir, expectedUntrackedFs, 'Mov' )

    #print( '\n Copying shared files.' )
    #dsts = [ spiClockDir, sprinkler2Dir ]
    #for dstn in dsts:
    #    #                src,       dst,  fLst,                 cmd
    #    #moveOrCopyFiles( sharedDir, dstn, expectedUntrackedFs, 'Copy' )

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

def getVerNums( fName, numChanged, numTracked ):
    curVStr   = None
    newVStrwV = None
    try:
        pcntChange = int((numChanged/numTracked) * 100.0)
    except ZeroDivisionError:
        return curVStr, -1, newVStrwV

    fileWithVerNum = Path( fName )

    try:
        txt = fileWithVerNum.read_text().split('\n')
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
    print( '\n Running command: {}\n'.format(' '.join(cmdLst)))
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
    allTrackedFiles = []
    cmdLst = [ 'git', 'ls-files' ]
    cmdLst = [ 'cmd', '/c', 'dir' ]
    err, stdOut, stdErr = runCommand(cmdLst)
    if not err:
        stdOutLines = stdOut.split('\n')
    print( err, stdOut, stdErr )
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
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':getAllTrackedFs         },

        'changedTrackedFs'     :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':getChangedTrackedFs     },

        'untrackedFs'          :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':getUntrackedFs          },

        'expectedUntrackedFs'  :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':getExpectedUntrackedFs  },

        'unexpectedUntrackedFs':
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':getUnexpectedUntrackedFs},

        'trackedPyFs'          :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':None                    },

        'changedTrackedPyFs'   :
        { 'sts':None, 'stdO':None, 'stdE':None, 'fLst':None, 'len':None,
        'func':None                    },
    }

    for k in fDict:
        if k in ['unexpectedUntrackedFs', 'trackedPyFs', 'changedTrackedPyFs']:
            continue
        s,o,e,l = fDict[k]['func']()
        fDict[k]['sts' ] = s
        fDict[k]['stdO'] = o
        fDict[k]['stdE'] = e
        fDict[k]['fLst'] = l

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

    for k in fDict:
        fDict[k]['len'] = len(fDict[k]['fLst'])
    return fDict
#############################################################################

if __name__ == '__main__':

    #runCommandTst()

    print( '\n Building Paths' )
    spiClockDir   = Path( r'C:\01-home\14-python\gitTrackedCode\spiClock' )
    sprinkler2Dir = Path( r'C:\01-home\14-python\gitTrackedCode\sprinkler2' )
    sharedDir     = Path( r'C:\01-home\14-python\gitTrackedCode\sharedClientServerCode' )
    #printPathInfo(spiClockDir,sprinkler2Dir,sharedDir)
    #########################################
    print( '\n Getting changed and untracked files.' )
    fLstDict = getFileLstDict()
    pp.pprint(fLstDict)

    printOrder = [
        'trackedFs',        'trackedPyFs',
        'changedTrackedFs', 'changedTrackedPyFs',
        'untrackedFs',      'expectedUntrackedFs', 'unexpectedUntrackedFs'
    ]
    for k in printOrder:
        print( '\n {} (len  = {}) = \n'.format(k, fLstDict[k]['len']))
        pp.pprint(fLstDict[k]['fLst'])

    print()
    for k in printOrder:
        print( ' {:23} error = {}'.format(k, fLstDict[k]['sts']))
        if fLstDict[k]['sts']:
            errMsgLines = fLstDict[k]['stdE'].split('\n')
            for l in  errMsgLines:
                print('     {}'.format(l))
            print()

    #########################################
    if fLstDict['unexpectedUntrackedFs']['len'] > 0:
        print( '\n unexpected/untracked files present.')
        print( ' Continuing will not add them.')
        print( ' Add from cmd line <git add fName>')
        goOn = input( ' Continue (y/n)? -> ')
        if goOn != 'y':
            sys.exit()
        print(' Continuing')

    if fLstDict['changedTrackedFs']['len'] == 0:
        print( ' No tracked/changed files present.')
        print( ' Continuing will bump rev and thus cmdVectors.py will change.')
        goOn = input( ' Continue (y/n)? -> ')
        if goOn != 'y':
            sys.exit()
        print(' Continuing')
    #########################################
    print( '\n Getting curr/new version number and Date' )

    fileWithVerNumInIt = 'cmdVectors.py' # pylint: disable=C0103

    curVerStr, pcntChanged, newVerStr = \
    getVerNums( fileWithVerNumInIt,
                fLstDict['changedTrackedPyFs']['len'],
                fLstDict['trackedPyFs']['len']
    )
    date = dt.datetime.now().strftime( '%d-%b-%Y' )
    print(' Percent of tracked .py files chanhged = {}%'.format(pcntChanged))
    print(' Old/New Version Numbers = {}/{}'.format(curVerStr, newVerStr))

    if pcntChanged == -1:
        print( '\n Error getting ver num (divide by zero).\n')
    if pcntChanged == -2:
        print( '\n Error getting ver num (file not found).\n')
    if pcntChanged == -3:
        print( '\n Error getting ver num (search string not found).\n')
    if pcntChanged < 0:
        sys.exit()
    #########################################

    print( '\n Updating app ver and date in {}'.format(fileWithVerNumInIt) )
    fileToChangeVerNumIn = Path( fileWithVerNumInIt )
    text = fileToChangeVerNumIn.read_text()
    new_text = re.sub( r"VER = .*", f"VER = '{newVerStr} - {date}'", text )
    fileToChangeVerNumIn.write_text(new_text)
    #########################################

    print( '\n Adding, committing and pushing appropriate files.' )
    cmdBaseLst = [ 'git', 'add' ]
    for f in fLstDict['changedTrackedFs']:
        cmd = cmdBaseLst + [f]
        print(cmd)
        #stdOut,stdErr = runCommand(cmd)
        #print( 'stdOut = \n{}'.format(stdOut ))
        #print( 'stdErr = \n{}'.format(stdErr ))
    #cmd = [ 'git', 'commit', '*', '--no-verify', '-m', commitMsg  ]
    commitTxt = 'Testing new release script.' # pylint: disable=C0103
    cmd = [ 'git', 'commit', '*', '--no-verify', '-m', commitTxt  ]
    print(cmd)
    #@rem only needed on first push
    #@rem git branch -M main
    #@rem git remote add origin https://github.com/sgarrow/spiClock.git

    #git remote set-url origin https://github.com/sgarrow/spiClock.git
    #git push -u origin main
#############################################################################
