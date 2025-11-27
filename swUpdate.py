import platform
import zipfile
import os
import requests
import cfg
#############################################################################
#############################################################################

def getLatestReleaseInfo(repoOwner, repoName):

    url = 'https://api.github.com/repos/{}/{}/releases/latest'.\
        format(repoOwner,repoName)

    response = requests.get( url, timeout = 5 )
    if response.status_code == 200:
        latestRelease = response.json()
        return latestRelease['tag_name'], latestRelease['html_url']
    return None, None
#############################################################################

def parseReleaseInfo(releaseInfo):
    latestTag  = releaseInfo[0]
    releaseUrl = releaseInfo[1]
    if latestTag:
        zipUrl = releaseUrl.replace('releases/tag','archive/refs/tags')+'.zip'
    else:
        zipUrl = None
    return latestTag,releaseUrl,zipUrl
#############################################################################

def getPaths():
    osName     = platform.system()
    if osName == 'Windows':
        dwnldToPath  = 'C:/01-home/temp/' # pylint: disable=C0103
        unzipToPath  = 'C:/01-home/temp/' # pylint: disable=C0103
    elif osName == 'Linux':
        dwnldToPath  = os.getcwd() + '/'
        unzipToPath  = os.getcwd() + '/'
    else:
        dwnldToPath  = None
        unzipToPath  = None
    return dwnldToPath, unzipToPath
#############################################################################

def downloadZip( dnldToPath, zipFileUrl ):
    fName = zipFileUrl.split('/')[-1]
    fullyQualifiedFname = dnldToPath + fName
    response = requests.get( zipFileUrl, timeout = 5 )
    status = 'FAIL'
    if response.status_code == 200:
        with open(fullyQualifiedFname,'wb') as outFile:
            outFile.write(response.content)
        status = 'SUCCESS'
    return status, fullyQualifiedFname
#############################################################################

def unzipFileTo(unzipToPath, fullyQualifiedFname):
    rspStr = ''
    # Unzip directly into the specified directory.
    with zipfile.ZipFile(fullyQualifiedFname, 'r') as f:
        # Get the name of the top-level folder in the zip
        topLevelFolder = f.namelist()[0].split('/')[0]
        for member in f.infolist():
            # Remove the top-level folder from the path
            memberPath = member.filename
            if memberPath.startswith(topLevelFolder + '/'):
                relativePath = memberPath[len(topLevelFolder)+1:]
            else:
                relativePath = memberPath
            if relativePath:  # skip the top-level folder itself
                targetPath = os.path.join(unzipToPath, relativePath)
                if member.is_dir():
                    os.makedirs(targetPath, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(targetPath), exist_ok=True)
                    if targetPath.split('/')[-1] == 'cfg.cfg':
                        rspStr += '     Skipping {}\n'.format(targetPath)
                    else:
                        with open(targetPath, 'wb') as outfile, f.open(member) as source:
                            rspStr += '     Writing  {}\n'.format(targetPath)
                            outfile.write(source.read())
    return rspStr
#############################################################################

def compareVerNums( swVerLst, repoVerLst ):
    # 0: equal. 1: SW Bigger. 2: Repo Bigger

    if len(swVerLst) != 3 or len(repoVerLst) != 3: return 3

    if swVerLst == repoVerLst:      return 0

    if swVerLst[0] > repoVerLst[0]: return 1
    if swVerLst[0] < repoVerLst[0]: return 2

    # swVerLst[0] == repoVerLst[0]: 
    if swVerLst[1] > repoVerLst[1]: return 1
    if swVerLst[1] < repoVerLst[1]: return 2

    # swVerLst[1] == repoVerLst[1]: 
    if swVerLst[2] > repoVerLst[2]: return 1
    if swVerLst[2] < repoVerLst[2]: return 2

    return 3 # Should never get here,
#############################################################################

if __name__ == '__main__':

    def getVer():
        VER = ' v1.6.12 - 24-Nov-2025'
        return [VER]

    #verND        = cv.getVer()
    verND         = getVer()
    verNDSplit    = verND[0].split('-')
    swVerAsLst    = [ x.strip() for x in verNDSplit[0].split('.') ]
    swVerAsLst[0] = swVerAsLst[0][1:]
    swVerAsIntLst = [int(x) for x in swVerAsLst]
    print('\n          SW  VER as list = {}'.format( swVerAsIntLst ))

    dwnldToPath,unzipToPath = getPaths()
    #print(' dwnldToPath, unzipToPath = {}, {}\n'.\
    #    format( dwnldToPath,unzipToPath ))

    mnRepoOwner = 'sgarrow'
    mnRepoNames = ['spiClock', 'sharedClientServerCode']
    mnRepoNames = ['spiClock']

    for ii, mnRepoName in enumerate(mnRepoNames):

        releaseInfo = getLatestReleaseInfo(mnRepoOwner,mnRepoName)
        #print(' Release Info {}  = {}'.format(ii,releaseInfo))

        tag,url,zipUrl = parseReleaseInfo(releaseInfo)

        if tag == None or url == None:
            print( '   Failed to get the latest release information from {}.\n'.\
                 format( 'github.com/' + mnRepoOwner + '/' + mnRepoName ))
            continue

        #print('   Parsed Release Info:')
        #print('     tag    = {}'.format( tag    ))
        #print('     url    = {}'.format( url    ))
        #print('     zipUrl = {}'.format( zipUrl ))
        #print()
        repoVerAsLst    = [ x.strip() for x in tag.split('.') ]
        repoVerAsLst[0] = repoVerAsLst[0][1:]
        repoVerAsIntLst = [int(x) for x in repoVerAsLst]
        print('\n        REPO  VER as list = {}'.format( repoVerAsIntLst ))

        # 0: equal. 1: SW Bigger. 2: Repo Bigger 
        rsp = compareVerNums( swVerAsLst, repoVerAsLst )
        myStrLst = [ 'same  as', 'older than', 'newer than', '??? than' ]
        print('Repo ver is {} running ver. '.format(myStrLst[rsp]))
        continue

        sts, fullQualifiedFname = downloadZip(dwnldToPath,zipUrl)
        if sts == 'FAIL':
            print('   Failed to download {} to {}\n'.\
                format(zipUrl.split('/')[-1],dwnldToPath))
            continue
        print('   Successfully downloaded {} to {}\n'.\
            format(zipUrl.split('/')[-1],dwnldToPath))

        if sts == 'SUCCESS':
            rspStr = unzipFileTo( unzipToPath, fullQualifiedFname )
            print(rspStr)
            print(' Successfully extracted {} into {}'.
                     format(fullQualifiedFname,unzipToPath))

    print()
