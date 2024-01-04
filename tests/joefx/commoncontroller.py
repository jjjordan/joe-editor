import atexit
import collections
import os
import pyte
import pyte.graphics
import shutil
import tempfile
import time
from . import keys, exceptions

coord = collections.namedtuple('coord', ['X', 'Y'])

class JoeControllerBase(object):
    """Controller class for JOE program.  Manages child process and sends/receives interaction.  Nothing specific to JOE here, really"""
    def __init__(self, startup):
        self.term = pyte.Screen(startup.columns, startup.lines)
        self.stream = pyte.ByteStream()
        self.stream.attach(self.term)
        
        self.timeout = 1

    def expect(self, func):
        """Waits for data from the child process and runs func until it returns true or a timeout has elapsed"""
        
        if not self.checkProcess():
            raise exceptions.ProcessExitedException
        
        if func(): return True
        
        timeout = self.timeout
        deadline = time.time() + timeout
        
        while timeout > 0:
            if not self._select(timeout):
                # Timeout expired.
                return False
            
            timeout = deadline - time.time()
            res = self._readData()
            if res <= 0:
                raise exceptions.ProcessExitedException
            
            if func():
                return True
        
        # Timeout expired.
        return False

    def flushin(self):
        """Reads all pending input and processes through the terminal emulator"""
        if self.fd is None: return
        while True:
            if self._select(0):
                if self._readData() <= 0:
                    return
            else:
                return
    
    def write(self, b):
        """Writes specified data (string or bytes) to the process"""
        self.flushin()
        if hasattr(b, 'encode'):
            return self._write(b.encode('utf-8'))
        else:
            return self._write(b)
    
    def writectl(self, ctlstr):
        """Writes specified control sequences to the process"""
        return self.write(keys.toctl(ctlstr))

    def readLine(self, line, col, length):
        """Reads the text found at the specified screen location"""
        def getChar(y, x):
            if len(self.term.buffer) <= y: return ''
            if len(self.term.buffer[y]) <= x: return ''
            return self.term.buffer[y][x].data
        
        return ''.join(getChar(line, i + col) for i in range(length))
    
    def checkText(self, line, col, text):
        """Checks whether the text at the specified position matches the input"""
        
        return self.readLine(line, col, len(text)) == text

    def resize(self, width, height):
        """Resizes terminal"""
        self.flushin()
        self.term.resize(height, width)
        self._resize(width, height)

    @property
    def screen(self):
        """Returns contents of screen as a string"""
        return '\n'.join([self.readLine(i, 0, self.term.columns) for i in range(self.term.lines)])
    
    def prettyScreen(self):
        """Returns stylized (ANSI-escaped) contents of screen"""
        # Build translation tables real quick
        fgcolors = {v: k for k, v in pyte.graphics.FG.items()}
        bgcolors = {v: k for k, v in pyte.graphics.BG.items()}
        modes_on = {v[1:]: k for k, v in pyte.graphics.TEXT.items() if v.startswith('+')}
        modes_off = {v[1:]: k for k, v in pyte.graphics.TEXT.items() if v.startswith('-')}
        
        result = []
        attrs = {'fg': 'default', 'bg': 'default', 'bold': False, 'italics': False, 'underscore': False, 'reverse': False, 'strikethrough': False}
        for y in range(len(self.term.buffer)):
            line = self.term.buffer[y]
            for x in range(len(line)):
                char = line[x]
                codes = []
                for key in list(attrs.keys()):
                    newvalue = getattr(char, key)
                    if attrs[key] != newvalue:
                        if key in modes_on:
                            codes.append(modes_on[key] if newvalue else modes_off[key])
                        elif key == 'fg':
                            codes.append(fgcolors[newvalue])
                        elif key == 'bg':
                            codes.append(bgcolors[newvalue])
                        attrs[key] = newvalue
                
                # Override if on cursor location
                if x == self.term.cursor.x and y == self.term.cursor.y:
                    result.append("\033[0m\033[32;42;7;1m")
                    attrs = {'fg': '-', 'bg': '-', 'bold': True, 'italics': False, 'underscore': False, 'reverse': True, 'strikethrough': False}
                elif len(codes) > 0:
                    result.append("\033[" + ";".join(map(str, codes)) + "m")
                
                result.append(char.data)
            result.append("\n")
        
        # Reset modes before leaving.
        result.append("\033[0;39;49m")
        return ''.join(result)
    
    @property
    def cursor(self):
        """Returns cursor position"""
        return coord(self.term.cursor.x, self.term.cursor.y)
    
    @property
    def size(self):
        """Returns size of terminal"""
        return coord(self.term.columns, self.term.lines)

class StartupArgs(object):
    """Startup arguments for JOE"""
    def __init__(self):
        self.args = ()
        self.env = {}
        self.lines = 25
        self.columns = 80

class TempFiles:
    """Temporary file manager.  Creates temp location and ensures it's deleted at exit"""
    def __init__(self):
        self.tmp = None
    
    def _cleanup(self):
        if os.path.exists(self.tmp):
            # Make sure we're not in it.
            os.chdir('/')
            shutil.rmtree(self.tmp)
    
    def getDir(self, path):
        """Get or create temporary directory 'path', under root temporary directory"""
        if self.tmp is None:
            self.tmp = tempfile.mkdtemp()
            atexit.register(self._cleanup)
        
        fullpath = os.path.join(self.tmp, path)
        if not os.path.exists(fullpath):
            os.makedirs(fullpath)
        return fullpath
    
    @property
    def homedir(self):
        """Temporary directory pointed to by HOME"""
        return self.getDir("home")
    
    @property
    def workdir(self):
        """Temporary directory where JOE will be started"""
        return self.getDir("work")

tmpfiles = TempFiles
