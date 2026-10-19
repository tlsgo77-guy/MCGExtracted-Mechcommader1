"""Make MCX.EXE's text engine draw 2-byte EUC-KR characters (MechCommander Gold / DM 2.99.7.2601).

Korean mode is active when the global `languageOffset` (0x80a86c, prefs.cfg "l Language=")
is non-zero; with Language=0 every patched function behaves exactly as before.

Glyph mapping (the Korean FNT files are built with this layout): bytes 0..255 keep
their glyph index; a pair (lead, trail) with both bytes in 0xA1..0xFE maps to
index 256 + (lead-0xA1)*94 + (trail-0xA1), so a Korean FNT has 9092 glyph slots.
Pairs are only decoded for fonts whose glyph count (u32 at fontData+4) is >= 9092;
a font that was not extended (DIM*.FNT, L*.FNT, ...) draws every byte as a single
glyph, so the offset table is never indexed out of range and the byte stream never
desynchronises.

Patched (code lives in the unused .text tail at 0x779900, VirtualSize enlarged):
  _VFX_string_draw @0x77164e          per-character walker decodes pairs
  aFont::width(char*) @0x60ab00       pair-aware string width
  aFont::writeString @0x60ac46        max-width truncation never splits a pair
  aFont::charactersToWidth @0x60adc1  character-mode count is pair aligned
  SMUTI::process @0x72931a/0x728fa6/0x72920c  briefing/description markup renderer
                                      measures, buffers and draws pairs as units
  SMUTI::checkWrap @0x729479          the no-space line break moves a whole pair
                                      (the pair path enters checkWrap's break body
                                      through a small frame stub, 0x729457)

usage: python patch_korean_text.py <in MCX.EXE> <out MCX.EXE>
"""
import hashlib
import struct
import sys

BASE = 0x600000
CAVE_VA = 0x779900
CAVE_END = 0x779c51
TEXT_VSIZE_MIN = CAVE_END - BASE - 0x1000

# (description, VA, original bytes, replacement bytes)
HOOKS = [
    ("VFX_string_draw", 0x77164e,
     bytes.fromhex("558bec53565706fc1e078b75188b7d0c0fb606ff751c50ff7514ff751057ff7508e847feffff83c41803f846803e0075df075f5e5bc9c3"),
     bytes.fromhex("e9438300009090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090")),
    ("aFont::width(char*)", 0x60ab00,
     bytes.fromhex("558bec5153"),
     bytes.fromhex("e9cfee1600")),
    ("aFont::writeString truncation", 0x60ac46,
     bytes.fromhex("8a4c37ff4f884d17"),
     bytes.fromhex("e8d9ed1600909090")),
    ("aFont::charactersToWidth char mode", 0x60adc1,
     bytes.fromhex("8b5d0883c9ff"),
     bytes.fromhex("e974ec160090")),
    ("SMUTI::process plain char", 0x72931a,
     bytes.fromhex("80fb200f82fdfbffff"),
     bytes.fromhex("e98107050090909090")),
    ("SMUTI::checkWrap no-space split", 0x729479,
     bytes.fromhex("8b8e200100008a54311f8d04318850208bbe200100004fc6443720008b862001000040898620010000"),
     bytes.fromhex("e98a060500909090909090909090909090909090909090909090909090909090909090909090909090")),
    ("SMUTI::process centred collect", 0x728fa6,
     bytes.fromhex("8a1880fb25"),
     bytes.fromhex("e9cc0b0500")),
    ("SMUTI::process single char", 0x72920c,
     bytes.fromhex("8b4e0485c9"),
     bytes.fromhex("e9e0090500")),
]

