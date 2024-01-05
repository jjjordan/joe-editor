#!/usr/bin/env python

def main(infile, outfile):
    with open(outfile, 'wb') as f:
        for title, data in readRecords(infile):
            print(title + ", ({} bytes)".format(len(data)), end='')
            f.write(data)
            f.flush()
            input()

def readRecords(fname):
    with open(fname, 'rb') as f:
        data = f.read()
    
    ptr = 0
    line = 1
    while ptr < len(data):
        # Find start of data
        col = data.find(b':', ptr)
        if col < 0: break
        
        # Get record
        title = "[{}] {}".format(line, data[ptr:col].decode('ascii'))
        
        nxt = findNextRecord(data, col)
        if nxt < 0: break
        
        # Grab bytes, remove extra linefeed
        recdata = data[col+1:nxt-1]

        yield title, recdata
        
        # Update line ..
        for i in range(ptr, nxt):
            if data[i] == '\n': line += 1
        
        ptr = nxt

def findNextRecord(data, start):
    for i in range(start, len(data)):
        if i > 3 and 42 == data[i] == data[i - 1] == data[i - 2] and data[i - 3] == 10:
            return i - 2
    return len(data)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: in-log out-file")
        sys.exit(2)
    main(*sys.argv[1:])
