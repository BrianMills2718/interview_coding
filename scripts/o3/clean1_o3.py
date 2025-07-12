"""
CLEAN_TEAMS_TRANSCRIPT_V1.1
PURPOSE: PARSE A TEAMS .DOCX, DROP SYSTEM LINES, ASSERT UNIQUE SPEAKER+TIMESTAMP,
         GENERATE COMPOSITE UID, WRITE TIDY CSV FOR LLM TAGGING
"""

# ------- USER CONFIGURATION -----------------------------------------------
# Path handling now uses project-relative directories and optional .env overrides.
# Environment vars (with defaults):
#   RAW_DIR        → location of original .docx transcripts  (default: <proj>/data/raw)
#   PROCESSED_DIR  → location for generated CSV outputs      (default: <proj>/data/processed)

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR       = Path(__file__).resolve().parents[2]
RAW_DIR        = Path(os.getenv("RAW_DIR", ROOT_DIR / "data" / "raw"))
PROCESSED_DIR  = Path(os.getenv("PROCESSED_DIR", ROOT_DIR / "data" / "processed"))

# Ensure output directory exists
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# --- File-specific configuration -----------------------------------------
FILE_SLUG  = "FG07"  # ← Short identifier for this transcript
DOCX_FILE  = RAW_DIR / "Focus Group on AI and Methods 7_7.docx"
OUT_CSV    = PROCESSED_DIR / f"{FILE_SLUG}_tidy.csv"
# --------------------------------------------------------------------------

import re, pandas as pd
from docx import Document

# -- UTILITY ---------------------------------------------------------------
def hhmmss_to_ms(hhmmss: str) -> int:
    """Convert 'H:MM:SS' or 'M:SS' to integer milliseconds."""
    parts = list(map(int, hhmmss.split(":")))
    if len(parts) == 2:   # M:SS
        m, s = parts
        return (m * 60 + s) * 1000
    h, m, s = parts       # H:MM:SS
    return (h * 3600 + m * 60 + s) * 1000
# --------------------------------------------------------------------------

doc        = Document(str(DOCX_FILE))
rows, dup_check = [], set()

speaker_line_re = re.compile(r"^(.*?)\s{2,}(\d+:\d{2}(?::\d{2})?)\s+(.*)$")
system_line_re  = re.compile(r"^(Recording|Meeting|.*started transcription)", re.I)

for idx, p in enumerate(doc.paragraphs):
    raw = p.text.strip()
    if not raw or system_line_re.match(raw):
        continue  # skip noise
    m = speaker_line_re.match(raw)
    if not m:         # not a well-formed speaker line
        continue
    speaker, ts, text = m.groups()
    start_ms = hhmmss_to_ms(ts)
    # ----- DUPLICATE VALIDATION ------------------------------------------
    key = (speaker.strip(), start_ms)
    if key in dup_check:
        raise ValueError(f"Duplicate speaker+timestamp at paragraph {idx}: "
                         f"{speaker} @ {ts}")
    dup_check.add(key)
    # ----- UID CONSTRUCTION ----------------------------------------------
    uid = f"{FILE_SLUG}_{start_ms:07d}_{idx:05d}"
    rows.append(dict(uid=uid,
                     transcript_id=FILE_SLUG,
                     start_ms=start_ms,
                     end_ms=None,   # Teams lacks explicit end times
                     speaker=speaker.strip(),
                     line_idx=idx,
                     text=text.strip()))

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)
print(f"Wrote {len(df)} rows to {OUT_CSV}")
