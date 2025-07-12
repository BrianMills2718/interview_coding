# TRANSCRIBE / AUTO-CHUNK / IN-MEMORY  ·  V2.1
#
# CHANGE v2.0 → v2.1
# • Assign a .name attribute to each BytesIO slice so the API
#   sees a legal file-name with a supported extension (.wav).
# • Cosmetic: use enumerate() for prettier chunk names.

from pathlib import Path
from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment          # needs ffmpeg in PATH
import os

SRC      = Path(r"C:\Users\bmills\Downloads\kitgreen_wsj_june132025_15868765680_0_1749835242091.mp3")
API_KEY  = os.getenv("OPENAI_API_KEY", "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")
CHUNK_MS = 10 * 60 * 1000              # 10-minute windows
client   = OpenAI(api_key=API_KEY)

def wav_mono_16k(seg: AudioSegment, chunk_no: int) -> BytesIO:
    """Re-encode to 16-kHz mono WAV and label with .name attr."""
    seg = seg.set_channels(1).set_frame_rate(16_000)
    buf = BytesIO()
    seg.export(buf, format="wav")      # pcm_s16le
    buf.seek(0)
    buf.name = f"chunk_{chunk_no:03d}.wav"   # 👈 *critical line*
    return buf

audio = AudioSegment.from_file(SRC)
subs  = []

for i, start in enumerate(range(0, len(audio), CHUNK_MS), 1):
    wav_buf = wav_mono_16k(audio[start:start + CHUNK_MS], i)
    resp    = client.audio.transcriptions.create(
        file            = wav_buf,
        model           = "gpt-4o-transcribe",
        response_format = "text",
    )
    subs.append(resp.strip())

out = SRC.with_suffix(".txt")
out.write_text("\n".join(subs), encoding="utf-8")
print(f"✅ transcript saved → {out}")
