import csv
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools/localisation/build_russian_lng.py"
SPEC = importlib.util.spec_from_file_location("build_russian_lng", MODULE)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)

class RussianLngTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "eng.lng"
        self.tsv = self.root / "ru.tsv"
        self.output = self.root / "rus.lng"

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def slot(text, size):
        return text.encode("cp1252").ljust(size, b"\0")

    def write_source(self):
        counts = (0, 1, 0, 1, 0, 0, 0, 0)
        continent = bytearray(0xBA)
        continent[:51] = self.slot("Africa", 51)
        continent[51] = 0xBA
        nation = bytearray(0x6D)
        nation[:51] = self.slot("Afghanistan", 51)
        nation[51] = 0xF0
        nation[52:78] = self.slot("Afghanistan", 26)
        nation[78] = 0xA7
        nation[79:109] = bytes(range(30))
        data = struct.pack("<8i", *counts) + continent + nation
        self.source.write_bytes(data)
        return data

    def write_tsv(self, rows):
        fields = ["section", "row", "source_en", "source_short_en", "name_ru", "short_name_ru"]
        with self.tsv.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    def test_translates_names_and_keeps_source_structure(self):
        original = self.write_source()
        self.write_tsv([
            {"section": "continents", "row": 0, "source_en": "Africa", "source_short_en": "", "name_ru": "Африка", "short_name_ru": ""},
            {"section": "nations", "row": 0, "source_en": "Afghanistan", "source_short_en": "Afghanistan", "name_ru": "Афган.", "short_name_ru": "Афг."},
        ])
        self.assertEqual(builder.build_russian_lng(self.source, self.tsv, self.output), (2, 1))
        result = self.output.read_bytes()
        self.assertEqual(len(result), len(original))
        self.assertEqual(result[:32], original[:32])
        self.assertEqual(self.source.read_bytes(), original)
        self.assertIn(b"#0410##0444##0440##0438##043A##0430#", result)
        self.assertIn(b"#0410##0444##0433##0430##043D#.", result)
        self.assertIn(b"#0410##0444##0433#.", result)
        self.assertEqual(result[32 + 51], 0xBA)
        self.assertEqual(result[32 + 0xBA + 51], 0xF0)
        nation_at = 32 + 0xBA
        self.assertEqual(result[nation_at + 78], 0xA7)
        self.assertEqual(result[nation_at + 79:nation_at + 109], bytes(range(30)))

    def test_rejects_source_mismatch_and_slot_overflow(self):
        self.write_source()
        self.write_tsv([{"section": "nations", "row": 0, "source_en": "Wrong", "source_short_en": "Afghanistan", "name_ru": "Афган.", "short_name_ru": ""}])
        with self.assertRaisesRegex(ValueError, "source name mismatch"):
            builder.build_russian_lng(self.source, self.tsv, self.output)
        self.write_tsv([{"section": "nations", "row": 0, "source_en": "Afghanistan", "source_short_en": "Afghanistan", "name_ru": "А" * 9, "short_name_ru": ""}])
        with self.assertRaisesRegex(ValueError, "fixed slot"):
            builder.build_russian_lng(self.source, self.tsv, self.output)

    def test_rejects_short_slot_on_section_without_short_name(self):
        self.write_source()
        self.write_tsv([{"section": "continents", "row": 0, "source_en": "Africa", "source_short_en": "", "name_ru": "Африка", "short_name_ru": "Аф."}])
        with self.assertRaisesRegex(ValueError, "no short-name slot"):
            builder.build_russian_lng(self.source, self.tsv, self.output)

    def test_rejects_overwrite_and_out_of_range(self):
        original = self.write_source()
        self.write_tsv([{"section": "nations", "row": 100, "source_en": "Afghanistan", "source_short_en": "Afghanistan", "name_ru": "Афган.", "short_name_ru": ""}])
        with self.assertRaisesRegex(ValueError, "outside"):
            builder.build_russian_lng(self.source, self.tsv, self.output)
        with self.assertRaisesRegex(ValueError, "differ from source"):
            builder.build_russian_lng(self.source, self.tsv, self.source)
        self.assertEqual(self.source.read_bytes(), original)

if __name__ == "__main__":
    unittest.main()
