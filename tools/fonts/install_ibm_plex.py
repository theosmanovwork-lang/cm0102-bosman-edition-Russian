#!/usr/bin/env python3
"""Decode the OFL-licensed IBM Plex TTF files into a staged game's Data/FONTS."""
from __future__ import annotations

import argparse
import base64
import binascii
from pathlib import Path

FONTS = (
    "IBMPlexSans-Regular.ttf",
    "IBMPlexSans-Medium.ttf",
    "IBMPlexSans-SemiBold.ttf",
    "IBMPlexSans-Bold.ttf",
    "IBMPlexSansCondensed-Regular.ttf",
    "IBMPlexSansCondensed-Bold.ttf",
)
TTF_SIGNATURE = b"\x00\x01\x00\x00"


def decode_font(source: Path) -> bytes:
    try:
        encoded = b"".join(source.read_bytes().split())
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"{source}: invalid base64 font asset") from exc
    if not data.startswith(TTF_SIGNATURE):
        raise ValueError(f"{source}: not a TrueType sfnt file")
    if len(data) < 16_000:
        raise ValueError(f"{source}: implausibly small font file ({len(data)} bytes)")
    return data


def install(source_dir: Path, target_dir: Path) -> list[Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    installed = []
    for name in FONTS:
        source = source_dir / f"{name}.b64"
        output = target_dir / name
        data = decode_font(source)
        output.write_bytes(data)
        installed.append(output)
    licence = source_dir / "OFL.txt"
    if not licence.is_file():
        raise FileNotFoundError(f"missing font licence: {licence}")
    (target_dir / "OFL.txt").write_bytes(licence.read_bytes())
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    files = install(args.source, args.target)
    print(f"Installed {len(files)} IBM Plex TTF files in {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
