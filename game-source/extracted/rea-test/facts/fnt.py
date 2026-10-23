import struct, os, glob
D="D:/DEV/MCGExtracted-Mechcommader1/MISC.FST/"
files = sorted(glob.glob(D+'*.FNT'))
print(len(files),'FNT files')
for f in files:
    b=open(f,'rb').read()
    print(os.path.basename(f), len(b), b[:16].hex(' '), repr(b[:4]))
