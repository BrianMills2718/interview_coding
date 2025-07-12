"""Batch-clean Microsoft Teams transcripts.

For every .docx file in data/raw/, generate:
1. Tidy CSV with columns uid, transcript_id, start_ms, end_ms, speaker, line_idx, text
2. Readable TXT where each line is: [uid] SPEAKER: text

Outputs are written to data/processed/.
"""
from __future__ import annotations

import re
from pathlib import Path
import pandas as pd
from docx import Document
from dotenv import load_dotenv
import os

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = Path(os.getenv("RAW_DIR", ROOT / "data" / "raw"))
PROC_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
PROC_DIR.mkdir(parents=True, exist_ok=True)

speaker_line_re = re.compile(r"^(.*?)\s{2,}(\d+:\d{2}(?::\d{2})?)\s+(.*)$")
system_line_re = re.compile(r"^(Recording|Meeting|.*started transcription)", re.I)

def hhmmss_to_ms(hhmmss: str) -> int:
    parts = list(map(int, hhmmss.split(":")))
    if len(parts) == 2:
        m, s = parts
        return (m * 60 + s) * 1000
    h, m, s = parts
    return (h * 3600 + m * 60 + s) * 1000


def slugify(path: Path) -> str:
    stem = path.stem
    slug = re.sub(r"[^A-Za-z0-9]+", "_", stem).upper().strip("_")
    return slug  # use full (sanitized) filename


def process_docx(docx_path: Path) -> None:
    slug = slugify(docx_path)
    doc = Document(str(docx_path))
    rows = []
    dup_check: set[tuple[str, int]] = set()

    for idx, p in enumerate(doc.paragraphs):
        raw = p.text.strip()
        if not raw or system_line_re.match(raw):
            continue
        m = speaker_line_re.match(raw)
        if not m:
            continue
        speaker, ts, text = m.groups()
        start_ms = hhmmss_to_ms(ts)
        key = (speaker.strip(), start_ms)
        if key in dup_check:
            continue  # skip duplicates silently
        dup_check.add(key)
        uid = f"{slug}_{start_ms:07d}"
        rows.append({
            "uid": uid,
            "transcript_id": slug,
            "start_ms": start_ms,
            "end_ms": None,
            "speaker": speaker.strip(),
            "line_idx": idx,
            "text": text.strip(),
        })

    if not rows:
        print(f"No speaker lines found in {docx_path.name} – skipping")
        return

    df = pd.DataFrame(rows)
    csv_path = PROC_DIR / f"{slug}_tidy.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote {len(df)} rows -> {csv_path.relative_to(ROOT)}")

    # Write human-readable txt
    txt_path = PROC_DIR / f"{slug}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(f"[{r['uid']}] {r['speaker']}: {r['text']}\n")
    print(f"Wrote txt → {txt_path.relative_to(ROOT)}")


def main() -> None:
    docx_files = list(RAW_DIR.glob("*.docx"))
    if not docx_files:
        print(f"No .docx transcripts found in {RAW_DIR}")
        return
    for docx in docx_files:
        process_docx(docx)

if __name__ == "__main__":
    main() 