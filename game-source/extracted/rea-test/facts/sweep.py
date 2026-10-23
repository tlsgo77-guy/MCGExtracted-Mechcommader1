import sys, re, collections, pickle
sys.path.insert(0,'pylib')
from capstone import *
data = open("D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE",'rb').read()
BASE=0x600000
TEXT_START=0x1000; TEXT_END=0x1000+0x178800   # up to vsize 0x1784a8 roughly
md=Cs(CS_ARCH_X86,CS_MODE_32)
vals={640,480,800,600,1024,768,639,479,799,599,1280,960,1023,767}
hits=collections.defaultdict(list)
pos=TEXT_START; n=0
pat=re.compile(r'0x[0-9a-f]+|(?<![\w])\d+(?![\w])')
while pos<TEXT_END:
    got=False
    for (a,sz,mn,ops) in md.disasm_lite(data[pos:TEXT_END], BASE+pos):
        got=True
        n+=1
        for m in pat.finditer(ops):
            try: v=int(m.group(),0)
            except: continue
            if v in vals: hits[v].append((a-BASE,mn,ops))
        if ('0x8fc]' in ops or '0x900]' in ops): hits['8fc/900'].append((a-BASE,mn,ops))
        pos=a-BASE+sz
    if not got or pos<TEXT_END and False: pos+=1
    else:
        # disasm stopped on bad byte: skip it
        pos+=1
print('instructions decoded', n)
for k,v in sorted(hits.items(), key=lambda kv: str(kv[0])): print(k, len(v))
pickle.dump(dict(hits), open('hits.pkl','wb'))
