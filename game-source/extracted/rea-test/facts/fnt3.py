import struct
D="D:/DEV/MCGExtracted-Mechcommader1/MISC.FST/"
for n in ['BLUE.FNT','BLUE10.FNT','BLUE12.FNT']:
    b=open(D+n,'rb').read()
    ver,cnt,h,x=struct.unpack_from('<4I',b,0)
    tbl=struct.unpack_from('<%dI'%cnt,b,16)
    # count consecutive strictly increasing
    k=1
    while k<len(tbl) and tbl[k]>tbl[k-1]: k+=1
    print('=====',n,'size',len(b),'hdr',ver,cnt,h,x,'| table bytes end at',16+4*cnt)
    print(' consecutive increasing dwords from table[0]:',k,'of',cnt,' first',hex(tbl[0]),'last increasing',hex(tbl[k-1]))
    diffs=[tbl[i+1]-tbl[i] for i in range(k-1)]
    from collections import Counter
    print(' stride histogram:',Counter(diffs).most_common(6))
    print(' non-increasing at index',k, 'values',[hex(v) for v in tbl[k-2:k+4]])
    print(' distinct values',len(set(tbl)),'zeros',sum(1 for v in tbl if v==0))
    # glyph record at tbl[0]
    o=tbl[0]
    print(' first glyph rec 32 bytes:',b[o:o+32].hex(' '))
    print(' last glyph rec region start',hex(tbl[k-1]),b[tbl[k-1]:tbl[k-1]+16].hex(' '), '; file ends at',hex(len(b)))
