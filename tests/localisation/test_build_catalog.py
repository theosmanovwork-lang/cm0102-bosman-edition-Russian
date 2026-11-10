import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools" / "localisation" / "build_catalog.py"
SPEC = importlib.util.spec_from_file_location("build_catalog", MODULE)
build_catalog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_catalog)


class CatalogTests(unittest.TestCase):
    def test_cyrillic_uses_four_digit_t2k_escapes(self):
        self.assertEqual(build_catalog.encode_t2k("Ёж"), "#0401##0436#")

    def test_latin_and_punctuation_stay_readable(self):
        self.assertEqual(build_catalog.encode_t2k("CM 01/02 — Русский"), "CM 01/02 #2014# #0420##0443##0441##0441##043A##0438##0439#")

    def test_printf_argument_types_and_order_are_preserved(self):
        self.assertEqual(
            build_catalog.printf_signature("Signed %s: %d"),
            build_catalog.printf_signature("%s — %d"),
        )
        self.assertNotEqual(
            build_catalog.printf_signature("Signed %s: %d"),
            build_catalog.printf_signature("Signed %d: %s"),
        )

    def test_repository_catalog_is_valid_and_generated_header_is_ascii(self):
        rows = build_catalog.read_catalog(ROOT / "locales" / "ru-RU.tsv")
        self.assertEqual(len(rows), 350)
        header = build_catalog.render_header(rows)
        header.encode("ascii")
        self.assertIn("#041D#", header)
        committed = (ROOT / "src" / "recomp_rt" / "win" / "russian_catalog.h").read_text(encoding="ascii")
        self.assertEqual(header, committed)

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.tsv"
            source.write_text(
                "id\tsource\ttranslation\tcontext\n"
                "same\tOne\tОдин\tTest\n"
                "same\tTwo\tДва\tTest\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate id"):
                build_catalog.read_catalog(source)


if __name__ == "__main__":
    unittest.main()
