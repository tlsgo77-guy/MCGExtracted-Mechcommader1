import struct, sys
data = open("D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE",'rb').read()
BASE=0x600000
t=int(sys.argv[1],0)  # file offset of target func
for i in range(0x1000, 0x179000-5):
    if data[i]==0xe8:
        rel=struct.unpack_from('<i',data,i+1)[0]
        if (i+5+rel)==t: print('call at',hex(i))
pat=struct.pack('<I',BASE+t)
i=0
while True:
    i=data.find(pat,i)
    if i<0 or i>0x1aa000: break
    print('abs ref at',hex(i), data[i-3:i+5].hex(' ')); i+=1
