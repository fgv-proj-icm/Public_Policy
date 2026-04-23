from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_clean.csv"
OUTPUT_FILE = FINAL_DIR / "unified_base_analysis_ready.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

if "citation_count_unified" not in df.columns:
    df["citation_count_unified"] = 0

df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
df["citation_count_log1p"] = (df["citation_count_unified"] + 1).map(lambda x: pd.np.log(x) if x > 0 else 0)

df["has_doi"] = df["doi_clean"].fillna("").astype(str).str.strip() != ""
df["has_abstract"] = df["abstract"].fillna("").astype(str).str.strip() != ""
df["has_authors"] = df["authors"].fillna("").astype(str).str.strip() != ""
df["has_journal"] = df["journal_clean"].fillna("").astype(str).str.strip() != ""
df["journal_missing_flag"] = ~df["has_journal"]

df["language_clean"] = df["language"].fillna("").astype(str).str.strip().str.lower()
df["language_clean"] = df["language_clean"].replace({"": "nd", "nan": "nd", "n/d": "nd"})

df["record_id"] = range(1, len(df) + 1)

keep_cols_first = [
    "record_id",
    "source",
    "source_file",
    "title",
    "title_clean",
    "doi",
    "doi_clean",
    "publication_year",
    "year_clean",
    "journal",
    "journal_clean",
    "type",
    "type_clean",
    "language",
    "language_clean",
    "citation_count_unified",
    "citation_count_log1p",
    "has_doi",
    "has_abstract",
    "has_authors",
    "has_journal",
    "journal_missing_flag",
]

other_cols = [c for c in df.columns if c not in keep_cols_first]
df = df[keep_cols_first + other_cols]

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(f"Total final: {len(df)}")
