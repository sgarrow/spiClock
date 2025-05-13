import os
import zipfile
import platform
import requests
import clkCfg   as cc # For port, pwd.
#############################################################################
#############################################################################

def getLatestReleaseInfo(repoOwner, repoName):
    url = 'https://api.github.com/repos/{}/{}/releases/latest'.format(repoOwner,repoName)
    response = requests.get( url, timeout = 5 )

    if response.status_code == 200:
        latestRelease = response.json()
        return latestRelease['tag_name'], latestRelease['html_url']
    return None, None
#############################################################################

def downloadZip( dnldToPath, zipFileUrl ):

    fName = zipFileUrl.split('/')[-1]
    fullyQualifiedFname = dnldToPath + fName
    response = requests.get( zipFileUrl, timeout = 5 )

    if response.status_code == 200:
        with open(fullyQualifiedFname,'wb') as outFile:
            outFile.write(response.content)
        rspStr = ' Successfully downloaded {} to {}\n'.format(fName,dnldToPath)
        status = 'SUCCESS'
    else:
        rspStr = ' Failed to download {} to {}\n'.format(fName,dnldToPath)
        status = 'FAIL'

    return rspStr, status, fullyQualifiedFname
#############################################################################

def unzipFileTo(unzipToPath, fullyQualifiedFname):

    # Create and Unzip to the parent directory name contained in the zip file itself.
    #with zipfile.ZipFile(fullyQualifiedFname, 'r') as f:
    #    f.extractall( unzipToPath )

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
                    with open(targetPath, 'wb') as outfile, f.open(member) as source:
                        outfile.write(source.read())

    rspStr = ' Successfully extracted {} into {}'.\
             format(fullyQualifiedFname,unzipToPath)

    return rspStr
#############################################################################

def updateSw():

    rspStr    = ''
    repoOwner = 'sgarrow'
    repoName  = 'spiClock'
    osName    = platform.system()

    ###############
    if osName == 'Windows':
        dwnldToPath  = 'C:/01-home/temp/' # pylint: disable=C0103
        unzipToPath  = 'C:/01-home/temp/' # pylint: disable=C0103
    elif osName == 'Linux':
        dwnldToPath  = os.getcwd() + '/'
        unzipToPath  = os.getcwd() + '/'
    else:
        rspStr = 'Could not determine OS.'
        return [rspStr]
    ###############

    latestTag, releaseUrl = getLatestReleaseInfo( repoOwner, repoName )
    if latestTag:
        zipUrl= releaseUrl.replace('releases/tag','archive/refs/tags')+'.zip'

        rspStr += ' Latest release version:      {}\n'.format( latestTag  )
        rspStr += ' Latest release location:     {}\n'.format( releaseUrl )
        rspStr += ' Latest release zip location: {}\n'.format( zipUrl     )

        fRspStr, sts, fullQualifiedFname = downloadZip(dwnldToPath,zipUrl)
        rspStr += fRspStr

        if sts == 'SUCCESS':
            rspStr += unzipFileTo( unzipToPath, fullQualifiedFname )

    else:
        rspStr = ' Failed to fetch the latest release information from {}.'.\
                 format( 'github.com/' + repoOwner + '/' + repoName )

    return [rspStr]
#############################################################################

if __name__ == '__main__':
    ccDict = cc.getClkCfgDict()
    print(ccDict)
    mnRspStr = updateSw()
    print()
    print(mnRspStr[0])
    print()
