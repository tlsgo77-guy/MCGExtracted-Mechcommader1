"""Keep in-mission unit names English in MCX.EXE (MechCommander Gold / DM 2.99.7.2601).

With the Korean overlay (patch_korean_io.py) every cLoadString() call returns the
Korean table entry, including the mech/vehicle names that BattleMech::init and
GroundVehicle::init store on the mission objects.  In-mission those names are
drawn by the vector `Font` class (font.bin) and the un-extended HUD fonts, which
have no Hangul, so the float-help label over a unit shows garbage.

Patch: a 54-byte copy of the original cLoadString() body that never consults the
Korean table and does not add languageOffset (plain LoadStringA of the base id),
placed in the unused .text tail at 0x7797C0, and the two name-loading call sites
(BattleMech::init @0x677264, GroundVehicle::init @0x66ACF5) retargeted to it.
Logistics screens keep the Korean names (their own call sites are untouched).
Image base 0x600000, .text file offset == VA-0x600000.

usage: python patch_korean_names_en.py <in MCX.EXE> <out MCX.EXE>
"""
import hashlib
import struct
import sys

BASE = 0x600000
CLOADSTRING = 0x75AA30
STUB_VA = 0x7797C0
SITES = (0x677264, 0x66ACF5)      # call cLoadString in BattleMech::init / GroundVehicle::init

# cLoadString(hInst, id, buf, size) without the languageOffset add and without
# the Korean-table lookup: zero-fill buf, LoadStringA(hInst, id, buf, size).
STUB = bytes.fromhex(
    "55"            # push ebp
    "89e5"          # mov ebp,esp
    "8b550c"        # mov edx,[ebp+0xc]        ; id (base, no offset)
    "53"            # push ebx
    "56"            # push esi
    "8b7514"        # mov esi,[ebp+0x14]       ; size
    "57"            # push edi
    "8b7d10"        # mov edi,[ebp+0x10]       ; buf
    "89f1"          # mov ecx,esi
    "89cb"          # mov ebx,ecx
    "31c0"          # xor eax,eax
    "56"            # push esi                 ; LoadStringA arg 4: size
    "c1e902"        # shr ecx,2
    "f3ab"          # rep stosd                ; zero-fill buf
    "89d9"          # mov ecx,ebx
    "83e103"        # and ecx,3
    "f3aa"          # rep stosb
    "8b4510"        # mov eax,[ebp+0x10]
    "8b4d08"        # mov ecx,[ebp+8]
    "50"            # push eax                 ; buf
    "52"            # push edx                 ; id
    "51"            # push ecx                 ; hInst
    "ff15c0a27700"  # call [__imp__LoadStringA]
    "5f"            # pop edi
    "5e"            # pop esi
    "5b"            # pop ebx
    "5d"            # pop ebp
    "c3"            # ret                      ; cdecl like the original
)
TEXT_VSIZE_MIN = STUB_VA + len(STUB) - BASE - 0x1000


def text_header(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    for i in range(nsec):
        hdr = pe + 24 + opt + 40 * i
        if data[hdr:hdr + 8].rstrip(b"\0") == b".text":
            return hdr
    raise SystemExit("no .text section")


def call_target(data, site):
    off = site - BASE
    if data[off] != 0xE8:
        return None
    return site + 5 + struct.unpack_from("<i", data, off + 1)[0]


def main(src, dst):
    data = bytearray(open(src, "rb").read())
    hdr = text_header(data)
    vsize, rva, rsize = struct.unpack_from("<III", data, hdr + 8)
    stub_off = STUB_VA - BASE
    cur = bytes(data[stub_off:stub_off + len(STUB)])
    targets = [call_target(data, s) for s in SITES]
    if cur == STUB and all(t == STUB_VA for t in targets) and vsize >= TEXT_VSIZE_MIN:
        print("already patched"); return 0
    if any(t != CLOADSTRING for t in targets):
        print("refusing: the name-loading call sites do not call cLoadString"); return 2
    if rva != 0x1000 or rsize < TEXT_VSIZE_MIN or (cur != STUB and cur.strip(b"\0")):
        print("refusing: .text tail at the stub address is not unused zero padding"); return 2
    data[stub_off:stub_off + len(STUB)] = STUB
    for site in SITES:
        struct.pack_into("<i", data, site - BASE + 1, STUB_VA - (site + 5))
    struct.pack_into("<I", data, hdr + 8, max(vsize, TEXT_VSIZE_MIN))
    open(dst, "wb").write(data)
    print(f"patched {dst}: in-mission unit names load English strings via stub @0x{STUB_VA:x}")
    print("sha256:", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))
