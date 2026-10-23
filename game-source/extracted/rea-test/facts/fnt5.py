import struct
D="D:/DEV/MCGExtracted-Mechcommader1/MISC.FST/"
def load(n):
    b=open(D+n,'rb').read()
    ver,cnt,h,x=struct.unpack_from('<4I',b,0)
    tbl=struct.unpack_from('<%dI'%cnt,b,16)
    return b,cnt,h,tbl
def glyph(b,h,tbl,i):
    o=tbl[i]; w=struct.unpack_from('<I',b,o)[0]
    return w,b[o+4:o+4+w*h]
def art(b,h,tbl,i):
    w,px=glyph(b,h,tbl,i)
    return '\n'.join(''.join('#' if px[r*w+c]!=0xff else '.' for c in range(w)) for r in range(h))
for n in ['BLUE.FNT','BLUE10.FNT','BLUE12.FNT']:
    b,cnt,h,tbl=load(n)
    print('=====',n,'cnt',cnt)
    nonempty=[i for i in range(cnt) if any(p!=0xff for p in glyph(b,h,tbl,i)[1])]
    # ranges of nonempty indices
    rng=[];s=None;prev=None
    for i in nonempty:
        if s is None: s=i
        elif i!=prev+1: rng.append((s,prev)); s=i
        prev=i
    rng.append((s,prev))
    print(' nonblank glyph index ranges:',rng,' total nonblank',len(nonempty))
    if n=='BLUE.FNT':
        for i in (65,97,0xe9,0xc4):
            print(' idx',i,ascii(chr(i)),'width',glyph(b,h,tbl,i)[0]); print(art(b,h,tbl,i))
