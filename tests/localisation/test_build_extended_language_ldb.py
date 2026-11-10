import csv
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "tools" / "localisation"
sys.path.insert(0, str(MODULE_DIR))

from build_extended_language_ldb import (
    DEFAULT_LANGUAGE_ID,
    LANGUAGE_ID_CAPACITY,
    META_SIZE,
    ORIGINAL_LANG_COUNT,
    TEXT_SLOT_SIZE,
    build_extended_language_ldb,
    check_language_capacity,
    encode_game_text,
)


class ExtendedLanguageLdbTests(unittest.TestCase):
    def make_source(self, path: Path) -> bytes:
        ids = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        header = struct.pack("<III10I", 1, 1, ORIGINAL_LANG_COUNT, *ids)
        record_size = TEXT_SLOT_SIZE + 30 + (ORIGINAL_LANG_COUNT - 1) * (TEXT_SLOT_SIZE + META_SIZE)
        record = bytearray(record_size)
        record[:5] = b"Hello"
        source = header + record
        path.write_bytes(source)
        return source

    def test_adds_language_13_and_preserves_every_old_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output, translations = root / "language.ldb", root / "extended.ldb", root / "ru.tsv"
            original = self.make_source(source)
            with translations.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=["id", "text_ru", "grammar_meta_ru"], delimiter="\t"
                )
                writer.writeheader()
                writer.writerow(
                    {"id": 0, "text_ru": "Привет\n%s", "grammar_meta_ru": "[0,1,2,3,4,5,6,7,8,9]"}
                )

            entries, supplied = build_extended_language_ldb(source, output, translations)
            result = output.read_bytes()
            self.assertEqual((entries, supplied), (1, 1))
            self.assertEqual(struct.unpack_from("<III", result), (1, 1, 11))
            self.assertEqual(
                struct.unpack_from("<11I", result, 12), (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13)
            )
            old_record_size = TEXT_SLOT_SIZE + 30 + 9 * (TEXT_SLOT_SIZE + META_SIZE)
            new_record_size = old_record_size + TEXT_SLOT_SIZE + META_SIZE
            self.assertEqual(
                result[56:56 + old_record_size],
                original[52:52 + old_record_size],
            )
            slot = result[56 + old_record_size:56 + old_record_size + TEXT_SLOT_SIZE]
            self.assertEqual(
                slot.split(b"\0", 1)[0],
                b"#041F##0440##0438##0432##0435##0442#\n%s",
            )
            self.assertEqual(
                struct.unpack_from("<10i", result, 56 + old_record_size + TEXT_SLOT_SIZE),
                tuple(range(10)),
            )
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(len(result), 56 + new_record_size)

    def test_blank_translation_is_empty_with_minus_one_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "source.ldb", root / "extended.ldb"
            self.make_source(source)
            build_extended_language_ldb(source, output, None)
            result = output.read_bytes()
            old_record_size = TEXT_SLOT_SIZE + 30 + 9 * (TEXT_SLOT_SIZE + META_SIZE)
            slot_at = 56 + old_record_size
            self.assertEqual(result[slot_at:slot_at + TEXT_SLOT_SIZE], b"\0" * TEXT_SLOT_SIZE)
            self.assertEqual(
                struct.unpack_from("<10i", result, slot_at + TEXT_SLOT_SIZE), (-1,) * 10
            )

    def test_existing_runtime_id_table_capacity_is_19(self):
        self.assertEqual(LANGUAGE_ID_CAPACITY, 19)
        check_language_capacity(18, 1)
        with self.assertRaisesRegex(ValueError, "19 slots"):
            check_language_capacity(19, 1)

    def test_rejects_output_over_original_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "language.ldb"
            original = self.make_source(source)
            with self.assertRaisesRegex(ValueError, "must differ"):
                build_extended_language_ldb(source, source, None)
            self.assertEqual(source.read_bytes(), original)

    def test_rejects_astral_unicode_and_overlong_text(self):
        with self.assertRaisesRegex(ValueError, "16-bit"):
            encode_game_text("⚽")
        with self.assertRaisesRegex(ValueError, "slot limit"):
            encode_game_text("Ж" * 400)

    def test_rejects_duplicate_and_out_of_range_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output, translations = root / "source.ldb", root / "out.ldb", root / "ru.tsv"
            self.make_source(source)
            for rows, message in [
                ([{"id": 0, "text_ru": "A"}, {"id": 0, "text_ru": "B"}], "duplicate"),
                ([{"id": 1, "text_ru": "B"}], "outside"),
            ]:
                with translations.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=["id", "text_ru"], delimiter="\t")
                    writer.writeheader()
                    writer.writerows(rows)
                with self.assertRaisesRegex(ValueError, message):
                    build_extended_language_ldb(source, output, translations)


if __name__ == "__main__":
    unittest.main()
