#!/usr/bin/env python3

def convert_key(keyname, s):
    ns = ''
    for c in s:
        ns += keyname[c]
    return ns

def read_cin_file(filename):
    keyname = {}
    with open(filename) as f:
        STATE_INIT = 0
        STATE_KEYNAME = 1
        STATE_CHARDEF = 2
        state = STATE_INIT
        for line in f:
            if line[0] == '#':
                continue
            e = line.split()
            if e[0] == '%keyname':
                if e[1] == 'begin':
                    state = STATE_KEYNAME
            elif e[0] == '%chardef':
                if e[1] == 'begin':
                    state = STATE_CHARDEF
            elif state == STATE_KEYNAME:
                keyname[e[0]] = e[1]
            elif state == STATE_CHARDEF:
                mapping = convert_key(keyname, e[0])
                print(e[1], mapping)

def main():
    filename = 'phone.cin'
    read_cin_file(filename)

if __name__ == '__main__':
    main()
