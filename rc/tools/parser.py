
class Replacement(object):
    def __init__(self, file, line, col, text):
        self.line = line
        self.col = col
        self.file = file
        self.text = text
        self.options = {}
    
    def __str__(self):
        return "Replacement [%d, %d]\n\t%s\n\t\"%s\"" % (self.line, self.col, repr(self.options), self.text.decode('utf-8'))

class Text(object):
    def __init__(self, filename, line, col):
        self.text = bytearray()
        self.filename = filename
        self.line = line
        self.col = col
    
    def __str__(self):
        return "Text [%d, %d]\n\t%s" % (self.line, self.col, repr(self.text))

def parse(filename, s):
    line = 1
    col = 1
    nest = 0
    repbegin = -1
    repline = -1
    repcol = -1
    last = Text(filename, 1, 1)
    result = []
    
    for i in range(len(s)):
        c = s[i:i+1]

        if c == b'$':
            if s[i+1:i+2] == b'{' and nest == 0:
                nest = 1
                repbegin = i
                repline = line
                repcol = col
                result.append(last)
                last = None
        if c == b'{':
            if nest > 0 and repbegin < i-1:
                nest += 1
        
        if nest == 0:
            if last is None:
                last = Text(filename, line, col)
            last.text.append(s[i])

        if c == b'}':
            if nest > 0:
                nest -= 1
                if nest == 0:
                    result.append(parseFormat(filename, repline, repcol, s[repbegin:i+1]))

        if c == b'\t':
            col = (col + 8) & 0xfff8
        elif c == b'\n':
            col = 1
            line += 1
        else:
            col += 1
    
    result.append(last)
    return result

def parseFormat(file, line, col, data):
    #print("Parsing: " + data.decode('ascii'))
    if b'|' in data:
        x = data.find(b'|')
        result = Replacement(file, line, col, data[x+1:-1])
        optxt = data[2:x].decode('utf-8')
        
        i = 0
        while i < len(optxt):
            co = optxt.find(':', i)
            cm = optxt.find(',', i)
            if co < 0:
                # No colon remaining -- if name not empty, simply mark a flag and stop.
                name = optxt[i:].strip()
                if name:
                    result.options[name] = True
                break
            if cm > -1 and cm < co:
                # There's a comma before the next colon, mark a flag.
                result.options[optxt[i:cm].strip()] = True
                i = cm + 1
                continue
            
            # Name extends to colon.
            name = optxt[i:co].strip()
            if optxt[co+1:co+2] == '"':
                # Quoted string, capture between quotes
                endq = optxt.find('"', co+2)
                result.options[name] = optxt[co+2:endq]
                
                cm = optxt.find(',', endq)
                if cm < 0:
                    break
                i = cm + 1
            else:
                # Unquoted value, capture to comma
                cm = optxt.find(',', co+1)
                if cm < 0:
                    result.options[name] = optxt[co+1:]
                    break
                else:
                    result.options[name] = optxt[co+1:cm]
                    i = cm + 1
        
        return result
    else:
        return Replacement(file, line, col, data[2:-1])

if __name__ == '__main__':
    import sys
    
    fname = 'test.in'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    
    with open(fname, 'rb') as f:
        result = parse(fname, f.read())
    
    for v in result:
        print(str(v))