CAVE = bytes.fromhex(
    # --- kr_boundary @0x779900
    "8b4c2404"          # mov ecx, dword ptr [esp + 4]
    "8b542408"          # mov edx, dword ptr [esp + 8]
    "89d0"              # mov eax, edx
    "833d6ca8800000"    # cmp dword ptr [0x80a86c], 0
    "7438"              # je 0x77994b
    "53"                # push ebx
    "31c0"              # xor eax, eax
    "39d0"              # cmp eax, edx
    "7329"              # jae 0x779943
    "0fb61c01"          # movzx ebx, byte ptr [ecx + eax]
    "85db"              # test ebx, ebx
    "7421"              # je 0x779943
    "80fba1"            # cmp bl, 0xa1
    "7219"              # jb 0x779940
    "80fbff"            # cmp bl, 0xff
    "7414"              # je 0x779940
    "0fb65c0101"        # movzx ebx, byte ptr [ecx + eax + 1]
    "80fba1"            # cmp bl, 0xa1
    "720a"              # jb 0x779940
    "80fbff"            # cmp bl, 0xff
    "7405"              # je 0x779940
    "83c002"            # add eax, 2
    "ebd6"              # jmp 0x779916
    "40"                # inc eax
    "ebd3"              # jmp 0x779916
    "39d0"              # cmp eax, edx
    "7603"              # jbe 0x77994a
    "83e802"            # sub eax, 2
    "5b"                # pop ebx
    "c3"                # ret 
    # --- kr_decode @0x77994c
    "53"                # push ebx
    "8b4c240c"          # mov ecx, dword ptr [esp + 0xc]
    "0fb601"            # movzx eax, byte ptr [ecx]
    "ba01000000"        # mov edx, 1
    "833d6ca8800000"    # cmp dword ptr [0x80a86c], 0
    "7432"              # je 0x779994
    "3ca1"              # cmp al, 0xa1
    "722e"              # jb 0x779994
    "3cff"              # cmp al, 0xff
    "742a"              # je 0x779994
    "0fb65901"          # movzx ebx, byte ptr [ecx + 1]
    "80fba1"            # cmp bl, 0xa1
    "7221"              # jb 0x779994
    "80fbff"            # cmp bl, 0xff
    "741c"              # je 0x779994
    "8b4c2408"          # mov ecx, dword ptr [esp + 8]
    "81790484230000"    # cmp dword ptr [ecx + 4], 0x2384
    "720f"              # jb 0x779994
    "6bc05e"            # imul eax, eax, 0x5e
    "01d8"              # add eax, ebx
    "2dbf3a0000"        # sub eax, 0x3abf
    "ba02000000"        # mov edx, 2
    "5b"                # pop ebx
    "c3"                # ret 
    # --- vfx_sd @0x779996
    "55"                # push ebp
    "89e5"              # mov ebp, esp
    "53"                # push ebx
    "56"                # push esi
    "57"                # push edi
    "8b7518"            # mov esi, dword ptr [ebp + 0x18]
    "8b7d0c"            # mov edi, dword ptr [ebp + 0xc]
    "56"                # push esi
    "ff7514"            # push dword ptr [ebp + 0x14]
    "e8a1ffffff"        # call 0x77994c
    "83c408"            # add esp, 8
    "4a"                # dec edx
    "01d6"              # add esi, edx
    "ff751c"            # push dword ptr [ebp + 0x1c]
    "50"                # push eax
    "ff7514"            # push dword ptr [ebp + 0x14]
    "ff7510"            # push dword ptr [ebp + 0x10]
    "57"                # push edi
    "ff7508"            # push dword ptr [ebp + 8]
    "e8f77affff"        # call 0x7714bb
    "83c418"            # add esp, 0x18
    "01c7"              # add edi, eax
    "46"                # inc esi
    "803e00"            # cmp byte ptr [esi], 0
    "75d3"              # jne 0x7799a2
    "5f"                # pop edi
    "5e"                # pop esi
    "5b"                # pop ebx
    "5d"                # pop ebp
    "c3"                # ret 
    # --- afont_width @0x7799d4
    "833d6ca8800000"    # cmp dword ptr [0x80a86c], 0
    "750a"              # jne 0x7799e7
    "55"                # push ebp
    "89e5"              # mov ebp, esp
    "51"                # push ecx
    "53"                # push ebx
    "e91e11e9ff"        # jmp 0x60ab05
    "55"                # push ebp
    "89e5"              # mov ebp, esp
    "53"                # push ebx
    "56"                # push esi
    "57"                # push edi
    "31ff"              # xor edi, edi
    "8b5d08"            # mov ebx, dword ptr [ebp + 8]
    "85db"              # test ebx, ebx
    "7425"              # je 0x779a1b
    "8b31"              # mov esi, dword ptr [ecx]
    "85f6"              # test esi, esi
    "741f"              # je 0x779a1b
    "803b00"            # cmp byte ptr [ebx], 0
    "741a"              # je 0x779a1b
    "53"                # push ebx
    "56"                # push esi
    "e844ffffff"        # call 0x77994c
    "83c408"            # add esp, 8
    "01d3"              # add ebx, edx
    "50"                # push eax
    "56"                # push esi
    "e8877affff"        # call 0x77149b
    "83c408"            # add esp, 8
    "01c7"              # add edi, eax
    "ebe1"              # jmp 0x7799fc
    "89f8"              # mov eax, edi
    "5f"                # pop edi
    "5e"                # pop esi
    "5b"                # pop ebx
    "5d"                # pop ebp
    "c20400"            # ret 4
    # --- ws_stub @0x779a24
    "8d47ff"            # lea eax, [edi - 1]
    "50"                # push eax
    "56"                # push esi
    "e8d2feffff"        # call 0x779900
    "83c408"            # add esp, 8
    "89c7"              # mov edi, eax
    "8a0c37"            # mov cl, byte ptr [edi + esi]
    "884d17"            # mov byte ptr [ebp + 0x17], cl
    "c3"                # ret 
    # --- ctw_char @0x779a3a
    "8b5d08"            # mov ebx, dword ptr [ebp + 8]
    "89df"              # mov edi, ebx
    "83c9ff"            # or ecx, 0xffffffff
    "31c0"              # xor eax, eax
    "f2ae"              # repne scasb al, byte ptr es:[edi]
    "f7d1"              # not ecx
    "49"                # dec ecx
    "88450b"            # mov byte ptr [ebp + 0xb], al
    "8d340b"            # lea esi, [ebx + ecx]
    "39de"              # cmp esi, ebx
    "762f"              # jbe 0x779a82
    "8b4dfc"            # mov ecx, dword ptr [ebp - 4]
    "53"                # push ebx
    "e8a410e9ff"        # call 0x60ab00
    "3b450c"            # cmp eax, dword ptr [ebp + 0xc]
    "7e21"              # jle 0x779a82
    "8a450b"            # mov al, byte ptr [ebp + 0xb]
    "8806"              # mov byte ptr [esi], al
    "89f0"              # mov eax, esi
    "29d8"              # sub eax, ebx
    "48"                # dec eax
    "50"                # push eax
    "53"                # push ebx
    "e88efeffff"        # call 0x779900
    "83c408"            # add esp, 8
    "8d3403"            # lea esi, [ebx + eax]
    "8a0e"              # mov cl, byte ptr [esi]
    "884d0b"            # mov byte ptr [ebp + 0xb], cl
    "c60600"            # mov byte ptr [esi], 0
    "ebcd"              # jmp 0x779a4f
    "8a550b"            # mov dl, byte ptr [ebp + 0xb]
    "8816"              # mov byte ptr [esi], dl
    "29de"              # sub esi, ebx
    "89f0"              # mov eax, esi
    "5f"                # pop edi
    "5e"                # pop esi
    "5b"                # pop ebx
    "89ec"              # mov esp, ebp
    "5d"                # pop ebp
    "c20c00"            # ret 0xc
    # --- kr_wrap_body @0x779a94
    "55"                # push ebp
    "89e5"              # mov ebp, esp
    "56"                # push esi
    "89ce"              # mov esi, ecx
    "57"                # push edi
    "e9b7f9faff"        # jmp 0x729457
    # --- smuti_plain @0x779aa0
    "80fb20"            # cmp bl, 0x20
    "7259"              # jb 0x779afe
    "57"                # push edi
    "8b0e"              # mov ecx, dword ptr [esi]
    "ff31"              # push dword ptr [ecx]
    "e89dfeffff"        # call 0x77994c
    "83c408"            # add esp, 8
    "83fa02"            # cmp edx, 2
    "754c"              # jne 0x779b03
    "8b0e"              # mov ecx, dword ptr [esi]
    "8b09"              # mov ecx, dword ptr [ecx]
    "50"                # push eax
    "51"                # push ecx
    "e8d979ffff"        # call 0x77149b
    "83c408"            # add esp, 8
    "50"                # push eax
    "034614"            # add eax, dword ptr [esi + 0x14]
    "03460c"            # add eax, dword ptr [esi + 0xc]
    "3b4608"            # cmp eax, dword ptr [esi + 8]
    "7c09"              # jl 0x779ada
    "6a00"              # push 0
    "89f1"              # mov ecx, esi
    "e8baffffff"        # call 0x779a94
    "58"                # pop eax
    "8b8e20010000"      # mov ecx, dword ptr [esi + 0x120]
    "885c0e20"          # mov byte ptr [esi + ecx + 0x20], bl
    "8a5701"            # mov dl, byte ptr [edi + 1]
    "88540e21"          # mov byte ptr [esi + ecx + 0x21], dl
    "83c102"            # add ecx, 2
    "898e20010000"      # mov dword ptr [esi + 0x120], ecx
    "c6440e2000"        # mov byte ptr [esi + ecx + 0x20], 0
    "47"                # inc edi
    "01460c"            # add dword ptr [esi + 0xc], eax
    "e91df4faff"        # jmp 0x728f20
    "e91bf8faff"        # jmp 0x729323
    # --- cw_nospace @0x779b08
    "8b8e20010000"      # mov ecx, dword ptr [esi + 0x120]
    "83f902"            # cmp ecx, 2
    "721d"              # jb 0x779b30
    "8d4620"            # lea eax, [esi + 0x20]
    "8d51ff"            # lea edx, [ecx - 1]
    "52"                # push edx
    "50"                # push eax
    "e8e0fdffff"        # call 0x779900
    "83c408"            # add esp, 8
    "8b8e20010000"      # mov ecx, dword ptr [esi + 0x120]
    "8d51ff"            # lea edx, [ecx - 1]
    "39d0"              # cmp eax, edx
    "751c"              # jne 0x779b4c
    "8a540e1f"          # mov dl, byte ptr [esi + ecx + 0x1f]
    "88540e20"          # mov byte ptr [esi + ecx + 0x20], dl
    "8d79ff"            # lea edi, [ecx - 1]
    "c6443e2000"        # mov byte ptr [esi + edi + 0x20], 0
    "41"                # inc ecx
    "898e20010000"      # mov dword ptr [esi + 0x120], ecx
    "e956f9faff"        # jmp 0x7294a2
    "8a540e1e"          # mov dl, byte ptr [esi + ecx + 0x1e]
    "88540e20"          # mov byte ptr [esi + ecx + 0x20], dl
    "8a540e1f"          # mov dl, byte ptr [esi + ecx + 0x1f]
    "88540e21"          # mov byte ptr [esi + ecx + 0x21], dl
    "c6440e1e00"        # mov byte ptr [esi + ecx + 0x1e], 0
    "c6440e1f00"        # mov byte ptr [esi + ecx + 0x1f], 0
    "8d79ff"            # lea edi, [ecx - 1]
    "83c102"            # add ecx, 2
    "898e20010000"      # mov dword ptr [esi + 0x120], ecx
    "e92bf9faff"        # jmp 0x7294a2
    # --- smuti_center @0x779b77
    "833d6ca8800000"    # cmp dword ptr [0x80a86c], 0
    "750a"              # jne 0x779b8a
    "8a18"              # mov bl, byte ptr [eax]
    "80fb25"            # cmp bl, 0x25
    "e921f4faff"        # jmp 0x728fab
    "8a18"              # mov bl, byte ptr [eax]
    "80fb25"            # cmp bl, 0x25
    "7456"              # je 0x779be7
    "84db"              # test bl, bl
    "7452"              # je 0x779be7
    "83ff4f"            # cmp edi, 0x4f
    "734d"              # jae 0x779be7
    "50"                # push eax
    "8b0e"              # mov ecx, dword ptr [esi]
    "ff31"              # push dword ptr [ecx]
    "e8a8fdffff"        # call 0x77994c
    "83c408"            # add esp, 8
    "8b0e"              # mov ecx, dword ptr [esi]
    "8b09"              # mov ecx, dword ptr [ecx]
    "52"                # push edx
    "50"                # push eax
    "51"                # push ecx
    "e8e878ffff"        # call 0x77149b
    "83c408"            # add esp, 8
    "5a"                # pop edx
    "8b4d0c"            # mov ecx, dword ptr [ebp + 0xc]
    "885c3dac"          # mov byte ptr [ebp + edi - 0x54], bl
    "47"                # inc edi
    "83fa02"            # cmp edx, 2
    "750b"              # jne 0x779bcf
    "8a4901"            # mov cl, byte ptr [ecx + 1]
    "884c3dac"          # mov byte ptr [ebp + edi - 0x54], cl
    "47"                # inc edi
    "ff450c"            # inc dword ptr [ebp + 0xc]
    "8b4d10"            # mov ecx, dword ptr [ebp + 0x10]
    "01c1"              # add ecx, eax
    "894d10"            # mov dword ptr [ebp + 0x10], ecx
    "3b4e08"            # cmp ecx, dword ptr [esi + 8]
    "7d10"              # jge 0x779bec
    "8b450c"            # mov eax, dword ptr [ebp + 0xc]
    "40"                # inc eax
    "89450c"            # mov dword ptr [ebp + 0xc], eax
    "8a18"              # mov bl, byte ptr [eax]
    "eba5"              # jmp 0x779b8c
    "e9f4f3faff"        # jmp 0x728fe0
    "e9f2f3faff"        # jmp 0x728fe3
    # --- smuti_single @0x779bf1
    "57"                # push edi
    "8b0e"              # mov ecx, dword ptr [esi]
    "ff31"              # push dword ptr [ecx]
    "e851fdffff"        # call 0x77994c
    "83c408"            # add esp, 8
    "83fa02"            # cmp edx, 2
    "7544"              # jne 0x779c47
    "0fb707"            # movzx eax, word ptr [edi]
    "50"                # push eax
    "8b4e04"            # mov ecx, dword ptr [esi + 4]
    "85c9"              # test ecx, ecx
    "7418"              # je 0x779c26
    "e8cd2fe9ff"        # call 0x60cbe0
    "89e2"              # mov edx, esp
    "6aff"              # push -1
    "52"                # push edx
    "ff7610"            # push dword ptr [esi + 0x10]
    "ff760c"            # push dword ptr [esi + 0xc]
    "50"                # push eax
    "8b0e"              # mov ecx, dword ptr [esi]
    "e8ca0fe9ff"        # call 0x60abf0
    "89e0"              # mov eax, esp
    "50"                # push eax
    "8b0e"              # mov ecx, dword ptr [esi]
    "e8d00ee9ff"        # call 0x60ab00
    "83c404"            # add esp, 4
    "8b4e0c"            # mov ecx, dword ptr [esi + 0xc]
    "01c1"              # add ecx, eax
    "894e0c"            # mov dword ptr [esi + 0xc], ecx
    "8b7d0c"            # mov edi, dword ptr [ebp + 0xc]
    "47"                # inc edi
    "897d0c"            # mov dword ptr [ebp + 0xc], edi
    "e9d9f2faff"        # jmp 0x728f20
    "8b4e04"            # mov ecx, dword ptr [esi + 4]
    "85c9"              # test ecx, ecx
    "e9c0f5faff"        # jmp 0x729211
)
assert CAVE_VA + len(CAVE) == CAVE_END


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
    cave = bytes(data[CAVE_VA - BASE:CAVE_END - BASE])
    states = set()
    for name, va, orig, new in HOOKS:
        cur = bytes(data[va - BASE:va - BASE + len(orig)])
        states.add("new" if cur == new else "orig" if cur == orig else "other:" + name)
    if states == {"new"} and cave == CAVE:
        print("already patched"); return 0
    if states != {"orig"}:
        print("refusing: unexpected bytes at", sorted(states)); return 2
    if rva != 0x1000 or rsize < TEXT_VSIZE_MIN or cave.strip(b"\0"):
        print("refusing: the cave region 0x779900..0x779f00 is not unused zero padding"); return 2
    for name, va, orig, new in HOOKS:
        data[va - BASE:va - BASE + len(new)] = new
    data[CAVE_VA - BASE:CAVE_END - BASE] = CAVE
    if vsize < TEXT_VSIZE_MIN:
        struct.pack_into("<I", data, hdr + 8, TEXT_VSIZE_MIN)
    open(dst, "wb").write(data)
    print(f"patched {dst}: EUC-KR text engine (Korean mode when prefs Language != 0)")
    print("sha256:", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))
