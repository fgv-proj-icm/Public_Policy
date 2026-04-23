from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "focus_corpus_policy_admin.csv"
OUTPUT_STRICT = FINAL_DIR / "focus_corpus_strict.csv"
OUTPUT_STRICT_TOP200 = FINAL_DIR / "focus_corpus_strict_top200.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

def to_bool(series: pd.Series) -> pd.Series:
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

for col in ["has_journal", "has_authors", "has_abstract", "journal_suspect_flag"]:
    if col not in df.columns:
        df[col] = False

for col in ["title_clean", "journal_clean", "primary_type", "citation_count_unified"]:
    if col not in df.columns:
        df[col] = ""

df["has_journal"] = to_bool(df["has_journal"])
df["has_authors"] = to_bool(df["has_authors"])
df["has_abstract"] = to_bool(df["has_abstract"])
df["journal_suspect_flag"] = to_bool(df["journal_suspect_flag"])

df["title_clean"] = df["title_clean"].fillna("").astype(str).str.strip().str.lower()
df["journal_clean"] = df["journal_clean"].fillna("").astype(str).str.strip().str.lower()
df["primary_type"] = df["primary_type"].fillna("nd").astype(str).str.strip().str.lower()
df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)

STRICT_HINTS = [
    "judicial administration",
    "court administration",
    "judicial governance",
    "court governance",
    "judicial reform",
    "reforma judicial",
    "reforma do judiciário",
    "política judiciária",
    "políticas judiciárias",
    "administração judiciária",
    "governança judicial",
    "conselho nacional de justiça",
    "court management",
    "judicial management",
    "case management",
    "judicial performance",
    "court performance",
    "judicial efficiency",
    "court efficiency",
    "e-justice",
    "digital justice",
    "smart courts",
]

def has_hint(text: str) -> bool:
    return any(h in text for h in STRICT_HINTS)

df["strict_title_flag"] = (
    df["title_clean"].apply(has_hint)
    | df["journal_clean"].apply(has_hint)
)

df["strict_metadata_score"] = (
    df["has_journal"].astype(int)
    + df["has_authors"].astype(int)
    + df["has_abstract"].astype(int)
)

strict = df[
    (df["primary_type"].isin(["article", "review"]))
    & (~df["journal_suspect_flag"])
    & (df["has_journal"])
    & (df["strict_title_flag"])
].copy()

strict = strict.sort_values(
    by=["strict_metadata_score", "citation_count_unified", "publication_year"],
    ascending=[False, False, False],
)

strict_top200 = strict.head(200).copy()

strict.to_csv(OUTPUT_STRICT, index=False, encoding="utf-8-sig")
strict_top200.to_csv(OUTPUT_STRICT_TOP200, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_STRICT}")
print(f"Arquivo salvo em: {OUTPUT_STRICT_TOP200}")
print(f"Total entrada: {len(df)}")
print(f"Total strict: {len(strict)}")
print(f"Total top200 strict: {len(strict_top200)}")
