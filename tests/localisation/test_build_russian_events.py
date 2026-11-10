import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools/localisation/build_russian_events.py"
SPEC = importlib.util.spec_from_file_location("build_russian_events", MODULE)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)


class RussianEventsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "events_eng.cfg"
        self.tsv = self.root / "ru.tsv"
        self.output = self.root / "events_rus.cfg"
        self.source.write_bytes(
            b"# comment\r\n= 1, 2, 0, 0, 0, 1, 0, 1, 0\r\n"
            b"> 1, 900, goal.wav\r\nG <p1> scores!\r\nR <p1> scored!\r\n"
            b"> 1, 700,\r\nG <Rf> awards <t> a free kick\r\nR <Rf> awarded <t> a free kick\r\n"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def write_rows(self, rows):
        fields = ["event_id", "event_occurrence", "variant_index", "source_game_en",
                  "source_report_en", "game_text_ru", "report_text_ru"]
        with self.tsv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    def test_preserves_event_structure_and_escapes_cyrillic(self):
        rows = [{
            "event_id": 1, "event_occurrence": 0, "variant_index": 0,
            "source_game_en": "<p1> scores!", "source_report_en": "<p1> scored!",
            "game_text_ru": "Гол забивает <p1>!", "report_text_ru": "<p1> забил!",
        }, {
            "event_id": 1, "event_occurrence": 0, "variant_index": 1,
            "source_game_en": "<Rf> awards <t> a free kick",
            "source_report_en": "<Rf> awarded <t> a free kick",
            "game_text_ru": "<Rf> назначает <t> штрафной",
            "report_text_ru": "<Rf> назначил <t> штрафной",
        }]
        self.write_rows(rows)
        original = self.source.read_bytes()
        self.assertEqual(builder.build(self.source, self.tsv, self.output), (1, 2, 2))
        result = self.output.read_bytes()
        self.assertIn(b"G #0413##043E##043B# #0437##0430##0431##0438##0432##0430##0435##0442# <p1>!", result)
        self.assertIn(b"> 1, 900, goal.wav\r\n", result)
        self.assertIn(b"# comment\r\n", result)
        self.assertEqual(self.source.read_bytes(), original)

    def test_rejects_changed_placeholders_and_wrong_source(self):
        row = {
            "event_id": 1, "event_occurrence": 0, "variant_index": 0,
            "source_game_en": "<p1> scores!", "source_report_en": "<p1> scored!",
            "game_text_ru": "Игрок забивает!", "report_text_ru": "<p1> забил!",
        }
        self.write_rows([row])
        with self.assertRaisesRegex(ValueError, "placeholder mismatch"):
            builder.build(self.source, self.tsv, self.output)
        row["game_text_ru"] = "Забил <p1>!"
        row["source_game_en"] = "not the source"
        self.write_rows([row])
        with self.assertRaisesRegex(ValueError, "source text mismatch"):
            builder.build(self.source, self.tsv, self.output)

    def test_rejects_unknown_keys_and_overwrite(self):
        self.write_rows([{
            "event_id": 999, "event_occurrence": 0, "variant_index": 0,
            "source_game_en": "x", "source_report_en": "x",
            "game_text_ru": "x", "report_text_ru": "x",
        }])
        with self.assertRaisesRegex(ValueError, "not found"):
            builder.build(self.source, self.tsv, self.output)
        with self.assertRaisesRegex(ValueError, "differ from source"):
            builder.build(self.source, self.tsv, self.source)


if __name__ == "__main__":
    unittest.main()
