"""Add a bounds check to ScenarioMap::cellPassable() in MCX.EXE (MechCommander Gold / DM 2.99.7.2601).

Crash: Access violation at 0x006B9B20 (ScenarioMap::cellPassable +0x50) from
InterfaceObject::UpdateMouseState(). The mouse position is inverse-projected to a
world position and passed to cellPassable(), which indexes map[tileRow*width+tileCol]
without any bounds check. At resolutions above 640x480 the view can show area
outside the map, so the cursor can produce an out-of-range tile -> read fault.

Patch: rewrite the function tail (file 0xb9afe..0xb9b3f, 66 bytes incl. 13 NOP pad)
so that tileRow is checked against this->height (+4) and tileCol against
this->width (+8) exactly like the engine's own ScenarioMap::inBounds(); out of
range returns 0 (impassable).  Image base 0x600000, .text file offset == VA-0x600000.

usage: python patch_cellpassable.py <in MCX.EXE> <out MCX.EXE>
"""
import hashlib
import sys

BASE = 0x600000
FUNC_VA = 0x6B9AD0
PATCH_VA = 0x6B9AFE          # right after `call ScenarioMap::worldToMapPos`
ORIG_SHA256 = "bc9593b6744d92e341730f9ff22d9dbe56064a74145eee7c6bda4dda2c876f64"

ORIG_TAIL = bytes.fromhex(
    "8b45fc"        # mov eax,[ebp-4]
    "8b4df8"        # mov ecx,[ebp-8]
    "8d1441"        # lea edx,[ecx+eax*2]
    "03c2"          # add eax,edx
    "8b55f0"        # mov edx,[ebp-0x10]
    "d1e0"          # shl eax,1
    "8bc8"          # mov ecx,eax
    "8b4608"        # mov eax,[esi+8]
    "0faf45f4"      # imul eax,[ebp-0xc]
    "03c2"          # add eax,edx
    "8b16"          # mov edx,[esi]
    "be00400000"    # mov esi,0x4000
    "8b04c2"        # mov eax,[edx+eax*8]   <- faulting read
    "d3e6"          # shl esi,cl
    "83c10e"        # add ecx,0xe
    "23c6"          # and eax,esi
    "5e"            # pop esi
    "d3e8"          # shr eax,cl
    "8be5"          # mov esp,ebp
    "5d"            # pop ebp
    "c20c00"        # ret 0xc
    + "90" * 13     # padding
)

NEW_TAIL = bytes.fromhex(
    "8b45f4"        # mov eax,[ebp-0xc]      ; tileRow
    "3b4604"        # cmp eax,[esi+4]        ; this->height
    "732e"          # jae bad                ; (also catches negative)
    "8b55f0"        # mov edx,[ebp-0x10]     ; tileCol
    "3b5608"        # cmp edx,[esi+8]        ; this->width
    "7326"          # jae bad
    "0faf4608"      # imul eax,[esi+8]       ; row*width
    "03c2"          # add eax,edx            ; +col
    "8b16"          # mov edx,[esi]          ; map
    "8b04c2"        # mov eax,[edx+eax*8]    ; map[idx] (now in range)
    "8b4dfc"        # mov ecx,[ebp-4]
    "8d0c49"        # lea ecx,[ecx+ecx*2]    ; *3
    "034df8"        # add ecx,[ebp-8]
    "03c9"          # add ecx,ecx            ; *2  -> bit shift
    "ba00400000"    # mov edx,0x4000
    "d3e2"          # shl edx,cl
    "23c2"          # and eax,edx
    "83c10e"        # add ecx,0xe
    "d3e8"          # shr eax,cl
    "eb02"          # jmp done
    "33c0"          # bad: xor eax,eax
    "5e"            # done: pop esi
    "8be5"          # mov esp,ebp
    "5d"            # pop ebp
    "c20c00"        # ret 0xc
    + "90" * 3
)
assert len(ORIG_TAIL) == len(NEW_TAIL) == 66, (len(ORIG_TAIL), len(NEW_TAIL))


def main(src, dst):
    data = bytearray(open(src, "rb").read())
    sha = hashlib.sha256(data).hexdigest()
    if sha != ORIG_SHA256:
        print(f"warning: input sha256 {sha} differs from the known original {ORIG_SHA256}")
    off = PATCH_VA - BASE
    cur = bytes(data[off:off + 66])
    if cur == NEW_TAIL:
        print("already patched"); return 0
    if cur != ORIG_TAIL:
        print("refusing: bytes at the patch site do not match the original cellPassable tail"); return 2
    data[off:off + 66] = NEW_TAIL
    open(dst, "wb").write(data)
    print(f"patched {dst}: ScenarioMap::cellPassable @0x{FUNC_VA:x} now bounds-checks tileRow/tileCol")
    print("sha256:", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))
