from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"

INPUT_FILE = RAW_DIR / "semantic_scholar_results.csv"
OUTPUT_FILE = RAW_DIR / "semantic_scholar_results_refined.csv"

ANCHORS = [
    "judicial",
    "judiciary",
    "court",
    "courts",
    "tribunal",
    "tribunals",
    "justice",
    "access to justice",
    "judicial review",
    "judicial reform",
    "judicial administration",
    "court administration",
    "constitutional court",
    "supreme court",
    "legal system",
]

BAD_JOURNAL_HINTS = [
    "plos medicine",
    "british medical journal",
    "social science research network",
    "emerald expert briefings",
]

BAD_TITLE_HINTS = [
    "world development report",
    "poverty reduction",
    "natural resources",
    "sex workers",
    "stakeholder and citizen participation",
    "history of british india",
]

BAD_QUERY_HINTS = [
    '"access to justice"',
]

def norm(text) -> str:
    if pd.isna(text):
        return ""
    return str(text).strip().lower()

df = pd.read_csv(INPUT_FILE)

df["title_norm"] = df["title"].apply(norm)
df["journal_norm"] = df["journal"].apply(norm)
df["query_norm"] = df["query_term"].apply(norm)

def is_relevant(row) -> bool:
    text = " ".join([row["title_norm"], row["journal_norm"], row["query_norm"]])

    has_anchor = any(anchor in text for anchor in ANCHORS)
    bad_journal = any(bad in row["journal_norm"] for bad in BAD_JOURNAL_HINTS)
    bad_title = any(bad in row["title_norm"] for bad in BAD_TITLE_HINTS)
    bad_query = any(bad.lower() in row["query_norm"] for bad in BAD_QUERY_HINTS)

    return has_anchor and not bad_journal and not bad_title and not bad_query

df_refined = df[df.apply(is_relevant, axis=1)].copy()

df_refined["doi_norm"] = df_refined["doi"].fillna("").astype(str).str.strip().str.lower()
df_refined["title_norm"] = df_refined["title"].fillna("").astype(str).str.strip().str.lower()
df_refined["journal_norm"] = df_refined["journal"].fillna("").astype(str).str.strip().str.lower()
df_refined["publication_year"] = df_refined["publication_year"].fillna("").astype(str).str.strip()
df_refined["citation_count"] = pd.to_numeric(df_refined["citation_count"], errors="coerce").fillna(0)

df_refined = df_refined.sort_values("citation_count", ascending=False)

if "paper_id" in df_refined.columns:
    df_refined = df_refined.drop_duplicates(subset=["paper_id"], keep="first")

df_with_doi = df_refined[df_refined["doi_norm"] != ""].copy()
df_without_doi = df_refined[df_refined["doi_norm"] == ""].copy()

df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
df_without_doi = df_without_doi.drop_duplicates(
    subset=["title_norm", "publication_year", "journal_norm"],
    keep="first",
)

df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)
df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(f"Total antes do refino: {len(df)}")
print(f"Total após o refino: {len(df_final)}")