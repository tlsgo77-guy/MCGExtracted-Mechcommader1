import sys
sys.path.insert(0, 'pylib')
from capstone import *
data = open("D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE",'rb').read()
BASE=0x600000
start=int(sys.argv[1],0); end=int(sys.argv[2],0)
md = Cs(CS_ARCH_X86, CS_MODE_32)
# map string VAs to strings
import json, re
S = json.load(open('strings.json'))
smap = {BASE+o: s for o,s in S}
for i in md.disasm(data[start:end], BASE+start):
    note=''
    m = re.search(r'0x([0-9a-f]{6,8})\b', i.op_str)
    if m:
        v=int(m.group(1),16)
        if v in smap: note='  ; "'+smap[v][:70]+'"'
    print('%x  %-8s %s%s' % (i.address - BASE, i.mnemonic, i.op_str, note))
