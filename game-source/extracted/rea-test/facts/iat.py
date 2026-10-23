import struct
src=open('imports.py').read().split("imp_rva, imp_sz")[0]
exec(src)
# IAT map
imp_rva, imp_sz = struct.unpack_from('<II', data, opt+96+8)
o=r2o(imp_rva); m={}
while True:
    ilt, ts, fc, nm, iat = struct.unpack_from('<IIIII', data, o)
    if nm==0: break
    dn=data[r2o(nm):data.index(b'\0',r2o(nm))].decode()
    t=r2o(ilt or iat); k=0
    while True:
        v=struct.unpack_from('<I',data,t)[0]
        if v==0: break
        if v&0x80000000: fn='ord%d'%(v&0xffff)
        else:
            fo=r2o(v); fn=data[fo+2:data.index(b'\0',fo+2)].decode()
        m[0x600000+iat+4*k]=dn+'!'+fn; k+=1; t+=4
    o+=20
import sys
for a in sys.argv[1:]:
    print(a, m.get(int(a,0)))
