import struct, sys
data = open("D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE",'rb').read()
BASE=0x600000
def xrefs(fileoff):
    va = BASE + fileoff  # valid for .rdata/.data/.text where rawptr==rva
    pat = struct.pack('<I', va)
    out=[]; i=0
    while True:
        i = data.find(pat, i)
        if i<0 or i>1785856: break
        out.append(i); i+=1
    return va,out
for a in sys.argv[1:]:
    fo = int(a,0)
    va,x = xrefs(fo)
    print(hex(fo), 'VA', hex(va), 'refs at file offsets:', [hex(i) for i in x])
    for i in x[:3]:
        lo=max(0,i-48); hi=i+24
        print('  ', hex(lo), data[lo:hi].hex(' '))
