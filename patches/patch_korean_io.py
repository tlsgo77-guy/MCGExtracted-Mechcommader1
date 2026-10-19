r"""Korean localization I/O hooks for MCX.EXE (MechCommander Gold / DM 2.99.7.2601).

Both hooks are active only in "Korean mode": the prefs.cfg value `l Language=`
is stored in the global languageOffset @0x80a86c by systemInit; non-zero means
Korean.  With Language=0 the game behaves exactly as before.

1. File overlay.  File::open() (0x645480) opens game data with relative paths
   such as `data\fonts\BLUE.FNT` or `data\missions\brf0101.txt`, first as a
   loose file (CreateFileA) and then from the .FST packs.  The hook at 0x645546
   (the read-only CreateFileA) first tries `lang\kor\` + path and, if that file
   exists, uses it; otherwise the original call runs unchanged.  Write/create
   opens (save games, logs), absolute paths and paths already under `lang\` are
   never redirected.  The alternate path is built in the function's own
   0x12c-byte local, which the original code only uses afterwards for the
   file-traffic log.

2. External string table.  cLoadString() (0x75aa30) is the single wrapper
   around LoadStringA for the 835 UI strings.  In Korean mode it lazily loads
   `lang\kor\strings.bin` (format: u32 'KSTR', u32 count, u32 ids[count]
   ascending, u32 offsets[count], NUL-terminated EUC-KR strings; built by
   tools/build_strings_bin.py), looks the base id up and copies at most size-1
   bytes.  Missing table or id falls back to LoadStringA with the base id, so
   untranslated strings stay English.  The table pointer and state live in the
   zero padding after the last .data symbol (0x80d680..0x80d68c; .data
   VirtualSize is raised to cover them).

Code goes to the unused tail of .text (0x779580..0x7797b2); the .text
VirtualSize is raised if needed.  Composable with patch_cellpassable.py and
patch_radar_viewbox.py (any order).  Image base 0x600000, .text file offset ==
VA-0x600000.

usage: python patch_korean_io.py <in MCX.EXE> <out MCX.EXE>
"""
import hashlib
import struct
import sys

BASE = 0x600000
FO_HOOK_VA = 0x645546        # File::open: push 3 ... call CreateFileA (read-only open)
LS_HOOK_VA = 0x75AA30        # cLoadString entry
CAVE_FO_VA = 0x779580
CAVE_LS_VA = 0x779650
DATA_GLOBALS_END = 0x80D690  # g_state 0x80d680, g_table 0x80d684, g_tmp 0x80d688

ORIG_FO_HOOK = bytes.fromhex(
    "6a03"          # push 3                   ; OPEN_EXISTING
    "53"            # push ebx                 ; 0 (security)
    "6a01"          # push 1                   ; FILE_SHARE_READ
    "50"            # push eax                 ; GENERIC_READ / READ|WRITE
    "57"            # push edi                 ; name
    "ff15c4a07700"  # call [CreateFileA]
)
NEW_FO_HOOK = b"\xe9" + struct.pack("<i", CAVE_FO_VA - (FO_HOOK_VA + 5)) + b"\x90" * 8

ORIG_LS = bytes.fromhex(
    "558bec8b550ca16ca8800053568b7514578b7d108bce8bd903d033c056c1e902f3ab"
    "8bcb83e103f3aa8b45108b4d08505251ff15c0a277005f5e5b5dc3909090"
)                    # whole original cLoadString (0x40 bytes incl. 3 NOP pad)
NEW_LS_HOOK = b"\xe9" + struct.pack("<i", CAVE_LS_VA - (LS_HOOK_VA + 5))

