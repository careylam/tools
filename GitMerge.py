import os
import argparse
import shutil
import filecmp


def isGitRepository(dir):
    path = os.path.abspath(dir)
    if path.find('.git') > 0 :
        return True
    else:
        return os.path.exists(os.path.join(path, '.git'))

parser = argparse.ArgumentParser(description='Git merger')
parser.add_argument('--newversion', type=str, help='The source directory of the new version')
parser.add_argument('--oldversion', type=str, help='The targtt directory of the old version')

args = parser.parse_args()

oldVersionRoot = os.path.abspath(args.oldversion)
newVersionRoot = os.path.abspath(args.newversion)

if not os.path.exists(oldVersionRoot):
    print ('Invalid target directory: ' + oldVersionRoot)
    quit()
if not os.path.exists(newVersionRoot):
    print ('Invalid source directory: ' + newVersionRoot)
    quit()
# if not isGitRepository(oldVersionRoot):
#     print ('Target directory: [' + args.target + '] is not a git repository')
#     quit()



os.chdir(oldVersionRoot)

print('-------- Start Scanning %s ----------' %oldVersionRoot)
# Scan through the old version to address the remove dir/files
for dir, subDirs, files in os.walk(oldVersionRoot):
#    print ('Found directory: %s' % dir)
    if dir != oldVersionRoot and not isGitRepository(dir):
        sourceDir = dir.replace(oldVersionRoot, newVersionRoot)
        if not os.path.exists(sourceDir):
            print ('Removing directory: %s' % dir)
            os.system('git rm -r ' + dir)
    for file in files:
        fullPath = os.path.join(dir, file)
#        print ('Found file: ' + fullPath)
        targetFile = fullPath.replace(oldVersionRoot, newVersionRoot)
        if fullPath.find('.git') == -1 and os.path.exists(fullPath) and not os.path.exists(targetFile):
            print ('Removing file: %s' % fullPath)
            os.system('git rm ' + fullPath)

# scan through the new version directory:
# 1. if the directory doesn't exist in the old, create directory so that we can copy file file over
# 2. if the file doesn't exist, git add the file.
# 3. if the file is different, then copy the file over and git add the file
# 4. otherwise skip
print('-------- Start Scanning %s ----------' %newVersionRoot)
for dir, subDirs, files in os.walk(newVersionRoot):
    #print ('Found directory: %s' %dir)
    targetDir = dir.replace(newVersionRoot, oldVersionRoot)
    if not os.path.exists(targetDir):
        os.mkdir(targetDir)
    for file in files:
        fullPath = os.path.join(dir, file)
        targetFile = fullPath.replace(newVersionRoot, oldVersionRoot)
        if not os.path.exists(targetFile):
            print ('Adding new file: %s' % targetFile)
            shutil.copyfile(fullPath, targetFile)
            os.system('git add %s' % targetFile)
        elif not filecmp.cmp(fullPath, targetFile, shallow=False):
            print ('Updating file: %s' % targetFile)
            shutil.copyfile(fullPath, targetFile)
            os.system('git add %s' % targetFile)

print('-------- Finished merging from ' + args.source + ' to ' + args.target)

