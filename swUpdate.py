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
        print(' Successfully downloaded {} to {}'.format( fName, dnldToPath ))
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
        top_level_folder = f.namelist()[0].split('/')[0]
        
        for member in f.infolist():
            # Remove the top-level folder from the path
            member_path = member.filename
            if member_path.startswith(top_level_folder + '/'):
                relative_path = member_path[len(top_level_folder)+1:]
            else:
                relative_path = member_path

            if relative_path:  # skip the top-level folder itself
                target_path = os.path.join(unzipToPath, relative_path)
                if member.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, 'wb') as outfile, f.open(member) as source:
                        outfile.write(source.read())
    print(' Extraction complete!')
#############################################################################

if __name__ == '__main__':

    REPOOWNER = 'sgarrow'
    REPONAME  = 'spiClock'

    latestTag, releaseUrl = getLatestReleaseInfo( REPOOWNER, REPONAME )

    if latestTag:

        zipUrl   = releaseUrl.replace('releases/tag', 'archive/refs/tags') + '.zip'
        targzUrl = releaseUrl.replace('releases/tag', 'archive/refs/tags') + '.tar.gz'
        print()
        print( ' Latest release version:         {}'.format( latestTag  ))
        print( ' Latest release location:        {}'.format( releaseUrl ))
        print( ' Latest release zip location:    {}'.format( zipUrl     ))
        print( ' Latest release tar.gz location: {}'.format( targzUrl   ))
        print()

        mnDwnldToPath  = 'C:/01-home/temp/' # Be sure to include ending / character.
        mnUnzipToPath  = 'C:/01-home/temp/' # Be sure to include ending / character.

        sts, dwnldedFname,fullQualifiedFname   = downloadZip( mnDwnldToPath, zipUrl )
        print(' ** ', sts, ' ** ', dwnldedFname,' ** ', fullQualifiedFname, ' ** ')

        if sts == 'SUCCESS':
            #unzipFileTo( mnUnzipToPath, fullQualifiedFname )
            unzipFileTo2( mnUnzipToPath, fullQualifiedFname )

    else:
        print('Failed to fetch the latest release information.')
#############################################################################
