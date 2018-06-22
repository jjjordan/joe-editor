
import parser
import formatters

def main(files):
    parsed = []
    for fname in files:
        with open(fname, 'rb') as f:
            parsed.append(parser.parse(fname, f.read()))
    
    strings = {}
    for f in parsed:
        for p in f:
            if isinstance(p, parser.Replacement):
                s = formatters.get(p).formatIn(p.text)
                # options ...
                if s not in strings:
                    strings[s] = []
                strings[s].append(p)
    
    print("msgid \"\"")
    print("msgstr \"\"")
    
    outlist = list(strings.items())
    outlist.sort(key=potkey)
    
    for st, locs in outlist:
        print()
        print("#: " + ' '.join("%s:%d" % (loc.file, loc.line) for loc in locs))
        print("msgid " + repr(st))
        print("msgstr \"\"")
    
    return True

def potkey(x):
    xfirst = x[1][0]
    return (xfirst.file, xfirst.line, xfirst.col)

if __name__ == '__main__':
    import sys
    sys.exit(0 if main(sys.argv[1:]) else 1)
