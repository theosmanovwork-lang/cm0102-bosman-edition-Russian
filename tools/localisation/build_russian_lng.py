#!/usr/bin/env python3
"""Build a Russian CM 01/02 database-name file without modifying clean eng.lng.

The legacy .lng format uses fixed-width name slots. Cyrillic is represented with
the game's #XXXX# escape syntax; a value that does not fit is rejected, never cut.
Untranslated club, city and stadium proper names are copied unchanged.
"""
from __future__ import annotations
import argparse
import csv
import os
import struct
from pathlib import Path

HEADER_SIZE = 32
NAME_SIZE = 51
SECTIONS = {
    "clubs": (0, 0x4F, 26),
    "continents": (1, 0xBA, 0),
    "nation_competitions": (2, 0x53, 26),
    "nations": (3, 0x6D, 51),
    "stadiums": (6, 0x34, 0),
    "cities": (4, 0x34, 0),
    "staff_competitions": (7, 0x4F, 26),
    "club_competitions": (5, 0x53, 26),
}
DATA_ORDER = ("clubs", "continents", "nation_competitions", "nations",
              "stadiums", "cities", "staff_competitions", "club_competitions")

def encode_game_text(value: str, slot_size: int) -> bytes:
    out = bytearray()
    for char in value:
        cp = ord(char)
        if cp == 0:
            raise ValueError("translation contains NUL")
        if cp > 0xFFFF:
            raise ValueError(f"translation contains non-BMP U+{cp:04X}")
        if cp < 0x80 and char != "#":
            out.append(cp)
        else:
            out.extend(f"#{cp:04X}#".encode("ascii"))
    if len(out) + 1 > slot_size:
        raise ValueError(f"encoded value needs {len(out) + 1} bytes; fixed slot has {slot_size}")
    return bytes(out)

def read_rows(path: Path):
    required = {"section", "row", "source_en", "source_short_en", "name_ru", "short_name_ru"}
    result = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("names TSV must contain: " + ", ".join(sorted(required)))
        for row in reader:
            section = (row.get("section") or "").strip()
            if section not in SECTIONS:
                raise ValueError(f"unknown section {section!r}")
            try:
                index = int(row["row"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid row number {row.get('row')!r}") from exc
            key = (section, index)
            if key in result:
                raise ValueError(f"duplicate name translation key {key}")
            name_ru = (row.get("name_ru") or "").strip()
            short_ru = (row.get("short_name_ru") or "").strip()
            if name_ru or short_ru:
                result[key] = ((row.get("source_en") or "").strip(),
                               (row.get("source_short_en") or "").strip(),
                               name_ru, short_ru)
    return result

def build_russian_lng(source: Path, names_tsv: Path, output: Path) -> tuple[int, int]:
    if source.resolve() == output.resolve():
        raise ValueError("output path must differ from source eng.lng")
    original = source.read_bytes()
    if len(original) < HEADER_SIZE:
        raise ValueError("source .lng is shorter than its 32-byte header")
    counts = struct.unpack_from("<8i", original)
    if any(count < 0 for count in counts):
        raise ValueError("source .lng contains a negative section count")
    offsets = {}
    cursor = HEADER_SIZE
    for section in DATA_ORDER:
        header_index, entry_size, _ = SECTIONS[section]
        offsets[section] = cursor
        cursor += counts[header_index] * entry_size
    if cursor != len(original):
        raise ValueError(f"unexpected .lng size: got {len(original)}, expected {cursor}")
    translations = read_rows(names_tsv)
    data = bytearray(original)
    long_count = short_count = 0
    for (section, index), (source_en, source_short, name_ru, short_ru) in translations.items():
        header_index, entry_size, short_size = SECTIONS[section]
        if index < 0 or index >= counts[header_index]:
            raise ValueError(f"{section} row {index} is outside 0..{counts[header_index] - 1}")
        base = offsets[section] + index * entry_size
        actual_long = bytes(data[base:base + NAME_SIZE]).split(b"\0", 1)[0].decode("cp1252")
        if source_en and actual_long != source_en:
            raise ValueError(f"{section} row {index}: source name mismatch: {actual_long!r} != {source_en!r}")
        if name_ru:
            encoded = encode_game_text(name_ru, NAME_SIZE)
            data[base:base + NAME_SIZE] = encoded.ljust(NAME_SIZE, b"\0")
            long_count += 1
        if short_ru:
            if not short_size:
                raise ValueError(f"{section} has no short-name slot")
            short_at = base + NAME_SIZE + 1
            actual_short = bytes(data[short_at:short_at + short_size]).split(b"\0", 1)[0].decode("cp1252")
            if source_short and actual_short != source_short:
                raise ValueError(f"{section} row {index}: source short-name mismatch: {actual_short!r} != {source_short!r}")
            encoded = encode_game_text(short_ru, short_size)
            data[short_at:short_at + short_size] = encoded.ljust(short_size, b"\0")
            short_count += 1
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    try:
        temporary.write_bytes(data)
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        if temporary.stat().st_size != len(original):
            raise ValueError("output .lng size changed")
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return long_count, short_count

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="clean Data/eng.lng")
    parser.add_argument("--names", type=Path, required=True, help="UTF-8 Russian database-name TSV")
    parser.add_argument("--output", type=Path, required=True, help="separate Data/rus.lng output")
    args = parser.parse_args()
    long_count, short_count = build_russian_lng(args.source, args.names, args.output)
    print(f"Russian name fields: {long_count}; short-name fields: {short_count}; file: {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