# in: eax = access flags, ebx = 0, esi = File*, edi = name; two CreateFileA args
# (0, FILE_ATTRIBUTE_NORMAL) already pushed.  ecx/edx are dead here.
CAVE_FO = bytes.fromhex(
    "833d6ca8800000"  # cmp [languageOffset],0
    "0f84a1000000"  # je orig
    "3d00000080"    # cmp eax,0x80000000       ; read-only open?
    "0f8596000000"  # jne orig
    "8a0f"          # mov cl,[edi]
    "80f95c"        # cmp cl,'\'
    "0f848b000000"  # je orig                  ; absolute path
    "80f92f"        # cmp cl,'/'
    "0f8482000000"  # je orig
    "807f013a"      # cmp byte [edi+1],':'
    "747c"          # je orig                  ; drive letter
    "50"            # push eax
    "6a05"          # push 5
    "6840967700"    # push "lang\"
    "57"            # push edi
    "e890f0ffff"    # call _strnicmp
    "83c40c"        # add esp,0xc
    "85c0"          # test eax,eax
    "58"            # pop eax
    "7466"          # je orig                  ; already under lang\
    "50"            # push eax
    "57"            # push edi
    "e84168feff"    # call _strlen
    "83c404"        # add esp,4
    "3d20010000"    # cmp eax,0x120            ; 9 + len + NUL must fit 0x12c
    "58"            # pop eax
    "7754"          # ja orig
    "8d95d4feffff"  # lea edx,[ebp-0x12c]
    "c7026c616e67"  # mov [edx],'lang'
    "c742045c6b6f72"  # mov [edx+4],'\kor'
    "c642085c"      # mov byte [edx+8],'\'
    "83c209"        # add edx,9
    "50"            # push eax
    "57"            # push edi
    "52"            # push edx
    "e82469feff"    # call _strcpy             ; "lang\kor\" + name
    "83c408"        # add esp,8
    "58"            # pop eax
    "50"            # push eax                 ; keep access flags
    "6a00"          # push 0
    "6880000000"    # push 0x80
    "6a03"          # push 3
    "6a00"          # push 0
    "6a01"          # push 1
    "50"            # push eax
    "8d95d4feffff"  # lea edx,[ebp-0x12c]
    "52"            # push edx
    "ff15c4a07700"  # call [CreateFileA]       ; overlay file
    "89c1"          # mov ecx,eax
    "58"            # pop eax
    "83f9ff"        # cmp ecx,-1
    "740a"          # je orig
    "83c408"        # add esp,8                ; drop the original two pushed args
    "89c8"          # mov eax,ecx
    "e925bfecff"    # jmp 0x645553             ; handle in eax, as if CreateFileA returned
    "6a03"          # orig: push 3
    "53"            # push ebx
    "6a01"          # push 1
    "50"            # push eax
    "57"            # push edi
    "ff15c4a07700"  # call [CreateFileA]
    "e913bfecff"    # jmp 0x645553
    "6c616e675c00"  # "lang\"
)

# cLoadString(HINSTANCE, UINT id, char* buf, int size), cdecl
CAVE_LS = bytes.fromhex(
    "55"            # push ebp
    "89e5"          # mov ebp,esp
    "53"            # push ebx
    "56"            # push esi
    "57"            # push edi
    "8b550c"        # mov edx,[ebp+0xc]        ; id
    "833d6ca8800000"  # cmp [languageOffset],0
    "7411"          # je fill
    "833d80d6800000"  # cmp [g_state],0
    "7508"          # jne fill
    "e888000000"    # call load_table
    "8b550c"        # mov edx,[ebp+0xc]
    "8b7d10"        # fill: mov edi,[ebp+0x10] ; buf
    "8b4d14"        # mov ecx,[ebp+0x14]       ; size
    "89cb"          # mov ebx,ecx
    "31c0"          # xor eax,eax
    "c1e902"        # shr ecx,2
    "f3ab"          # rep stosd                ; zero-fill like the original
    "89d9"          # mov ecx,ebx
    "83e103"        # and ecx,3
    "f3aa"          # rep stosb
    "833d6ca8800000"  # cmp [languageOffset],0
    "7451"          # je winapi
    "833d80d6800001"  # cmp [g_state],1
    "7548"          # jne winapi
    "8b3584d68000"  # mov esi,[g_table]
    "8b4e04"        # mov ecx,[esi+4]          ; count
    "8d7e08"        # lea edi,[esi+8]          ; ids[]
    "31db"          # xor ebx,ebx
    "39cb"          # scan: cmp ebx,ecx
    "7336"          # jae winapi               ; id not in table
    "39149f"        # cmp [edi+ebx*4],edx
    "7403"          # je found
    "43"            # inc ebx
    "ebf4"          # jmp scan
    "8d048f"        # found: lea eax,[edi+ecx*4] ; offsets[]
    "8b0498"        # mov eax,[eax+ebx*4]
    "01f0"          # add eax,esi              ; string
    "8b7d10"        # mov edi,[ebp+0x10]
    "8b4d14"        # mov ecx,[ebp+0x14]
    "49"            # dec ecx                  ; room for NUL
    "7e19"          # jle ret0
    "31db"          # xor ebx,ebx
    "8a1418"        # copy: mov dl,[eax+ebx]
    "84d2"          # test dl,dl
    "7408"          # je done
    "88141f"        # mov [edi+ebx],dl
    "43"            # inc ebx
    "39cb"          # cmp ebx,ecx
    "72f1"          # jb copy
    "c6041f00"      # done: mov byte [edi+ebx],0
    "89d8"          # mov eax,ebx              ; return length
    "eb14"          # jmp ret
    "31c0"          # ret0: xor eax,eax
    "eb10"          # jmp ret
    "ff7514"        # winapi: push [ebp+0x14]
    "ff7510"        # push [ebp+0x10]
    "52"            # push edx                 ; base id (English resource)
    "ff7508"        # push [ebp+8]
    "ff15c0a27700"  # call [LoadStringA]
    "5f"            # ret: pop edi
    "5e"            # pop esi
    "5b"            # pop ebx
    "5d"            # pop ebp
    "c3"            # ret
    "c70580d6800002000000"  # load_table: mov [g_state],2 ; assume failure
    "6a00"          # push 0
    "6880000000"    # push 0x80
    "6a03"          # push 3                   ; OPEN_EXISTING
    "6a00"          # push 0
    "6a01"          # push 1                   ; FILE_SHARE_READ
    "6800000080"    # push 0x80000000          ; GENERIC_READ
    "689d977700"    # push "lang\kor\strings.bin"
    "ff15c4a07700"  # call [CreateFileA]
    "83f8ff"        # cmp eax,-1
    "7478"          # je lt_ret
    "89c6"          # mov esi,eax              ; handle
    "6a00"          # push 0
    "56"            # push esi
    "ff15c0a07700"  # call [GetFileSize]
    "83f808"        # cmp eax,8
    "7261"          # jb lt_close
    "3d00004000"    # cmp eax,0x400000         ; 4 MB sanity limit
    "775a"          # ja lt_close
    "89c7"          # mov edi,eax              ; size
    "50"            # push eax
    "e82d61feff"    # call _malloc
    "83c404"        # add esp,4
    "85c0"          # test eax,eax
    "744b"          # je lt_close
    "89c3"          # mov ebx,eax              ; image
    "6a00"          # push 0
    "6888d68000"    # push g_tmp
    "57"            # push edi
    "53"            # push ebx
    "56"            # push esi
    "ff15b8a07700"  # call [ReadFile]
    "85c0"          # test eax,eax
    "7435"          # je lt_close
    "393d88d68000"  # cmp [g_tmp],edi          ; whole file read?
    "752d"          # jne lt_close
    "813b4b535452"  # cmp dword [ebx],'KSTR'
    "7525"          # jne lt_close
    "8b4304"        # mov eax,[ebx+4]          ; count
    "3d00001000"    # cmp eax,0x100000
    "771b"          # ja lt_close
    "8d04c508000000"  # lea eax,[eax*8+8]      ; header + tables must fit
    "39f8"          # cmp eax,edi
    "7710"          # ja lt_close
    "891d84d68000"  # mov [g_table],ebx
    "c70580d6800001000000"  # mov [g_state],1
    "56"            # lt_close: push esi
    "ff15a4a07700"  # call [CloseHandle]
    "c3"            # lt_ret: ret
    "6c616e675c6b6f725c737472696e67732e62696e00"  # "lang\kor\strings.bin"
)
assert CAVE_FO_VA + len(CAVE_FO) <= CAVE_LS_VA
CAVE_END_VA = CAVE_LS_VA + len(CAVE_LS)
assert CAVE_END_VA <= 0x779900, hex(CAVE_END_VA)
assert len(NEW_FO_HOOK) == len(ORIG_FO_HOOK) == 13 and len(ORIG_LS) == 0x40


