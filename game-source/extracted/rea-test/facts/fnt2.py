import struct
D="D:/DEV/MCGExtracted-Mechcommader1/MISC.FST/"
for n in ['BLUE.FNT','BLUE10.FNT','BLUE12.FNT']:
    b=open(D+n,'rb').read()
    print('=====',n,len(b))
    print('first 64 bytes:', b[:64].hex(' '))
    dw=struct.unpack_from('<16I',b,0)
    print('dwords:', [hex(x) if x>9 else x for x in dw])
    print('as text first 4:', repr(b[:4]))
