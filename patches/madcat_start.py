"""Recreate the 1998 "Mad Cat patch" for MechCommander Gold: put an unassigned Mad Cat A
in the mech bay at the start of the original campaign.

The official mc_madcat.exe shipped a start0.pkk whose roster header lists one
unassigned mech ([Mechs] NumMechs=1, PacketNum=7) followed by the Mad Cat A
profile (PM207100) with four extra lines (Assigned/NotMineYet/Pilot/Required).
This script does the same to the Gold START0.PKK, using Gold's own PM207100.FIT
so component/chassis IDs match the 1999 data.  Packets are written uncompressed
(RAW) with the save-file checksum header; the game reads RAW packets natively.

usage: python madcat_start.py <START0.PKK (original)> <PM207100.FIT> <out START0.PKK>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from mcg_pkk import PacketFile, build_packet_file  # noqa: E402

MADCAT_EXTRA = ["b Assigned=FALSE", "b NotMineYet=FALSE", "l Pilot= -1", "b Required=FALSE"]


def rewrite_header(text: str, madcat_packet_num: int) -> str:
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    i_mechs = lines.index("[Mechs]")
    i_veh = lines.index("[Vehicles]")
    block = lines[i_mechs:i_veh]
    # existing assigned mechs: (PacketNum line) pairs after [AssMechs]
    ass = [ln for ln in block if re.match(r"\s*ul\s+PacketNum\s*=", ln)]
    n_unassigned = int(re.search(r"NumMechs\s*=\s*(\d+)", "\n".join(block)).group(1))
    if n_unassigned != 0:
        raise SystemExit("header already lists unassigned mechs; refusing to guess")
    new_block = ["[Mechs]", "ul NumMechs=1", "", "[Mech0]", f"ul PacketNum={madcat_packet_num} //Mad Cat A", "",
                 "[AssMechs]", f"ul NumAssMechs={len(ass)}", ""]
    for k, ln in enumerate(ass, start=1):
        new_block += [f"[Mech{k}]", ln.strip(), ""]
    return eol.join(lines[:i_mechs] + new_block + lines[i_veh:])


def madcat_packet(profile: str) -> bytes:
    eol = "\r\n" if "\r\n" in profile else "\n"
    lines = profile.replace("\r\n", "\n").split("\n")
    i_general = lines.index("[General]")
    i_next = next(i for i in range(i_general + 1, len(lines)) if lines[i].startswith("["))
    lines[i_next:i_next] = MADCAT_EXTRA
    return eol.join(lines).encode("latin-1")


def main(src: str, profile: str, dst: str) -> int:
    pf = PacketFile(Path(src).read_bytes())
    if not pf.checksum_ok:
        raise SystemExit("input START0.PKK checksum mismatch")
    packets = [pf.read_packet(i) for i in range(pf.num_packets)]
    header = packets[0].decode("latin-1")
    if "Mad Cat" in header:
        raise SystemExit("input already contains a Mad Cat entry")
    gifts = packets[-1]                       # [Header] l NumGifts ... stays last
    middle = packets[1:-1]                    # warriors + assigned mechs
    madcat_num = len(middle)                  # PacketNum is index-1; new packet goes before gifts
    new_header = rewrite_header(header, madcat_num).encode("latin-1")
    # read as bytes: the FIT parser needs the original CRLF line endings, and
    # read_text() would silently convert them to LF.
    profile_text = Path(profile).read_bytes().decode("latin-1")
    out_packets = [new_header] + middle + [madcat_packet(profile_text)] + [gifts]
    for i, p in enumerate(out_packets):
        if b"\n" in p and p.count(b"\r\n") != p.count(b"\n"):
            raise SystemExit(f"packet {i} is not CRLF-terminated; the game would reject it")
    data = build_packet_file(out_packets)
    check = PacketFile(data)
    assert check.checksum_ok and check.num_packets == len(out_packets)
    for i, p in enumerate(out_packets):
        assert check.read_packet(i) == p, i
    Path(dst).write_bytes(data)
    print(f"wrote {dst}: {len(data)} bytes, {len(out_packets)} packets, Mad Cat A = packet {madcat_num + 1} (PacketNum {madcat_num})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(*sys.argv[1:]))
