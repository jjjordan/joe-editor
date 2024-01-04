import array
import fcntl
import os
import pty
import select
import signal
import termios

from commoncontroller import JoeControllerBase, tmpfiles
from . import exceptions

class JoeController(JoeControllerBase):
    def __init__(self, startup, pid, fd):
        super().__init__(startup)
        self.pid = pid
        self.fd = fd
        self.exited = None
    
    def checkProcess(self):
        """Checks whether the process is still running"""
        if self.exited is not None:
            return True
        
        result = os.waitpid(self.pid, os.WNOHANG)
        if result == (0, 0):
            return True
        else:
            self.exited = result
            return False
    
    def getExitCode(self):
        """Get exit code of program, if it has exited"""
        if self.exited is not None:
            result = self.exited
        else:
            result = os.waitpid(self.pid, os.WNOHANG)
        
        if result != (0, 0):
            self.exited = result
            return result[1] >> 8
        else:
            return None
    
    def kill(self, code=9):
        """Kills the child process with the specified signal"""
        os.kill(self.pid, code)
    
    def close(self):
        """Waits for process to exit and close down open handles"""
        self.wait()
        os.close(self.fd)
        self.fd = None
    
    def wait(self):
        """Waits for child process to exit or timeout to expire"""
        
        if self.exited is not None:
            return self.exited[1] >> 8
        
        def ontimeout(signum, frame):
            raise exceptions.TimeoutException()
        
        signal.signal(signal.SIGALRM, ontimeout)
        signal.alarm(int(self.timeout))
        try:
            result = os.waitpid(self.pid, 0)
        except exceptions.TimeoutException:
            return None
        signal.alarm(0)
        self.exited = result
        return result[1] >> 8

    def _resize(self, width, height):
        buf = array.array('h', [height, width, 0, 0])
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, buf)

    def _select(self, timeout):
        rready, wready, xready = select.select([self.fd], [], [self.fd], timeout)
        return len(rready) > 0
    
    def _write(self, b):
        return os.write(self.fd, b)
    
    def _readData(self):
        """Reads bytes from program and sends them to the terminal"""
        try:
            result = os.read(self.fd, 1024)
        except OSError:
            return -1
        self.stream.feed(result)
        return len(result)

class FileLocations(object):
    def joerc(self, personality='joe'):
        """Gets the location of ~HOME/.joerc for this platform"""
        return os.path.join(tmpfiles.home, '.%src' % personality)
    
    @property
    def syntaxdir(self):
        return os.path.join(tmpfiles.home, '.joe/syntax')
    
    @property
    def colorsdir(self):
        return os.path.join(tmpfiles.home, '.joe/colors')

def startJoe(args=None):
    """Starts JOE in a pty, returns a handle to controller"""
    joeexe = os.path.join(os.path.dirname(__file__), '../../joe/joe')
    if not joeexe.startswith('/'):
        joeexepath = os.path.join(.getcwd(), joeexe)
    else:
        joeexepath = joeexe
    
    if args is None:
        args = StartupArgs()
    
    env = {}
    #env.update(os.environ)
    
    env['HOME'] = tmpfiles.homedir
    env['LINES'] = str(args.lines)
    env['COLUMNS'] = str(args.columns)
    env['TERM'] = 'ansi'
    env['LANG'] = 'en_US.UTF-8'
    env['SHELL'] = os.getenv('SHELL', '/bin/sh')
    
    env.update(args.env)
    
    cmdline = ('joe',) + args.args
    
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(tmpfiles.workdir)
        os.execve(joeexepath, cmdline, env)
        os._exit(1)
    else:
        buf = array.array('h', [args.lines, args.columns, 0, 0])
        fcntl.ioctl(fd, termios.TIOCSWINSZ, buf)
        return JoeController(joeexepath, cmdline, env, args, pid, fd)
