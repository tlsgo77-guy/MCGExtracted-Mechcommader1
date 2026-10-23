import json, sys
S = json.load(open('strings.json'))
c = int(sys.argv[1],0); w = int(sys.argv[2]) if len(sys.argv)>2 else 200
for off,s in S:
    if c-w <= off <= c+w: print(hex(off), repr(s[:140]))
