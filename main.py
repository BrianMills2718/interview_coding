"""Entry point for running the Sonnet analysis pipeline."""

import asyncio
from pathlib import Path
import json

from src.analysis.pipeline import AnalysisPipeline


async def run() -> None:
    pipeline = AnalysisPipeline("config/codebook.yaml")
    transcripts_dir = Path("data/processed")
    for txt_file in transcripts_dir.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
        result = await pipeline.process_transcript(txt_file.stem, text)
        out_path = Path("outputs/sonnet") / f"{txt_file.stem}_sonnet.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f_out:
            json.dump(result, f_out, indent=2)
        print(f"Processed {txt_file.name} → {out_path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    asyncio.run(run()) 