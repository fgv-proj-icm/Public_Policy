from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_v3.csv"
OUTPUT_STRICT = FINAL_DIR / "focus_corpus_strict.csv"
OUTPUT_STRICT_TOP = FINAL_DIR / "focus_corpus_strict_top200.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

def to_bool(series: pd.Series) -> pd.Series:
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

for col in [
    "focus_policy_admin_flag",
    "focus_title_flag",
    "focus_query_flag",
    "journal_suspect_flag",
    "has_journal",
    "has_authors",
    "has_abstract",
]:
    if col not in df.columns:
        df[col] = False

for col in ["primary_type", "title_clean", "journal_clean", "query_term_clean"]:
    if col not in df.columns:
        df[col] = ""

if "citation_count_unified" not in df.columns:
    df["citation_count_unified"] = 0

df["focus_policy_admin_flag"] = to_bool(df["focus_policy_admin_flag"])
df["focus_title_flag"] = to_bool(df["focus_title_flag"])
df["focus_query_flag"] = to_bool(df["focus_query_flag"])
df["journal_suspect_flag"] = to_bool(df["journal_suspect_flag"])
df["has_journal"] = to_bool(df["has_journal"])
df["has_authors"] = to_bool(df["has_authors"])
df["has_abstract"] = to_bool(df["has_abstract"])

df["primary_type"] = df["primary_type"].fillna("nd").astype(str).str.strip().str.lower()
df["title_clean"] = df["title_clean"].fillna("").astype(str).str.strip().str.lower()
df["journal_clean"] = df["journal_clean"].fillna("").astype(str).str.strip().str.lower()
df["query_term_clean"] = df["query_term_clean"].fillna("nd").astype(str).str.strip().str.lower()
df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)

STRICT_HINTS = [
    "judicial policy",
    "judicial policies",
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
    "judicial performance",
    "court performance",
    "judicial efficiency",
    "court efficiency",
    "case management",
    "e-justice",
    "digital justice",
]

def has_strict_hint(text: str) -> bool:
    return any(h in text for h in STRICT_HINTS)

df["strict_title_flag"] = (
    df["title_clean"].apply(has_strict_hint)
    | df["journal_clean"].apply(has_strict_hint)
)

# score simples de qualidade
df["strict_metadata_score"] = (
    df["has_journal"].astype(int)
    + df["has_authors"].astype(int)
    + df["has_abstract"].astype(int)
)

strict = df[
    (df["focus_policy_admin_flag"])
    & (df["primary_type"].isin(["article", "review"]))
    & (~df["journal_suspect_flag"])
    & (df["has_journal"])
    & (df["strict_title_flag"])
].copy()

strict["strict_reason"] = "title_and_journal_focus"

strict = strict.sort_values(
    by=["strict_metadata_score", "citation_count_unified", "publication_year"],
    ascending=[False, False, False],
)

strict_top = strict.head(200).copy()

strict.to_csv(OUTPUT_STRICT, index=False, encoding="utf-8-sig")
strict_top.to_csv(OUTPUT_STRICT_TOP, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_STRICT}")
print(f"Arquivo salvo em: {OUTPUT_STRICT_TOP}")
print(f"Total entrada: {len(df)}")
print(f"Total focus corpus strict: {len(strict)}")
print(f"Total top200 strict: {len(strict_top)}")
