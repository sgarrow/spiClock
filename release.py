from pathlib import Path
import subprocess
import datetime
import re
#############################################################################

def runCommand( cmdLst ):
    print( '\n Running command: {}\n'.format(' '.join(cmdLst)))
    try:
        #check          = True,
        result = subprocess.run(
            cmdLst,
            capture_output = True,
            text           = True,
            shell          = False
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return (f' Command failed: {e.stderr.strip()}')
#############################################################################

def moveOrCopyFiles( src, dst, fLst, moveOrCopy ):
    if moveOrCopy not in ['Mov','Copy']:
        print(' moveOrCopy has invalid value.')
        return
    print('   {}ing from \n     {} to \n     {}.'.format( moveOrCopy, src, dst ))

    for f in fLst:
        s =  src / f  # A Path join. All 3 vars type Path.
        d =  dst / f  # A Path join. All 3 vars type Path.
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
                print( '       Moved {}.'.format(f))
            elif moveOrCopy == 'Copy':
                d.write_bytes(s.read_bytes())
                print( '       Copied {}.'.format( f))
#############################################################################

def getChangedAndUntrackedFiles():
    cmdLst = [ 'cmd', '/c', 'git', 'status', '--porcelain' ]
    stdOut,stdErr = runCommand(cmdLst)
    stdOutLines   = stdOut.split('\n')
    changedFiles  = [ line.split()[1]   for line in stdOutLines \
        if line.split()[0] == 'M']
    untrackedFiles = [ line.split()[1] for line in stdOutLines \
        if line.split()[0] == '??']
    return changedFiles, untrackedFiles
#############################################################################

def printPathInfo(spiClockD,sprinkler2D,sharedD):
    print()
    print( ' spiClockDir   = {}'.format(spiClockD   ))
    print( '   spiClockDir.name   = {}'.format(spiClockD.name   )) # The fname without any directory
    print( '   spiClockDir.stem   = {}'.format(spiClockD.stem   )) # The fname without the file extension
    print( '   spiClockDir.suffix = {}'.format(spiClockD.suffix )) # The file extension
    print( '   spiClockDir.anchor = {}'.format(spiClockD.anchor )) # The part of the path before the directories
    print( '   spiClockDir.parent = {}'.format(spiClockD.parent )) # Dir containing the file, or the parent dir if the path is a dir
    print( ' sprinkler2Dir = {}'.format(sprinkler2D ))
    print( ' sharedDir     = {}'.format(sharedD     ))
#############################################################################

if __name__ == '__main__':
    print( '\n Building Paths' )
    spiClockDir   = Path( r'C:\01-home\14-python\gitTrackedCode\spiClock' )
    sprinkler2Dir = Path( r'C:\01-home\14-python\gitTrackedCode\sprinkler2' )
    sharedDir     = Path( r'C:\01-home\14-python\gitTrackedCode\sharedClientServerCode' )
    sharedFiles   = [ 'cfg.cfg',   'cfg.py',    'client.py',   'gui.py',
                      'fileIO.py', 'server.py', 'swUpdate.py', 'utils.py' ]
    sharedFiles   = [ 'd1.txt', 'd2.txt', 'd3.txt' ]
    #printPathInfo(spiClockDir,sprinkler2Dir,sharedDir)
    #########################################
    print( '\n Setting variable values' )
    APPVER    = 'v1.6.45A'
    SRVVER    = 'v1.7.D'
    cDT       = datetime.datetime.now()
    DAT       = cDT.strftime( '%d-%b-%Y' )
    PRJ       = 'spiClock'
    commitTxt = 'Testing new release script.'
    commitMsg = r'"app={}. srv={}. {}."'.format( APPVER, SRVVER, commitTxt )
    parmMsg   = '{} {}'.format( PRJ, commitMsg )
    #########################################
    print( '\n Updating application version and date' )
    file = Path( 'cmdVectors.py' )
    text = file.read_text()
    new_text = re.sub( r"VER = .*", f"VER = '{APPVER} - {DAT}'", text )
    #file.write_text(new_text)
    #########################################
    #print( '\n Updating server version and date' )
    #file = Path( 'fileIO.py' )
    #text = file.read_text()
    #new_text = re.sub( r"VER = .*", f"VER = '{SRVVER} - {DAT}'", text )
    #file.write_text(new_text)
    #########################################
    print( '\n Moving shared files.' )
    src  = spiClockDir
    dst  = sharedDir
    fLst = sharedFiles
    moveOrCopyFiles( src, dst, fLst, 'Mov' )
    #########################################
    print( '\n Getting changed and untracked files.' )
    changedFs, untrackedFs =getChangedAndUntrackedFiles()
    print( 'changed   Files:\n{}'.format( changedFs   ))
    print( 'untracked Files:\n{}'.format( untrackedFs ))
    if len(untrackedFs) > 0:
        goOn = input( ' Untracked files are  present continue (y/n)? -> ')
        if goOn != 'y':
            exit()
    if len(changedFs) == 0:
        goOn = input( ' No changed files are present continue (y/n)? -> ')
        if goOn != 'y':
            exit()
    #########################################
    print( '\n Adding, committing and pushing appropriate files.' )
    cmdBaseLst = [ 'cmd', '/c', 'git', 'add' ]
    for f in changedFs:
        cmd = cmdBaseLst + [f]
        print(cmd)
        #stdOut,stdErr = runCommand(cmd)
        #print( 'stdOut = \n{}'.format(stdOut ))
        #print( 'stdErr = \n{}'.format(stdErr ))
    cmd = [ 'git', 'commit', '*', '--no-verify', '-m', commitMsg  ]
    print(cmd)
    #@rem only needed on first push
    #@rem git branch -M main
    #@rem git remote add origin https://github.com/sgarrow/spiClock.git
    # 
    #git remote set-url origin https://github.com/sgarrow/spiClock.git
    #git push -u origin main
#############################################################################

#echo Calling release.bat for shared code.
#cd C:\01-home\14-python\gitTrackedCode\sharedClientServerCode
#call release.bat "%parmMsg%"
#############################################################################

    print( '\n Copying shared files.' )
    src  = sharedDir
    dsts = [ spiClockDir, sprinkler2Dir ]
    fLst = sharedFiles
    for dst in dsts:
        moveOrCopyFiles( src, dst, fLst, 'Copy' )
        print()
#############################################################################
