from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_v3.csv"
OUTPUT_MASTER = FINAL_DIR / "focus_corpus_policy_admin.csv"
OUTPUT_JOURNAL = FINAL_DIR / "focus_corpus_policy_admin_journal.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

for col in [
    "query_term_clean",
    "title_clean",
    "journal_clean",
    "primary_type",
    "relevance_flag",
    "journal_suspect_flag",
    "has_journal",
    "citation_count_unified",
]:
    if col not in df.columns:
        df[col] = ""

def norm(v) -> str:
    if pd.isna(v):
        return ""
    return str(v).strip().lower()

df["query_term_clean"] = df["query_term_clean"].apply(norm)
df["title_clean"] = df["title_clean"].apply(norm)
df["journal_clean"] = df["journal_clean"].apply(norm)
df["primary_type"] = df["primary_type"].fillna("nd").astype(str).str.strip().str.lower()
df["relevance_flag"] = pd.to_numeric(df["relevance_flag"], errors="coerce").fillna(0).astype(int)
df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)

# normalizar bools
df["journal_suspect_flag"] = (
    df["journal_suspect_flag"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["true", "1", "yes"])
)

df["has_journal"] = (
    df["has_journal"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["true", "1", "yes"])
)

CORE_QUERY_TERMS = {
    "judicial policy",
    "judicial policies",
    "judicial governance",
    "judicial administration",
    "court administration",
    "court governance",
    "judicial reform",
    "política judiciária",
    "políticas judiciárias",
    "governança judicial",
    "administração judiciária",
    "reforma do judiciário",
    "reforma judicial",
    "conselho nacional de justiça",
}

FOCUS_TITLE_HINTS = [
    "judicial policy",
    "judicial policies",
    "judicial governance",
    "judicial administration",
    "court administration",
    "court governance",
    "judicial reform",
    "política judiciária",
    "políticas judiciárias",
    "governança judicial",
    "administração judiciária",
    "reforma judicial",
    "reforma do judiciário",
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
]

def has_any_hint(text: str, hints: list[str]) -> bool:
    return any(h in text for h in hints)

df["focus_query_flag"] = df["query_term_clean"].isin(CORE_QUERY_TERMS)
df["focus_title_flag"] = (
    df["title_clean"].apply(lambda x: has_any_hint(x, FOCUS_TITLE_HINTS))
    | df["journal_clean"].apply(lambda x: has_any_hint(x, FOCUS_TITLE_HINTS))
)

df["focus_policy_admin_flag"] = (
    (df["relevance_flag"] == 1)
    & (df["primary_type"].isin(["article", "review"]))
    & (~df["journal_suspect_flag"])
    & (df["focus_query_flag"] | df["focus_title_flag"])
)

def focus_reason(row) -> str:
    if row["focus_query_flag"] and row["focus_title_flag"]:
        return "query_and_title"
    if row["focus_query_flag"]:
        return "query_only"
    if row["focus_title_flag"]:
        return "title_only"
    return "no_focus_signal"

df["focus_reason"] = df.apply(focus_reason, axis=1)

focus = df[df["focus_policy_admin_flag"]].copy()
focus_journal = focus[focus["has_journal"]].copy()

focus = focus.sort_values(
    by=["citation_count_unified", "publication_year"],
    ascending=[False, False],
)
focus_journal = focus_journal.sort_values(
    by=["citation_count_unified", "publication_year"],
    ascending=[False, False],
)

focus.to_csv(OUTPUT_MASTER, index=False, encoding="utf-8-sig")
focus_journal.to_csv(OUTPUT_JOURNAL, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_MASTER}")
print(f"Arquivo salvo em: {OUTPUT_JOURNAL}")
print(f"Total base entrada: {len(df)}")
print(f"Total focus corpus: {len(focus)}")
print(f"Total focus corpus com journal: {len(focus_journal)}")
