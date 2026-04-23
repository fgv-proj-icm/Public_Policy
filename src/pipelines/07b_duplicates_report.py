from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
AUDIT_DIR = FINAL_DIR / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = FINAL_DIR / "unified_base.csv"


def clean_doi(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.strip()


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


df = pd.read_csv(INPUT_FILE, low_memory=False)

df["doi_clean"] = df["doi"].apply(clean_doi) if "doi" in df.columns else ""
df["title_clean"] = df["title"].apply(norm_text) if "title" in df.columns else ""
df["journal_clean"] = df["journal"].apply(norm_text) if "journal" in df.columns else ""
df["year_clean"] = df["publication_year"].fillna("").astype(str).str.strip()

with_doi = df[df["doi_clean"] != ""].copy()
dup_doi = with_doi[with_doi.duplicated(subset=["doi_clean"], keep=False)].copy()
dup_doi = dup_doi.sort_values(["doi_clean", "publication_year", "title_clean"])

dup_doi.to_csv(AUDIT_DIR / "duplicate_doi_candidates.csv", index=False, encoding="utf-8-sig")

without_doi = df[df["doi_clean"] == ""].copy()
dup_no_doi = without_doi[
    without_doi.duplicated(subset=["title_clean", "year_clean", "journal_clean"], keep=False)
].copy()
dup_no_doi = dup_no_doi.sort_values(["title_clean", "year_clean", "journal_clean"])

dup_no_doi.to_csv(AUDIT_DIR / "duplicate_no_doi_candidates.csv", index=False, encoding="utf-8-sig")

summary = pd.DataFrame(
    {
        "metric": [
            "n_total",
            "n_with_doi",
            "n_unique_doi_clean",
            "n_records_in_duplicate_doi_groups",
            "n_without_doi",
            "n_records_in_duplicate_no_doi_groups",
        ],
        "value": [
            len(df),
            len(with_doi),
            with_doi["doi_clean"].nunique(),
            len(dup_doi),
            len(without_doi),
            len(dup_no_doi),
        ],
    }
)
summary.to_csv(AUDIT_DIR / "duplicates_summary.csv", index=False, encoding="utf-8-sig")

print("Total com DOI:", len(with_doi))
print("DOIs limpos únicos:", with_doi["doi_clean"].nunique())
print("Registros em grupos duplicados por DOI:", len(dup_doi))
print("Registros em grupos duplicados sem DOI:", len(dup_no_doi))
print("Arquivos salvos em:", AUDIT_DIR)
