import sys
from commoncontroller import coord, StartupArgs, tmpfiles

if sys.platform == 'win32':
    from wincontroller import FileLocations, startJoe
else:
    from unixcontroller import FileLocations, startJoe

fileLocations = FileLocations()

__all__ = ["fileLocations", "tmpfiles", "startJoe"]
