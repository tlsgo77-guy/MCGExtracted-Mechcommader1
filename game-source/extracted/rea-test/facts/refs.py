import struct, sys
sys.path.insert(0,'pylib')
from capstone import *
data = open("D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE",'rb').read()
BASE=0x600000
va=int(sys.argv[1],0)
pat=struct.pack('<I',va)
i=0; hits=[]
while True:
    i=data.find(pat,i)
    if i<0 or i>0x179000: break   # .text only
    hits.append(i); i+=1
print('hits in .text:', len(hits))
md=Cs(CS_ARCH_X86,CS_MODE_32)
for h in hits:
    # disassemble starting a bit before; try several starts to sync
    best=None
    for back in range(1,12):
        s=h-back
        ins=list(md.disasm(data[s:s+16], BASE+s))
        if ins and ins[0].address-BASE+ins[0].size > h-0 and ins[0].address-BASE<=h-1:
            best=ins[0]; break
    if best: print(hex(h), '%x'%(best.address-BASE), best.mnemonic, best.op_str)
    else: print(hex(h),'??', data[h-4:h+8].hex(' '))
