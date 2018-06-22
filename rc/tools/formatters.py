
class Formatter(object):
    def formatIn(self, s):
        return s
    
    def formatOut(self, s, line, col):
        return s

class RawFormatter(Formatter):
    pass

class CenterFormatter(Formatter):
    pass

class SpaceWrapFormatter(Formatter):
    pass

class SpaceIndentFormatter(Formatter):
    pass

class TabWrapFormatter(Formatter):
    pass

class TrimAroundFormatter(Formatter):
    pass

def get(rplc):
    f = rplc.options.get('fmt', 'raw')
    if f == 'raw':
        return RawFormatter()
    elif f == 'spwrap':
        return SpaceWrapFormatter()
    elif f == 'splines':
        return SpaceIndentFormatter()
    elif f == 'tabwrap':
        return TabWrapFormatter()
    elif f == 'trimaround':
        return TrimAroundFormatter()
    elif f == 'center':
        return CenterFormatter()
    else:
        raise KeyError("No such formatter: " + f)