def section(data, name):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    for i in range(nsec):
        hdr = pe + 24 + opt + 40 * i
        if data[hdr:hdr + 8].rstrip(b"\0") == name:
            return hdr
    raise SystemExit(f"no {name!r} section")


def main(src, dst):
    data = bytearray(open(src, "rb").read())
    text, dsec = section(data, b".text"), section(data, b".data")
    t_vsize, t_rva, t_rsize = struct.unpack_from("<III", data, text + 8)
    d_vsize, d_rva = struct.unpack_from("<II", data, dsec + 8)
    want_text = CAVE_END_VA - BASE - t_rva
    want_data = DATA_GLOBALS_END - BASE - d_rva
    fo_off, ls_off = FO_HOOK_VA - BASE, LS_HOOK_VA - BASE
    cfo, cls = CAVE_FO_VA - BASE, CAVE_LS_VA - BASE
    fo_cur, ls_cur = bytes(data[fo_off:fo_off + 13]), bytes(data[ls_off:ls_off + 0x40])
    cave_cur = bytes(data[cfo:cfo + (CAVE_END_VA - CAVE_FO_VA)])
    cave_new = CAVE_FO + b"\0" * (CAVE_LS_VA - CAVE_FO_VA - len(CAVE_FO)) + CAVE_LS
    if (fo_cur == NEW_FO_HOOK and ls_cur == NEW_LS_HOOK + ORIG_LS[5:] and cave_cur == cave_new
            and t_vsize >= want_text and d_vsize >= want_data):
        print("already patched"); return 0
    if fo_cur != ORIG_FO_HOOK or ls_cur != ORIG_LS:
        print("refusing: bytes at the hook sites do not match the original File::open / cLoadString code"); return 2
    if t_rva != 0x1000 or t_rsize < want_text or cave_cur.strip(b"\0"):
        print("refusing: the .text cave area is not unused zero padding"); return 2
    if d_rva != 0x189000 or d_vsize > want_data:
        print("refusing: unexpected .data layout (globals at 0x80d680 would collide)"); return 2
    data[fo_off:fo_off + 13] = NEW_FO_HOOK
    data[ls_off:ls_off + 5] = NEW_LS_HOOK
    data[cfo:cfo + len(cave_new)] = cave_new
    if t_vsize < want_text:
        struct.pack_into("<I", data, text + 8, want_text)
    struct.pack_into("<I", data, dsec + 8, want_data)
    open(dst, "wb").write(data)
    print(f"patched {dst}: lang\\kor\\ file overlay + lang\\kor\\strings.bin table (code at 0x{CAVE_FO_VA:x}-0x{CAVE_END_VA:x})")
    print("sha256:", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))
