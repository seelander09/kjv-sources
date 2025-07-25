"""
convert.py — Transform raw_data.csv into a canonical JSONL dataset.
"""

import pandas as pd
import json
from pathlib import Path

# Resolve paths dynamically
HERE = Path(__file__).parent              # src/kjv_sources
PROJECT_ROOT = HERE.parent.parent         # kjv-sources/
INPUT_CSV = PROJECT_ROOT / "src" / "kjv_sources" / "raw_data.csv"
OUTPUT_JSONL = PROJECT_ROOT / "data" / "verses.jsonl"

def csv_to_jsonl(csv_path: Path, jsonl_path: Path):
    """
    Read raw_data.csv, transform rows into JSONL, and write to file.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found at {csv_path!r}")

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    with jsonl_path.open("w", encoding="utf-8") as out:
        for _, row in df.iterrows():
            record = {
                "id": f"{row['book']}_{row['chapter']}_{row['verse_num']}",
                "book": row["book"],
                "chapter": row["chapter"],
                "verse": row["verse_num"],
                "text": row["verse_text"],
                "source_tag": None
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    csv_to_jsonl(INPUT_CSV, OUTPUT_JSONL)
    print(f"✅ Converted {INPUT_CSV.name} → {OUTPUT_JSONL}")