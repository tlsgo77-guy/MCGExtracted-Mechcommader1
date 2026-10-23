import struct, glob, os
D="D:/DEV/MCGExtracted-Mechcommader1/MISC.FST/"
print('%-14s %6s %5s %5s %5s | %-9s %s' % ('file','size','cnt','h','dw3','recsOK','widths(min/max) pixel bytes: has0xFF')) 
for f in sorted(glob.glob(D+'*.FNT')):
    b=open(f,'rb').read()
    ver,cnt,h,x=struct.unpack_from('<4I',b,0)
    tbl=list(struct.unpack_from('<%dI'%cnt,b,16))
    ends=tbl[1:]+[len(b)]
    ok=0; ws=[]
    has_ff=False
    for o,e in zip(tbl,ends):
        w=struct.unpack_from('<I',b,o)[0]; ws.append(w)
        if e-o==4+w*h: ok+=1
        if 0xff in b[o+4:e]: has_ff=True
    print('%-14s %6d %5d %5d %5d | %d/%d   w %d..%d  FF:%s' % (os.path.basename(f),len(b),cnt,h,x,ok,cnt,min(ws),max(ws),has_ff))
