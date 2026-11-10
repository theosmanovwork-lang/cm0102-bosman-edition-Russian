#!/usr/bin/env python3
"""Append a Russian language block to a player's original CM 01/02 language.ldb.

The source file is never modified. The output retains every original language block
byte-for-byte and appends one text+grammar block for the requested language ID.
"""
from __future__ import annotations

import argparse
import csv
import os
import struct
from pathlib import Path

HEADER_PREFIX_SIZE = 12
LANGUAGE_ID_CAPACITY = 19  # Langlib's available-language ID array is 76 bytes.
TEXT_SLOT_SIZE = 2048
KEY_SLOT_SIZE = 30
META_SIZE = 40
ORIGINAL_LANG_COUNT = 10
DEFAULT_LANGUAGE_ID = 13


def check_language_capacity(existing_count: int, added_count: int = 1) -> None:
    if existing_count < 0 or added_count < 0 or existing_count + added_count > LANGUAGE_ID_CAPACITY:
        raise ValueError(
            f"language ID list would need {existing_count + added_count} slots; "
            f"the original runtime stores {LANGUAGE_ID_CAPACITY}"
        )


def encode_game_text(text: str) -> bytes:
    """Encode BMP text as ASCII and non-ASCII UTF-16 units as #XXXX# escapes."""
    try:
        encoded = bytearray()
        for char in text:
            codepoint = ord(char)
            if codepoint == 0:
                raise ValueError("translation contains an embedded NUL")
            if codepoint > 0xFFFF:
                raise ValueError(
                    f"character U+{codepoint:04X} is outside the game's 16-bit text range"
                )
            if codepoint < 0x80 and char != "#":
                encoded.append(codepoint)
            else:
                encoded.extend(f"#{codepoint:04X}#".encode("ascii"))
    except UnicodeEncodeError as exc:
        raise ValueError("translation cannot be encoded for the game") from exc
    if len(encoded) + 1 > TEXT_SLOT_SIZE:
        raise ValueError(
            f"encoded Russian text needs {len(encoded) + 1} bytes; slot limit is {TEXT_SLOT_SIZE}"
        )
    return bytes(encoded)


def read_translations(
    path: Path | None, entry_count: int
) -> dict[int, tuple[bytes, tuple[int, ...]]]:
    translations: dict[int, tuple[bytes, tuple[int, ...]]] = {}
    if path is None:
        return translations

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"id", "text_ru"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("translation TSV must contain id and text_ru columns")

        for row in reader:
            try:
                index = int(row["id"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid translation id: {row.get('id')!r}") from exc
            if index < 0 or index >= entry_count:
                raise ValueError(f"translation id {index} is outside 0..{entry_count - 1}")
            if index in translations:
                raise ValueError(f"duplicate translation id: {index}")

            text_bytes = encode_game_text(row.get("text_ru") or "")
            raw_meta = (row.get("grammar_meta_ru") or "").strip()
            if raw_meta:
                try:
                    values = tuple(
                        int(part.strip()) for part in raw_meta.strip("[]").split(",")
                    )
                except ValueError as exc:
                    raise ValueError(f"bad grammar_meta_ru for id {index}") from exc
                if len(values) != 10 or any(
                    value < -0x80000000 or value > 0x7FFFFFFF for value in values
                ):
                    raise ValueError(
                        f"grammar_meta_ru for id {index} must contain ten signed 32-bit integers"
                    )
            else:
                values = (-1,) * 10
            translations[index] = (text_bytes, values)

    return translations


def build_extended_language_ldb(
    source: Path,
    destination: Path,
    translations_path: Path | None,
    new_language_id: int = DEFAULT_LANGUAGE_ID,
) -> tuple[int, int]:
    source_resolved = source.resolve()
    destination_resolved = destination.resolve()
    if source_resolved == destination_resolved:
        raise ValueError("output path must differ from the original language.ldb")
    if new_language_id < 0 or new_language_id > 0xFFFFFFFF:
        raise ValueError("language ID must be an unsigned 32-bit integer")

    with source.open("rb") as stream:
        prefix = stream.read(HEADER_PREFIX_SIZE)
        if len(prefix) != HEADER_PREFIX_SIZE:
            raise ValueError("source language.ldb is shorter than its header")

        version, entry_count, language_count = struct.unpack("<III", prefix)
        if version != 1:
            raise ValueError(f"unsupported language.ldb version: {version}")
        if language_count != ORIGINAL_LANG_COUNT:
            raise ValueError(
                f"expected {ORIGINAL_LANG_COUNT} original languages, found {language_count}"
            )
        check_language_capacity(language_count, 1)

        language_bytes = stream.read(language_count * 4)
        if len(language_bytes) != language_count * 4:
            raise ValueError("truncated language ID list")
        language_ids = struct.unpack(f"<{language_count}I", language_bytes)
        if len(set(language_ids)) != len(language_ids):
            raise ValueError("source language ID list contains duplicates")
        if new_language_id in language_ids:
            raise ValueError(f"language ID {new_language_id} already exists")

        record_size = (
            TEXT_SLOT_SIZE
            + KEY_SLOT_SIZE
            + (language_count - 1) * (TEXT_SLOT_SIZE + META_SIZE)
        )
        expected_size = HEADER_PREFIX_SIZE + language_count * 4 + entry_count * record_size
        stream.seek(0, os.SEEK_END)
        actual_size = stream.tell()
        if actual_size != expected_size:
            raise ValueError(
                f"unexpected source size: got {actual_size}, expected {expected_size}"
            )
        stream.seek(HEADER_PREFIX_SIZE + language_count * 4)

        translations = read_translations(translations_path, entry_count)
        new_header = struct.pack("<III", version, entry_count, language_count + 1)
        new_header += struct.pack(
            f"<{language_count + 1}I", *language_ids, new_language_id
        )

        new_record_size = record_size + TEXT_SLOT_SIZE + META_SIZE
        expected_output_size = (
            HEADER_PREFIX_SIZE + (language_count + 1) * 4 + entry_count * new_record_size
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".tmp")
        try:
            with temporary.open("wb") as output:
                output.write(new_header)
                for index in range(entry_count):
                    original_record = stream.read(record_size)
                    if len(original_record) != record_size:
                        raise ValueError(f"truncated source record {index}")

                    text_bytes, meta = translations.get(index, (b"", (-1,) * 10))
                    text_slot = bytearray(TEXT_SLOT_SIZE)
                    text_slot[: len(text_bytes)] = text_bytes
                    output.write(original_record)
                    output.write(text_slot)
                    output.write(struct.pack("<10i", *meta))

                if stream.read(1):
                    raise ValueError("unexpected trailing data in source language.ldb")

                output.flush()
                os.fsync(output.fileno())

            if temporary.stat().st_size != expected_output_size:
                raise ValueError("output size check failed")
            temporary.replace(destination)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    return entry_count, len(translations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="player's original Data/language.ldb")
    parser.add_argument("--translations", type=Path, help="TSV with id, text_ru and optional grammar_meta_ru")
    parser.add_argument("--output", type=Path, required=True, help="write a new extended language.ldb")
    parser.add_argument("--language-id", type=int, default=DEFAULT_LANGUAGE_ID)
    args = parser.parse_args()

    count, translated = build_extended_language_ldb(
        args.source, args.output, args.translations, args.language_id
    )
    print(f"entries: {count}; Russian rows supplied: {translated}; language ID: {args.language_id}")
    print(f"created: {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
