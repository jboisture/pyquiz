import sys, os, shutil

WIN32 = False
HAS_JUNCTION = False
if sys.platform[:3].lower() == "win":
    WIN32 = True

if WIN32:
    
    def _run(cmd):
        stdout = os.popen(cmd)
        output = stdout.read()
        stdout.close()
        return output
    
    # find the junction utility
    JUNCTION = "junction.exe"
    HAS_JUNCTION = False
    for path in os.environ['PATH'].split(';'):
        if os.path.exists(os.path.join(path, JUNCTION)):
            HAS_JUNCTION = True
            break
    
    def symlink(src, dest):
        cmd = "%s %s %s" % (JUNCTION, os.path.abspath(dest), os.path.abspath(src),)
        _run(cmd)

    def unlink(dest):
        cmd = "%s -d %s" % (JUNCTION, os.path.abspath(dest),)
        _run(cmd)

    def islink(dest):
        cmd = "%s %s" % (JUNCTION, os.path.abspath(dest),)
        output = _run(cmd)
        return "Substitute Name:" in output
        
        
    def rmtree(location, nonlinks=True):
        # Explicitly unlink all junction'd links
        for root, dirs, files in os.walk(location, topdown=False):
            for dir in dirs:
                path = os.path.join(root, dir)
                if islink(path):
                    unlink(path)
        # Then get rid of everything else
        if nonlinks:
            shutil.rmtree(location)
        
else:
    symlink = os.symlink
    islink = os.path.islink
    rmtree = shutil.rmtree
    unlink = None
