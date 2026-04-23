from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"

INPUT_FILE = RAW_DIR / "semantic_scholar_results_refined.csv"
OUTPUT_FILE = RAW_DIR / "semantic_scholar_results_core.csv"

TITLE_ANCHORS = [
    "judicial",
    "judiciary",
    "court",
    "courts",
    "tribunal",
    "tribunals",
    "constitutional court",
    "supreme court",
    "judicial review",
    "judicial reform",
    "judicial administration",
    "court administration",
    "judicial governance",
    "court governance",
    "access to justice",
]

BAD_TITLE_HINTS = [
    "poverty",
    "development",
    "natural resources",
    "capabilities approach",
    "history of british india",
    "optimal deterrence",
]

BAD_JOURNAL_HINTS = [
    "plato",
    "british medical journal",
]

def norm(text) -> str:
    if pd.isna(text):
        return ""
    return str(text).strip().lower()

df = pd.read_csv(INPUT_FILE)

df["title_norm"] = df["title"].apply(norm)
df["journal_norm"] = df["journal"].apply(norm)
df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
df["publication_year"] = df["publication_year"].fillna("").astype(str).str.strip()
df["citation_count"] = pd.to_numeric(df["citation_count"], errors="coerce").fillna(0)

def is_core(row) -> bool:
    title = row["title_norm"]
    journal = row["journal_norm"]
    doi = row["doi_norm"]

    has_title_anchor = any(anchor in title for anchor in TITLE_ANCHORS)
    bad_title = any(bad in title for bad in BAD_TITLE_HINTS)
    bad_journal = any(bad in journal for bad in BAD_JOURNAL_HINTS)

    # regra mais conservadora:
    # 1) precisa ter âncora no título
    # 2) e precisa ter periódico OU DOI
    has_min_metadata = (journal not in ("", "n/d", "nan")) or (doi != "")

    return has_title_anchor and has_min_metadata and not bad_title and not bad_journal

df_core = df[df.apply(is_core, axis=1)].copy()
df_core = df_core.sort_values("citation_count", ascending=False)

if "paper_id" in df_core.columns:
    df_core = df_core.drop_duplicates(subset=["paper_id"], keep="first")

df_with_doi = df_core[df_core["doi_norm"] != ""].copy()
df_without_doi = df_core[df_core["doi_norm"] == ""].copy()

df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
df_without_doi = df_without_doi.drop_duplicates(
    subset=["title_norm", "publication_year", "journal_norm"],
    keep="first",
)

df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)
df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(f"Total antes do refino core: {len(df)}")
print(f"Total após o refino core: {len(df_final)}")