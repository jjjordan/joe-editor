import os
import os.path
import win32api
import win32con
import win32error
import win32file
import win32pipe
import win32process
import win32security

from commoncontroller import JoeControllerBase, tmpfiles

class JoeController(JoeControllerBase):
    def __init__(self, startup, proc, stdin, stdout):
        super().__init__(startup)
        self.proc = proc
        self.stdin = stdin
        self.stdout = stdout
    
    def _write(self, b):
        err, count = win32file.WriteFile(self.stdin, b)
        if err != 0:
            return -1
        else:
            return count
    
    def _readData(self):
        err, data = win32file.ReadFile(self.stdout, 1024)
        if err != 0 and err != win32error.ERROR_MORE_DATA:
            # Error during read.
            return -1
        self.stream.feed(result)
        return len(result)
    
    def close(self):
        self.wait()
        win32file.CloseHandle(self.stdin)
        win32file.CloseHandle(self.stdout)
        self.stdin = self.stdout = None
    
    def _select(self, timeout):
        # TODO
        pass
    
    def wait(self):
        # TODO
        pass
    
    def getExitCode(self):
        pass
    
    def checkProcess(self):
        pass
    
    def kill(self, code=9):
        pass

class FileLocations(object):
    def __init__(self, tmpfiles):
        self.tmpfiles = tmpfiles
    
    def joerc(self, personality='joe'):
        """Gets the location of ~HOME/.joerc for this platform"""
        return os.path.join(self.tmpfiles.home, 'JoeEditor\\conf\\%src' % personality)
    
    @property
    def syntaxdir(self):
        return os.path.join(self.tmpfiles.home, 'JoeEditor\\syntax')
    
    @property
    def colorsdir(self):
        return os.path.join(self.tmpfiles.home, 'JoeEditor\\colors')

def startJoe(args=None):
    """Starts JOE, returns a handle to the controller"""
    
    # Find testjoe.exe (for now...)
    joeexe = r"C:\Users\JJ\Documents\src\joewin-hg\windows\bin\x86\Debug\testjoe.exe"
    
    if args is None:
        args = StartupArgs()
    
    # Setup pipes
    pipeSAttrs = win32security.SECURITY_ATTRIBUTES()
    pipeSAttrs.bInheritHandle = 1

    stdinR, stdinW = win32pipe.CreatePipe(pipeSAttrs, 0)
    stdoutR, stdoutW = win32pipe.CreatePipe(pipeSAttrs, 0)
    
    # For those that we'll use, duplicate uninheritable pipes
    def dupclose(p):
        mypid = win32api.GetCurrentProcess()
        result = win32api.DuplicateHandle(mypid, p, mypid, 0, 0, win32con.DUPLICATE_SAME_ACCESS)
        win32file.CloseHandle(p)
        return result
    
    stdinW = dupclose(stdinW)
    stdoutR = dupclose(stdoutR)
    
    # Input to CreateProcess
    si = win32process.STARTUPINFO()
    si.hStdInput = stdinR
    si.hStdOutput = stdoutW
    si.hStdError = stdoutW
    si.wShowWindow = 0
    si.dwFlags = win32process.STARTF_USESTDHANDLES | win32process.STARTF_USESHOWWINDOW
    
    # Set up environment
    myenv = {
        'JOETEST_HOME': tmpfiles.homedir,
        'JOETEST_PERSONALITY': args.personality,
    }
    
    env = {}
    env.update(os.environ)
    env.update(myenv)
    env.update(args.env)
    
    # Invoke CreateProcess...
    creation = win32process.CREATE_NEW_CONSOLE # | win32process.CREATE_NEW_PROCESS_GROUP
    hproc, hthread, pid, dwTid = win32process.CreateProcess(
        test_joe,	# Application name
        cmdline,	# Cmdline
        None,		# Process attributes
        None,		# Thread attributes
        1,		# Inherit handles
        creation,	# Creation flags
        env,		# Environment
        cwd,		# Current working directory
        si)		# STARTUPINFO
    
    # Close handles we don't need
    for h in (hthread, stdinR, stdoutW):
        win32file.CloseHandle(h)
    
    return JoeController(args, hproc, stdinW, stdoutR)
