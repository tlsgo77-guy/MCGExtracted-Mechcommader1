"""Fix the stretched view box on the radar (tactical map) in MCX.EXE (MechCommander Gold / DM 2.99.7.2601).

Symptom: at 1280x1024 the red box that marks the main view on the radar keeps its
width but turns into two long vertical lines running off the radar.

Cause: TacticalMap::display() (box code at 0x74339b) inverse-projects the main
view's corners (0,0) and (w,h) with Camera::inverseProject().  That function only
works for screen points inside the projected terrain block; for any other point it
silently uses a distance of 1e7 (a point 10 million pixels below the screen).  The
radar rotates the world by 45 degrees, so the error cancels on the radar x axis and
doubles on the y axis.  At 640x480 the corners always hit terrain; at higher
resolutions they often do not.

Patch: replace the two corner projections with a jump to new code in the unused
tail of .text (VA 0x7794b0).  It inverse-projects only the screen centre and
derives the corners with the engine's own linear screen->world map
(world.x += dy + dx/sqrt3, world.y += -dy + dx/sqrt3, doubled at the 45px zoom),
then rejoins the original code at the worldToTacMap calls.  If even the centre
misses the terrain the box is skipped for that frame.  The .text VirtualSize is
enlarged so the loader maps the new code.  Image base 0x600000, .text file
offset == VA-0x600000.

usage: python patch_radar_viewbox.py <in MCX.EXE> <out MCX.EXE>
"""
import hashlib
import struct
import sys

BASE = 0x600000
HOOK_VA = 0x74339B           # mov edi,[eax+0xdc] in TacticalMap::display
HOOK_END = 0x7433F3          # lea edx,[ebp-0x24] -> worldToTacMap(A)
CAVE_VA = 0x7794B0
TEXT_VSIZE_ORIG = 0x1784A8

ORIG_HOOK = bytes.fromhex(
    "8bb8dc000000"  # mov edi,[eax+0xdc]       ; view object
    "c745cc00000000"  # mov [ebp-0x34],0       ; corner A = (0,0)
    "c745c800000000"  # mov [ebp-0x38],0
    "8bcf"          # mov ecx,edi
    "8b07"          # mov eax,[edi]
    "ff500c"        # call [eax+0xc]           ; width
    "8945f4"        # mov [ebp-0xc],eax
    "8bcf"          # mov ecx,edi
    "db45f4"        # fild [ebp-0xc]
    "d95dbc"        # fstp [ebp-0x44]          ; corner B.x = w
    "8b17"          # mov edx,[edi]
    "ff5210"        # call [edx+0x10]          ; height
    "8945f4"        # mov [ebp-0xc],eax
    "8b45f0"        # mov eax,[ebp-0x10]
    "db45f4"        # fild [ebp-0xc]
    "8d4ddc"        # lea ecx,[ebp-0x24]
    "8d55c8"        # lea edx,[ebp-0x38]
    "51"            # push ecx
    "52"            # push edx
    "d95dc0"        # fstp [ebp-0x40]          ; corner B.y = h
    "8b7804"        # mov edi,[eax+4]          ; camera
    "8bcf"          # mov ecx,edi
    "e8ecb3f6ff"    # call Camera::inverseProject   ; A -> world [ebp-0x24]
    "8d45d0"        # lea eax,[ebp-0x30]
    "8d4dbc"        # lea ecx,[ebp-0x44]
    "50"            # push eax
    "51"            # push ecx
    "8bcf"          # mov ecx,edi
    "e8ddb3f6ff"    # call Camera::inverseProject   ; B -> world [ebp-0x30]
)
NEW_HOOK = b"\xe9" + struct.pack("<i", CAVE_VA - (HOOK_VA + 5)) + b"\x90" * (len(ORIG_HOOK) - 5)

