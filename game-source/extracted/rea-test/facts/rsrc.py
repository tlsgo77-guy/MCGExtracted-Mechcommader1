import struct
src=open('imports.py').read().split("imp_rva, imp_sz")[0]
exec(src)
rs_rva = [s for s in secs if s[0]=='.rsrc'][0][1]
rs_off = [s for s in secs if s[0]=='.rsrc'][0][3]
TYPES={1:'CURSOR',2:'BITMAP',3:'ICON',4:'MENU',5:'DIALOG',6:'STRING',9:'ACCEL',10:'RCDATA',12:'GROUP_CURSOR',14:'GROUP_ICON',16:'VERSION'}
def entries(off):
    n_named, n_id = struct.unpack_from('<HH', data, off+12)
    out=[]
    for i in range(n_named+n_id):
        nm, so = struct.unpack_from('<II', data, off+16+8*i)
        out.append((nm, so))
    return out
res=[]
for tnm,tso in entries(rs_off):
    t = TYPES.get(tnm, tnm)
    for inm,iso in entries(rs_off + (tso & 0x7fffffff)):
        for lnm,lso in entries(rs_off + (iso & 0x7fffffff)):
            dro, sz, cp, _ = struct.unpack_from('<IIII', data, rs_off+lso)
            res.append((t,inm,lnm,r2o(dro),sz))
from collections import Counter
print(Counter(r[0] for r in res))
print('languages (LANGID) used:', sorted(set(r[2] for r in res)))
strs=[r for r in res if r[0]=='STRING']
print('string blocks:', len(strs), 'ids', [r[1] for r in strs][:60])
total=0; samples=[]
for t,bid,lang,fo,sz in strs:
    p=fo
    for k in range(16):
        L=struct.unpack_from('<H',data,p)[0]; p+=2
        if L:
            txt=data[p:p+2*L].decode('utf-16le','replace'); total+=1
            if len(samples)<25: samples.append(((bid-1)*16+k, lang, txt[:90]))
        p+=2*L
print('nonempty strings in STRING table:', total)
for s in samples: print(s)
print([ (r[0],r[1],r[2],r[4]) for r in res if r[0] in ('DIALOG','MENU','VERSION','RCDATA')])
ids=[]
for t,bid,lang,fo,sz in strs:
    p=fo
    for k in range(16):
        L=struct.unpack_from('<H',data,p)[0]; p+=2
        if L: ids.append(((bid-1)*16+k, data[p:p+2*L].decode('utf-16le','replace')))
        p+=2*L
print('min id', ids[0][0], 'max id', ids[-1][0])
import collections
print('id ranges (blocks of 100):', sorted(collections.Counter(i//100 for i,_ in ids).items()))
for i,s in ids:
    if i in (100,101,200,300,400,500,600,700,800,900,1000,1100,1200) or i>1240: print(i, repr(s[:100]))
nonascii=[(i,s) for i,s in ids if any(ord(c)>127 for c in s)]
print('strings with non-ASCII chars:', len(nonascii), nonascii[:5])
print('---- ids 890..915')
for i,s in ids:
    if 890<=i<=915: print(i, repr(s[:100]))
print('count ids >=1000:', sum(1 for i,_ in ids if i>=1000), ' count ids <1000:', sum(1 for i,_ in ids if i<1000))
print('---- VERSION resource utf16 strings')
for t,bid,lang,fo,sz in res:
    if t=='VERSION':
        blob=data[fo:fo+sz]
        import re
        for m in re.finditer(rb'(?:[\x20-\x7e]\x00){3,}', blob):
            print(m.group().decode('utf-16le'))
