from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

FOCUS_FILE = FINAL_DIR / "focus_corpus_policy_admin.csv"
FINAL_FILE = FINAL_DIR / "bibliometric_corpus_final.csv"

OUTPUT_INCLUDED = FINAL_DIR / "validation_sample_included.csv"
OUTPUT_EXCLUDED = FINAL_DIR / "validation_sample_excluded.csv"

RANDOM_STATE = 42
SAMPLE_SIZE = 50


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def build_key(row: pd.Series) -> str:
    doi = norm_text(row.get("doi_clean", ""))
    title = norm_text(row.get("title_clean", ""))
    year = str(row.get("publication_year", "")).strip()
    journal = norm_text(row.get("journal_clean", ""))

    if doi:
        return f"doi::{doi}"
    return f"txt::{title}::{year}::{journal}"


focus = pd.read_csv(FOCUS_FILE, low_memory=False)
final = pd.read_csv(FINAL_FILE, low_memory=False)

for df in [focus, final]:
    for col in ["doi_clean", "title_clean", "journal_clean", "publication_year"]:
        if col not in df.columns:
            df[col] = ""

focus["record_key"] = focus.apply(build_key, axis=1)
final["record_key"] = final.apply(build_key, axis=1)

final_keys = set(final["record_key"].tolist())

included_pool = focus[focus["record_key"].isin(final_keys)].copy()
excluded_pool = focus[~focus["record_key"].isin(final_keys)].copy()

included_sample = included_pool.sample(
    n=min(SAMPLE_SIZE, len(included_pool)),
    random_state=RANDOM_STATE,
).copy()

excluded_sample = excluded_pool.sample(
    n=min(SAMPLE_SIZE, len(excluded_pool)),
    random_state=RANDOM_STATE,
).copy()

for df in [included_sample, excluded_sample]:
    df["validation_label"] = ""
    df["validation_notes"] = ""
    df["reviewer"] = ""

included_sample.to_csv(OUTPUT_INCLUDED, index=False, encoding="utf-8-sig")
excluded_sample.to_csv(OUTPUT_EXCLUDED, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_INCLUDED}")
print(f"Arquivo salvo em: {OUTPUT_EXCLUDED}")
print(f"Pool incluídos: {len(included_pool)}")
print(f"Pool excluídos: {len(excluded_pool)}")
print(f"Amostra incluídos: {len(included_sample)}")
print(f"Amostra excluídos: {len(excluded_sample)}")