# in: eax = Camera*, esi = TacticalMap*, ebx = 0; out at 0x7433f3: edi = Camera*,
# A = world [ebp-0x24..-0x1c], B = world [ebp-0x30..-0x28], FPU stack empty
CAVE = bytes.fromhex(
    "89c7"          # mov edi,eax              ; camera (0x74340d reads [edi+0xd0])
    "8b8fdc000000"  # mov ecx,[edi+0xdc]       ; view object
    "8b01"          # mov eax,[ecx]
    "ff500c"        # call [eax+0xc]           ; width
    "d1f8"          # sar eax,1
    "8945bc"        # mov [ebp-0x44],eax       ; hw
    "8b8fdc000000"  # mov ecx,[edi+0xdc]
    "8b11"          # mov edx,[ecx]
    "ff5210"        # call [edx+0x10]          ; height
    "d1f8"          # sar eax,1
    "8945c0"        # mov [ebp-0x40],eax       ; hh
    "db45bc"        # fild [ebp-0x44]
    "d95dc8"        # fstp [ebp-0x38]          ; screen centre = (hw,hh)
    "db45c0"        # fild [ebp-0x40]
    "d95dcc"        # fstp [ebp-0x34]
    "8d4ddc"        # lea ecx,[ebp-0x24]
    "8d55c8"        # lea edx,[ebp-0x38]
    "51"            # push ecx
    "52"            # push edx
    "89f9"          # mov ecx,edi
    "e8e352f3ff"    # call Camera::inverseProject   ; centre -> C at [ebp-0x24]
    "d945dc"        # fld [ebp-0x24]
    "d9e1"          # fabs
    "d81d74957700"  # fcomp [LIMIT]
    "dfe0"          # fnstsw ax
    "80e445"        # and ah,0x45
    "80fc01"        # cmp ah,1                 ; |C.x| < 1e6 (ordered)?
    "7569"          # jne skip
    "d945e0"        # fld [ebp-0x20]
    "d9e1"          # fabs
    "d81d74957700"  # fcomp [LIMIT]
    "dfe0"          # fnstsw ax
    "80e445"        # and ah,0x45
    "80fc01"        # cmp ah,1                 ; |C.y| < 1e6?
    "7554"          # jne skip
    "db45bc"        # fild [ebp-0x44]
    "d80d70957700"  # fmul [INV_SQRT3]         ; q = hw/sqrt3
    "db45c0"        # fild [ebp-0x40]          ; hh, q
    "83bfe000000001"  # cmp [edi+0xe0],1       ; 45px zoom doubles screen offsets
    "7508"          # jne nozoom
    "d8c0"          # fadd st0,st0
    "d9c9"          # fxch st1
    "d8c0"          # fadd st0,st0
    "d9c9"          # fxch st1
    "d9c1"          # nozoom: fld st1          ; q, hh, q
    "d8c1"          # fadd st0,st1             ; Dx = q+hh
    "d9ca"          # fxch st2                 ; q, hh, Dx
    "d8e1"          # fsub st0,st1             ; Dy = q-hh
    "ddd9"          # fstp st1                 ; Dy, Dx
    "d945e0"        # fld [ebp-0x20]           ; Cy
    "d9c0"          # fld st0
    "d8c2"          # fadd st0,st2
    "d95dd4"        # fstp [ebp-0x2c]          ; B.y = Cy+Dy
    "d8e1"          # fsub st0,st1
    "d95de0"        # fstp [ebp-0x20]          ; A.y = Cy-Dy
    "ddd8"          # fstp st0                 ; Dx
    "d945dc"        # fld [ebp-0x24]           ; Cx
    "d9c0"          # fld st0
    "d8c2"          # fadd st0,st2
    "d95dd0"        # fstp [ebp-0x30]          ; B.x = Cx+Dx
    "d8e1"          # fsub st0,st1
    "d95ddc"        # fstp [ebp-0x24]          ; A.x = Cx-Dx
    "ddd8"          # fstp st0                 ; FPU stack empty
    "8b45e4"        # mov eax,[ebp-0x1c]
    "8945d8"        # mov [ebp-0x28],eax       ; B.z = C.z (A.z already is)
    "e9889efcff"    # jmp 0x7433f3             ; worldToTacMap(A), (B), draw box
    "e9be9ffcff"    # skip: jmp 0x74352e       ; next terrain window
    "3acd133f"      # INV_SQRT3 @0x779570: 0.57735027f
    "00247449"      # LIMIT     @0x779574: 1.0e6f
)
TEXT_VSIZE_NEW = CAVE_VA + len(CAVE) - BASE - 0x1000
assert CAVE_VA + len(CAVE) == 0x779578, hex(CAVE_VA + len(CAVE))
assert len(NEW_HOOK) == len(ORIG_HOOK) == HOOK_END - HOOK_VA


def text_header(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    for i in range(nsec):
        hdr = pe + 24 + opt + 40 * i
        if data[hdr:hdr + 8].rstrip(b"\0") == b".text":
            return hdr
    raise SystemExit("no .text section")


def main(src, dst):
    data = bytearray(open(src, "rb").read())
    hdr = text_header(data)
    vsize, rva, rsize = struct.unpack_from("<III", data, hdr + 8)
    hook_off, cave_off = HOOK_VA - BASE, CAVE_VA - BASE
    hook, cave = bytes(data[hook_off:hook_off + len(ORIG_HOOK)]), bytes(data[cave_off:cave_off + len(CAVE)])
    if hook == NEW_HOOK and cave == CAVE and vsize == TEXT_VSIZE_NEW:
        print("already patched"); return 0
    if hook != ORIG_HOOK:
        print("refusing: bytes at the hook site do not match the original TacticalMap::display code"); return 2
    if vsize != TEXT_VSIZE_ORIG or rva != 0x1000 or rsize < TEXT_VSIZE_NEW or cave.strip(b"\0"):
        print("refusing: .text tail is not the expected unused zero padding"); return 2
    data[hook_off:hook_off + len(NEW_HOOK)] = NEW_HOOK
    data[cave_off:cave_off + len(CAVE)] = CAVE
    struct.pack_into("<I", data, hdr + 8, TEXT_VSIZE_NEW)
    open(dst, "wb").write(data)
    print(f"patched {dst}: radar view box now derived from the screen centre (code at 0x{CAVE_VA:x})")
    print("sha256:", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))
