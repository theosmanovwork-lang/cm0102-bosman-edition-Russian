import csv
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools/localisation/build_extended_language_ldb.py"
SPEC = importlib.util.spec_from_file_location("build_extended_language_ldb", MODULE)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)


class ExtendedLanguageTests(unittest.TestCase):
    def source(self, path):
        ids = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        header = struct.pack("<III10I", 1, 2, 10, *ids)
        size = 2048 + 30 + 9 * (2048 + 40)
        records = []
        for text, signature in [("Hello <%s - Name>", "%s~"), ("No marker", "")]:
            rec = bytearray(size)
            rec[:len(text)] = text.encode("cp1252")
            key = (signature + "\0").encode("ascii")
            rec[2048:2048 + len(key)] = key
            records.append(bytes(rec))
        data = header + b"".join(records)
        path.write_bytes(data)
        return data

    def tsv(self, path, rows):
        fields = ["id", "source_en", "format_signature", "text_ru", "grammar_meta_ru"]
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    def row(self, id, text, source, signature):
        return {"id": id, "text_ru": text, "source_en": source,
                "format_signature": signature,
                "grammar_meta_ru": "[0,-1,-1,-1,-1,-1,-1,-1,-1,-1]" if signature else "[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]"}

    def test_appends_id_13_and_preserves_original_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/"source.ldb"; out=root/"out.ldb"; tsv=root/"ru.tsv"
            original=self.source(src)
            self.tsv(tsv,[self.row(0,"Привет, \x08","Hello <%s - Name>","%s~")])
            self.assertEqual(builder.build_extended_language_ldb(src,out,tsv),(2,1))
            result=out.read_bytes()
            self.assertEqual(struct.unpack_from("<III",result),(1,2,11))
            self.assertEqual(struct.unpack_from("<11I",result,12),(0,2,3,4,5,6,7,8,9,10,13))
            old=2048+30+9*(2048+40); new=old+2048+40
            self.assertEqual(result[56:56+old],original[52:52+old])
            self.assertEqual(result[56+old:56+old+2048].split(b"\0",1)[0],
                             b"#041F##0440##0438##0432##0435##0442#, \x08")
            self.assertEqual(src.read_bytes(),original)
            self.assertEqual(len(result),56+2*new)

    def test_merges_multiple_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/"source.ldb"; out=root/"out.ldb"; a=root/"a.tsv"; b=root/"b.tsv"
            self.source(src)
            self.tsv(a,[self.row(0,"Привет, \x08","Hello <%s - Name>","%s~")])
            self.tsv(b,[self.row(1,"Без маркера","No marker","")])
            self.assertEqual(builder.build_extended_language_ldb(src,out,[a,b]),(2,2))

    def test_rejects_duplicate_ids_across_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/"source.ldb"; out=root/"out.ldb"; a=root/"a.tsv"; b=root/"b.tsv"
            self.source(src); row=self.row(0,"Привет, \x08","Hello <%s - Name>","%s~")
            self.tsv(a,[row]); self.tsv(b,[row])
            with self.assertRaisesRegex(ValueError,"duplicate translation id"):
                builder.build_extended_language_ldb(src,out,[a,b])

    def test_rejects_source_signature_and_argument_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/"source.ldb"; out=root/"out.ldb"; tsv=root/"ru.tsv"
            self.source(src)
            self.tsv(tsv,[self.row(0,"Привет, \x08","Wrong","%s~")])
            with self.assertRaisesRegex(ValueError,"source text mismatch"):
                builder.build_extended_language_ldb(src,out,tsv)
            self.tsv(tsv,[self.row(0,"Привет","Hello <%s - Name>","%s~")])
            with self.assertRaisesRegex(ValueError,"argument markers"):
                builder.build_extended_language_ldb(src,out,tsv)
            self.tsv(tsv,[self.row(0,"Привет, \x08","Hello <%s - Name>","%d~")])
            with self.assertRaisesRegex(ValueError,"format signature mismatch"):
                builder.build_extended_language_ldb(src,out,tsv)

    def test_id_capacity_and_no_overwrite(self):
        builder.check_language_capacity(18,1)
        with self.assertRaisesRegex(ValueError,"stores 19"):
            builder.check_language_capacity(19,1)
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"source.ldb"; original=self.source(src)
            with self.assertRaisesRegex(ValueError,"must differ"):
                builder.build_extended_language_ldb(src,src,None)
            self.assertEqual(src.read_bytes(),original)

    def test_rejects_non_bmp_and_long_text(self):
        with self.assertRaisesRegex(ValueError,"16-bit"):
            builder.encode_game_text("😀")
        with self.assertRaisesRegex(ValueError,"slot limit"):
            builder.encode_game_text("Ж"*400)


if __name__ == "__main__":
    unittest.main()
