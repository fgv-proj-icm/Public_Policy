from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INCLUDED_FILE = FINAL_DIR / "reading_corpus_final_curated_top100.csv"
EXCLUDED_FILE = FINAL_DIR / "bibliometric_removed_by_curated_filter.csv"

OUTPUT_INCLUDED = FINAL_DIR / "validation_curated_included_top30.csv"
OUTPUT_EXCLUDED = FINAL_DIR / "validation_curated_excluded_top30.csv"

RANDOM_STATE = 42

included = pd.read_csv(INCLUDED_FILE, low_memory=False)
excluded = pd.read_csv(EXCLUDED_FILE, low_memory=False)

included_sample = included.sample(n=min(30, len(included)), random_state=RANDOM_STATE).copy()
excluded_sample = excluded.sample(n=min(30, len(excluded)), random_state=RANDOM_STATE).copy()

for df in [included_sample, excluded_sample]:
    df["validation_label"] = ""
    df["validation_notes"] = ""
    df["reviewer"] = ""

included_sample.to_csv(OUTPUT_INCLUDED, index=False, encoding="utf-8-sig")
excluded_sample.to_csv(OUTPUT_EXCLUDED, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_INCLUDED}")
print(f"Arquivo salvo em: {OUTPUT_EXCLUDED}")
print(f"Amostra incluídos: {len(included_sample)}")
print(f"Amostra excluídos: {len(excluded_sample)}")