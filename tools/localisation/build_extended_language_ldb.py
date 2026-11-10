#!/usr/bin/env python3
"""Append a Russian language block to a copy of the original CM 01/02 language.ldb.

All inputs are UTF-8 TSV. The source binary is never modified. Original language blocks
are copied byte-for-byte, and each translation may carry a stable source ID and format signature.
"""
from __future__ import annotations

import argparse
import csv
import os
import struct
from pathlib import Path
from typing import Iterable

HEADER_PREFIX_SIZE = 12
LANGUAGE_ID_CAPACITY = 19
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
    """Encode BMP characters as ASCII, using #XXXX# for non-ASCII and literal '#'."""
    encoded = bytearray()
    for char in text:
        codepoint = ord(char)
        if codepoint == 0:
            raise ValueError("translation contains an embedded NUL")
        if codepoint > 0xFFFF:
            raise ValueError(f"character U+{codepoint:04X} is outside the game's 16-bit text range")
        if codepoint < 0x80 and char != "#":
            encoded.append(codepoint)
        else:
            encoded.extend(f"#{codepoint:04X}#".encode("ascii"))
    if len(encoded) + 1 > TEXT_SLOT_SIZE:
        raise ValueError(
            f"encoded Russian text needs {len(encoded) + 1} bytes; slot limit is {TEXT_SLOT_SIZE}"
        )
    return bytes(encoded)


def _normalise_paths(paths: Path | Iterable[Path]) -> list[Path]:
    if isinstance(paths, Path):
        return [paths]
    result = list(paths)
    if not result:
        raise ValueError("at least one translation TSV is required")
    return result


def read_translations(
    paths: Path | Iterable[Path], entry_count: int
) -> dict[int, tuple[bytes, tuple[int, ...], str | None, str | None]]:
    translations: dict[int, tuple[bytes, tuple[int, ...], str | None, str | None]] = {}
    for path in _normalise_paths(paths):
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            required = {"id", "text_ru"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError(f"{path}: TSV must contain id and text_ru columns")
            for row in reader:
                try:
                    index = int(row["id"])
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"{path}: invalid translation id {row.get('id')!r}") from exc
                if index < 0 or index >= entry_count:
                    raise ValueError(f"{path}: translation id {index} is outside 0..{entry_count - 1}")
                if index in translations:
                    raise ValueError(f"duplicate translation id across TSV files: {index}")

                text_bytes = encode_game_text(row.get("text_ru") or "")
                raw_meta = (row.get("grammar_meta_ru") or "").strip()
                if raw_meta:
                    try:
                        values = tuple(int(part.strip()) for part in raw_meta.strip("[]").split(","))
                    except ValueError as exc:
                        raise ValueError(f"{path}: bad grammar_meta_ru for id {index}") from exc
                    if len(values) != 10 or any(value < -1 or value > 9 for value in values):
                        raise ValueError(
                            f"{path}: grammar_meta_ru for id {index} must contain ten values in -1..9"
                        )
                else:
                    values = (-1,) * 10

                translations[index] = (
                    text_bytes, values, row.get("source_en"), row.get("format_signature")
                )
    return translations


def build_extended_language_ldb(
    source: Path,
    destination: Path,
    translations_path: Path | Iterable[Path] | None,
    new_language_id: int = DEFAULT_LANGUAGE_ID,
) -> tuple[int, int]:
    if source.resolve() == destination.resolve():
        raise ValueError("output path must differ from the original language.ldb")
    if new_language_id < 0 or new_language_id > 0xFFFFFFFF:
        raise ValueError("language ID must be an unsigned 32-bit integer")

    with source.open("rb") as stream:
        prefix = stream.read(HEADER_PREFIX_SIZE)
        if len(prefix) != HEADER_PREFIX_SIZE:
            raise ValueError("source language.ldb is shorter than its header")
        version, entry_count, language_count = struct.unpack("<III", prefix)
        if version != 1:
            raise ValueError(f"unsupported source language.ldb version: {version}")
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
            TEXT_SLOT_SIZE + KEY_SLOT_SIZE + (language_count - 1) * (TEXT_SLOT_SIZE + META_SIZE)
        )
        expected_size = HEADER_PREFIX_SIZE + language_count * 4 + entry_count * record_size
        stream.seek(0, os.SEEK_END)
        if stream.tell() != expected_size:
            raise ValueError(f"unexpected source size: got {stream.tell()}, expected {expected_size}")
        stream.seek(HEADER_PREFIX_SIZE + language_count * 4)

        translations = read_translations(translations_path, entry_count) if translations_path else {}
        new_header = struct.pack("<III", version, entry_count, language_count + 1)
        new_header += struct.pack(f"<{language_count + 1}I", *language_ids, new_language_id)
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

                    translated = translations.get(index)
                    if translated is None:
                        text_bytes, meta, expected_source, expected_signature = (
                            b"", (-1,) * 10, None, None
                        )
                    else:
                        text_bytes, meta, expected_source, expected_signature = translated

                    if expected_source is not None:
                        actual_source = original_record[:TEXT_SLOT_SIZE].split(b"\0", 1)[0].decode("cp1252")
                        if actual_source != expected_source:
                            raise ValueError(f"source text mismatch for translation id {index}")
                    key = original_record[TEXT_SLOT_SIZE:TEXT_SLOT_SIZE + KEY_SLOT_SIZE]
                    actual_signature = key.split(b"\0", 1)[0].decode("ascii", errors="strict")
                    if expected_signature is not None and actual_signature != expected_signature:
                        raise ValueError(f"format signature mismatch for translation id {index}")

                    if translated is not None:
                        argument_count = actual_signature.count("~")
                        decoded_translation = text_bytes.decode("ascii")
                        marker_count = decoded_translation.count("\x08")
                        if marker_count != argument_count:
                            raise ValueError(
                                f"translation id {index} has {marker_count} argument markers, "
                                f"but format signature {actual_signature!r} requires {argument_count}"
                            )
                        if any(meta[i] != i for i in range(argument_count)):
                            raise ValueError(f"translation id {index} must map arguments in source order")

                    text_slot = bytearray(TEXT_SLOT_SIZE)
                    text_slot[:len(text_bytes)] = text_bytes
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
    parser.add_argument("--source", type=Path, required=True,
                        help="player's original Data/language.ldb")
    parser.add_argument("--translations", type=Path, action="append", required=True,
                        help="UTF-8 TSV; repeat this option for multiple translation batches")
    parser.add_argument("--output", type=Path, required=True,
                        help="write a separate extended language.ldb")
    parser.add_argument("--language-id", type=int, default=DEFAULT_LANGUAGE_ID)
    args = parser.parse_args()
    count, translated = build_extended_language_ldb(
        args.source, args.output, args.translations, args.language_id
    )
    print(
        f"entries: {count}; Russian rows supplied: {translated}; language ID: {args.language_id}"
    )
    print(f"created: {args.output} ({args.output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
