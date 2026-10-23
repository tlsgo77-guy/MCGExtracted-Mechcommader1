import json, re, sys
S = json.load(open('strings.json'))
pat = re.compile(sys.argv[1], re.I)
lim = int(sys.argv[2]) if len(sys.argv)>2 else 400
n=0
for off,s in S:
    if pat.search(s):
        n+=1
        if n<=lim: print(hex(off), off, repr(s[:160]))
print('TOTAL', n)
