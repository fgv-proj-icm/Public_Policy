from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

BIBLIO_FILE = FINAL_DIR / "bibliometric_corpus_final_v2.csv"
READING_FILE = FINAL_DIR / "reading_corpus_final_curated.csv"
TOP100_FILE = FINAL_DIR / "reading_corpus_final_curated_top100.csv"

biblio = pd.read_csv(BIBLIO_FILE, low_memory=False)
reading = pd.read_csv(READING_FILE, low_memory=False)
top100 = pd.read_csv(TOP100_FILE, low_memory=False)

print("\n=== BIBLIOMETRIC CORPUS FINAL V2 ===")
print(f"Linhas: {len(biblio)}")
print(f"Colunas: {len(biblio.columns)}")

print("\n=== THEMATIC BUCKET | BIBLIO V2 ===")
if "thematic_bucket" in biblio.columns:
    print(biblio["thematic_bucket"].value_counts().to_string())

print("\n=== FONTES | BIBLIO V2 ===")
if "source_file" in biblio.columns:
    print(biblio["source_file"].value_counts().to_string())

print("\n=== TOP 20 PERIÓDICOS | BIBLIO V2 ===")
if "journal" in biblio.columns:
    print(biblio["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== CHECK DUPLICATAS | BIBLIO V2 ===")
if "doi_clean" in biblio.columns:
    with_doi = biblio[biblio["doi_clean"].fillna("").astype(str).str.strip() != ""].copy()
    print(f"Com DOI: {len(with_doi)}")
    print(f"DOIs únicos: {with_doi['doi_clean'].nunique()}")

no_doi = biblio[biblio["doi_clean"].fillna("").astype(str).str.strip() == ""].copy() if "doi_clean" in biblio.columns else pd.DataFrame()
if len(no_doi) > 0:
    dup_no_doi = no_doi.duplicated(subset=["title_clean", "publication_year", "journal_clean"], keep=False).sum()
    print(f"Registros em grupos duplicados sem DOI: {dup_no_doi}")
else:
    print("Registros sem DOI: 0")

print("\n=== READING CURATED ===")
print(f"Linhas: {len(reading)}")

print("\n=== TOP100 CURATED ===")
print(f"Linhas: {len(top100)}")

print("\n=== FONTES | TOP100 CURATED ===")
if "source_file" in top100.columns:
    print(top100["source_file"].value_counts().to_string())

print("\n=== THEMATIC BUCKET | TOP100 CURATED ===")
if "thematic_bucket" in top100.columns:
    print(top100["thematic_bucket"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN | TOP100 CURATED ===")
if "query_term_clean" in top100.columns:
    print(top100["query_term_clean"].value_counts().head(20).to_string())

print("\n=== TOP 30 CURATED ===")
cols = [
    "title",
    "publication_year",
    "journal",
    "citation_count_unified",
    "reading_score_curated",
    "thematic_bucket",
    "query_term_clean",
    "source_file",
]
cols = [c for c in cols if c in top100.columns]
print(top100[cols].head(30).to_string(index=False))