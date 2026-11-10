import base64
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools" / "fonts" / "install_ibm_plex.py"
SPEC = importlib.util.spec_from_file_location("install_ibm_plex", MODULE)
installer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(installer)


class FontInstallerTests(unittest.TestCase):
    def test_decodes_a_true_type_sfnt(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "font.ttf.b64"
            raw = installer.TTF_SIGNATURE + bytes(16_000)
            encoded = base64.b64encode(raw).decode("ascii")
            source.write_text(encoded[:24] + "\n" + encoded[24:], encoding="ascii")
            self.assertTrue(installer.decode_font(source).startswith(b"\x00\x01\x00\x00"))

    def test_rejects_non_font_data(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.ttf.b64"
            source.write_text("bm90IGEgZm9udA==", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "not a TrueType"):
                installer.decode_font(source)

    def test_rejects_invalid_base64(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.ttf.b64"
            source.write_text("!!!", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "invalid base64"):
                installer.decode_font(source)


if __name__ == "__main__":
    unittest.main()
