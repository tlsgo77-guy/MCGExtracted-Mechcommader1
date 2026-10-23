import struct
data = open("D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE",'rb').read()
e = struct.unpack_from('<I', data, 0x3c)[0]
opt = e+24
nsec = struct.unpack_from('<H', data, e+6)[0]
optsz = struct.unpack_from('<H', data, e+20)[0]
secs=[]
off = e+24+optsz
for i in range(nsec):
    name = data[off:off+8].rstrip(b'\0').decode()
    vs, va, rs, rp = struct.unpack_from('<IIII', data, off+8)
    secs.append((name,va,vs,rp,rs)); off+=40
def r2o(rva):
    for n,va,vs,rp,rs in secs:
        if va<=rva<va+max(vs,rs): return rva-va+rp
    return None
imp_rva, imp_sz = struct.unpack_from('<II', data, opt+96+8)
print('import dir rva', hex(imp_rva), 'size', imp_sz)
o = r2o(imp_rva)
dlls=[]
while True:
    ilt, ts, fc, nm, iat = struct.unpack_from('<IIIII', data, o)
    if nm==0: break
    no = r2o(nm); name = data[no:data.index(b'\0',no)].decode()
    t = r2o(ilt or iat); funcs=[]
    while True:
        v = struct.unpack_from('<I', data, t)[0]
        if v==0: break
        if v & 0x80000000: funcs.append('ord%d'%(v&0xffff))
        else:
            fo = r2o(v); funcs.append(data[fo+2:data.index(b'\0',fo+2)].decode())
        t+=4
    dlls.append((name,funcs)); o+=20
for n,f in dlls:
    print('%-16s %3d funcs' % (n,len(f)), ', '.join(f[:12]) + (' ...' if len(f)>12 else ''))
print('DLL names in import table:', [n for n,_ in dlls])
# delay import?
di = struct.unpack_from('<II', data, opt+96+13*8); print('delay import dir', di)
# regex DLL names in [0,LIM)
import re
LIM=1785856
names = sorted(set(m.group().decode().lower() for m in re.finditer(rb'[A-Za-z0-9_]+\.dll', data[:LIM], re.I)))
print('regex .dll names:', names)
for want in [b'IDirectDraw', b'IDirect3D', b'DDSURFACEDESC', b'SetCooperativeLevel', b'SetDisplayMode', b'DirectDrawCreate', b'Direct3DCreate', b'DirectInputCreate', b'DirectSoundCreate', b'DirectPlayCreate', b'DirectPlayEnumerate']:
    i = data[:LIM].find(want)
    print(want.decode(), '->', hex(i) if i>=0 else 'not found', ('in section '+ [s[0] for s in secs if s[3]<=i<s[3]+s[4]][0]) if i>=0 else '')
