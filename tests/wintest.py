import os
import os.path
import win32api
import win32con
import win32file
import win32pipe
import win32process
import win32security

# http://timgolden.me.uk/pywin32-docs/contents.html
# http://nullege.com/codes/show/src%40h%40o%40hortonworks-sandbox-HEAD%40desktop%40core%40ext-py%40Twisted%40twisted%40internet%40_dumbwin32proc.py/129/win32pipe.CreatePipe/python

pipeSAttrs = win32security.SECURITY_ATTRIBUTES()
pipeSAttrs.bInheritHandle = 1

stdoutR, stdoutW = win32pipe.CreatePipe(pipeSAttrs, 0)
stderrR, stderrW = win32pipe.CreatePipe(pipeSAttrs, 0)
stdinR, stdinW = win32pipe.CreatePipe(pipeSAttrs, 0)

# For those that we'll use, duplicate uninheritable pipes
def dupclose(p):
    mypid = win32api.GetCurrentProcess()
    result = win32api.DuplicateHandle(mypid, p, mypid, 0, 0, win32con.DUPLICATE_SAME_ACCESS)
    win32file.CloseHandle(p)
    return result

stdinW = dupclose(stdinW)
stdoutR = dupclose(stdoutR)
stderrR = dupclose(stderrR)

si = win32process.STARTUPINFO()
si.hStdInput = stdinR
si.hStdOutput = stdoutW
si.hStdError = stderrW
si.wShowWindow = 1
si.dwFlags = win32process.STARTF_USESTDHANDLES | win32process.STARTF_USESHOWWINDOW

test_joe = r"C:\Users\JJ\Documents\src\joewin-hg\windows\bin\x86\Debug\testjoe.exe"
#test_joe = r"C:\Windows\System32\cmd.exe"
cmdline = ""
cwd = os.path.dirname(test_joe)
print(cwd)
creation = win32process.CREATE_NEW_CONSOLE # | win32process.CREATE_NEW_PROCESS_GROUP
env = {}
env.update(os.environ)
env.update({
    "JOETEST_PERSONALITY": "joe",
})

proc, thread, pid, dwTid = win32process.CreateProcess(
    test_joe,	# Application name
    cmdline,	# Cmdline
    None,	# Process attributes
    None,	# Thread attributes
    1,		# Inherit handles
    creation,	# Creation flags
    env,	# Environment
    cwd,	# Current working directory
    si)		# STARTUPINFO

print("{} {} {} {}".format(*[repr(x) for x in (proc, thread, pid, dwTid)]))

for h in (thread, stdinR, stdoutW, stderrW):
    win32file.CloseHandle(h)

#first = True
#buf = win32file.AllocateReadBuffer(1024)

while True:
    #win32file.ReadFile(stdoutR, buf, None)
    err, st = win32file.ReadFile(stdoutR, 4096)
    if err != 0:
        break
#    if first:
#        first = False
#        win32file.WriteFile(stdinW, b"echo Hello world!\r\n")

    print(st)
