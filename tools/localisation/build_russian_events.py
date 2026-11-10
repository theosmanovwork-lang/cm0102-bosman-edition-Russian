#!/usr/bin/env python3
"""Build events_rus.cfg from events_eng.cfg and a Russian UTF-8 TSV."""
from __future__ import annotations
import argparse, csv, os, re
from collections import defaultdict
from pathlib import Path
SPECIAL = re.compile(r'<(?:p\d+c?|t|[Rr]f)>')
def encode_game_text(text: str) -> str:
    out=[]
    for ch in text:
        cp=ord(ch)
        if cp==0 or cp>0xFFFF: raise ValueError(f"unsupported event character U+{cp:04X}")
        out.append(ch if cp<0x80 and ch!="#" else f"#{cp:04X}#")
    return "".join(out)
def build(source: Path, translations_path: Path, output: Path):
    if source.resolve()==output.resolve(): raise ValueError("output must differ from source events file")
    with translations_path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        required={"event_id","event_occurrence","variant_index","source_game_en","source_report_en","game_text_ru","report_text_ru"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames): raise ValueError("event TSV lacks required columns")
        translations={}
        for row in reader:
            key=(int(row["event_id"]),int(row["event_occurrence"]),int(row["variant_index"]))
            if key in translations: raise ValueError(f"duplicate event key {key}")
            translations[key]=(row["source_game_en"],row["source_report_en"],row["game_text_ru"],row["report_text_ru"])
    lines=source.read_bytes().decode("cp1252").splitlines(keepends=True)
    occurrence=defaultdict(int); current_id=None; current_occ=0; variant=-1; used=set(); out=[]
    for line in lines:
        text=line.rstrip("\r\n"); nl=line[len(text):]
        if text.startswith("= "):
            current_id=int(text[2:].split(",",1)[0].strip()); current_occ=occurrence[current_id]; occurrence[current_id]+=1; variant=-1
            out.append(line); continue
        if text.startswith("> ") and current_id is not None:
            variant+=1; out.append(line); continue
        if current_id is not None and variant>=0 and text.startswith(("G ","R ")):
            tag,original=text[:2],text[2:]; key=(current_id,current_occ,variant); entry=translations.get(key)
            if entry is not None:
                sg,sr,rg,rr=entry; expected=sg if tag=="G " else sr; translated=rg if tag=="G " else rr
                if original!=expected: raise ValueError(f"source text mismatch for {key} {tag.strip()}")
                if SPECIAL.findall(original)!=SPECIAL.findall(translated): raise ValueError(f"placeholder mismatch for {key} {tag.strip()}")
                if original.count("|")!=translated.count("|"): raise ValueError(f"segment mismatch for {key}")
                out.append(tag+encode_game_text(translated)+nl); used.add(key); continue
        out.append(line)
    unused=set(translations)-used
    if unused: raise ValueError(f"translation keys not found: {sorted(unused)[:10]}")
    output.parent.mkdir(parents=True,exist_ok=True); tmp=output.with_name(output.name+".tmp")
    try:
        tmp.write_bytes("".join(out).encode("cp1252"))
        with tmp.open("rb") as f: os.fsync(f.fileno())
        tmp.replace(output)
    except Exception: tmp.unlink(missing_ok=True); raise
    return len(occurrence),len(used),len(translations)
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--source",type=Path,required=True); p.add_argument("--translations",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    events,translated,keys=build(a.source,a.translations,a.output); print(f"events: {events}; translated variants: {translated}/{keys}; output: {a.output}"); return 0
if __name__=="__main__": raise SystemExit(main())
