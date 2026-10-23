import re, sys, json
EXE = "D:/DEV/MCGExtracted-Mechcommader1/game-source/extracted/MCX/MCX.EXE"
data = open(EXE,'rb').read()
LIM = 1785856
d = data[:LIM]
res = []
for m in re.finditer(rb'[\x20-\x7e]{5,}', d):
    res.append((m.start(), m.group().decode('ascii')))
json.dump(res, open('strings.json','w'))
print(len(res), 'strings; file size', len(data))
# PE sections
import struct
e_lfanew = struct.unpack_from('<I', data, 0x3c)[0]
nsec = struct.unpack_from('<H', data, e_lfanew+6)[0]
optsz = struct.unpack_from('<H', data, e_lfanew+20)[0]
print('machine', hex(struct.unpack_from('<H', data, e_lfanew+4)[0]), 'nsec', nsec)
off = e_lfanew+24+optsz
for i in range(nsec):
    name = data[off:off+8].rstrip(b'\0').decode()
    vs, va, rs, rp = struct.unpack_from('<IIII', data, off+8)
    print(name, 'vsize', hex(vs), 'va', hex(va), 'rawsize', hex(rs), 'rawptr', hex(rp), 'rawptr+size', rp+rs)
    off += 40
