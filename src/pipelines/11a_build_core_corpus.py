from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_v2.csv"
OUTPUT_MASTER = FINAL_DIR / "unified_base_analysis_ready_v3.csv"
OUTPUT_CORE_BROAD = FINAL_DIR / "core_corpus_broad.csv"
OUTPUT_CORE_JOURNAL = FINAL_DIR / "core_corpus_journal.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

for col in [
    "relevance_flag",
    "primary_type",
    "journal_clean",
    "doi_clean",
    "has_journal",
    "has_authors",
    "has_abstract",
]:
    if col not in df.columns:
        df[col] = ""

df["relevance_flag"] = pd.to_numeric(df["relevance_flag"], errors="coerce").fillna(0).astype(int)

df["primary_type"] = df["primary_type"].fillna("nd").astype(str).str.strip().str.lower()
df["journal_clean"] = df["journal_clean"].fillna("").astype(str).str.strip().str.lower()

df["has_journal"] = df["has_journal"].fillna(False).astype(bool)
df["has_authors"] = df["has_authors"].fillna(False).astype(bool)
df["has_abstract"] = df["has_abstract"].fillna(False).astype(bool)

SUSPECT_JOURNAL_HINTS = [
    "lepidopterología",
    "institutional repositories database",
    "repository",
    "ssrn",
    "dialnet",
    "la referencia",
    "zenodo",
]

def is_suspect_journal(text: str) -> bool:
    return any(hint in text for hint in SUSPECT_JOURNAL_HINTS)

df["journal_suspect_flag"] = df["journal_clean"].apply(is_suspect_journal)

df["metadata_quality_score"] = (
    df["doi_clean"].fillna("").astype(str).str.strip().ne("").astype(int)
    + df["has_journal"].astype(int)
    + df["has_authors"].astype(int)
    + df["has_abstract"].astype(int)
)

# Corpus amplo: relevante + tipo principal adequado + sem periódico suspeito
df["core_broad_flag"] = (
    (df["relevance_flag"] == 1)
    & (df["primary_type"].isin(["article", "review"]))
    & (~df["journal_suspect_flag"])
)

# Corpus estrito para análises editoriais/periódicos
df["core_journal_flag"] = df["core_broad_flag"] & (df["has_journal"])

df.to_csv(OUTPUT_MASTER, index=False, encoding="utf-8-sig")

core_broad = df[df["core_broad_flag"]].copy()
core_journal = df[df["core_journal_flag"]].copy()

core_broad.to_csv(OUTPUT_CORE_BROAD, index=False, encoding="utf-8-sig")
core_journal.to_csv(OUTPUT_CORE_JOURNAL, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_MASTER}")
print(f"Arquivo salvo em: {OUTPUT_CORE_BROAD}")
print(f"Arquivo salvo em: {OUTPUT_CORE_JOURNAL}")
print(f"Total base mestre: {len(df)}")
print(f"Total core broad: {len(core_broad)}")
print(f"Total core journal: {len(core_journal)}")
