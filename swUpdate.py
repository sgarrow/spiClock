import os
import zipfile
import requests
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
        print(' Successfully downloaded {} to {}\n'.format( fName, dnldToPath ))

        print( ' dnldToPath          = {}'.format(dnldToPath         ))
        print( ' zipFileUrl          = {}'.format(zipFileUrl         ))
        print( ' fName               = {}'.format(fName              )) 
        print( ' fullyQualifiedFname = {}'.format(fullyQualifiedFname)) 
        print()

        status = 'SUCCESS'
    else:
        print(' Failed to download {} to {}'.format( fName, dnldToPath ))
        status = 'FAIL'

    return status, fName, fullyQualifiedFname
#############################################################################

def unzipFileTo( unzipToPath, fullyQualifiedFname ):
    with zipfile.ZipFile(fullyQualifiedFname, 'r') as f:
        f.extractall( unzipToPath )
    print( ' Extraction complete!' )
#############################################################################

def unzipFileTo2(unzipToPath, fullyQualifiedFname):
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
    print(' Extraction complete!')
#############################################################################

def updateSw():

    runningOn = 'rpi'
    #runningOn = 'pc'

    REPOOWNER = 'sgarrow'
    REPONAME  = 'spiClock'

    latestTag, releaseUrl = getLatestReleaseInfo( REPOOWNER, REPONAME )

    if latestTag:

        cwd = os.getcwd()
        zipUrl   = releaseUrl.replace('releases/tag', 'archive/refs/tags') + '.zip'
        targzUrl = releaseUrl.replace('releases/tag', 'archive/refs/tags') + '.tar.gz'
        print()
        print( ' Current Working directory:      {}'.format( cwd        ))
        print()
        print( ' Latest release version:         {}'.format( latestTag  ))
        print( ' Latest release location:        {}'.format( releaseUrl ))
        print( ' Latest release zip location:    {}'.format( zipUrl     ))
        print( ' Latest release tar.gz location: {}'.format( targzUrl   ))
        print()

        if runningOn == 'pc':
            dwnldToPath  = 'C:/01-home/temp/' # pylint: disable=C0103
            unzipToPath  = 'C:/01-home/temp/' # pylint: disable=C0103
        elif runningOn == 'rpi':
            dwnldToPath  = cwd + '/'
            unzipToPath  = cwd + '/' 
        else:
            return ['error']

        sts,dwnldedFname,fullQualifiedFname = downloadZip(dwnldToPath,zipUrl)
        print(' ** ', sts, ' ** ', dwnldedFname,' ** ', fullQualifiedFname, ' ** ')
        
        if sts == 'SUCCESS':
            #unzipFileTo( mnUnzipToPath, fullQualifiedFname )
            unzipFileTo2( unzipToPath, fullQualifiedFname )

    else:
        print('Failed to fetch the latest release information.')

    return ['done']
#############################################################################
if __name__ == '__main__':
    updateSw()
