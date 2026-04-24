from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "bibliometric_corpus_final.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

print("\n=== BIBLIOMETRIC CORPUS FINAL ===")
print(f"Linhas: {len(df)}")
print(f"Colunas: {len(df.columns)}")

print("\n=== PRIMARY TYPE ===")
if "primary_type" in df.columns:
    print(df["primary_type"].value_counts().to_string())

print("\n=== THEMATIC BUCKET ===")
if "thematic_bucket" in df.columns:
    print(df["thematic_bucket"].value_counts().to_string())

print("\n=== FONTES ===")
if "source_file" in df.columns:
    print(df["source_file"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN ===")
if "query_term_clean" in df.columns:
    print(df["query_term_clean"].value_counts().head(20).to_string())

print("\n=== TOP 20 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== CHECK DUPLICATAS ===")
if "doi_clean" in df.columns:
    with_doi = df[df["doi_clean"].fillna("").astype(str).str.strip() != ""].copy()
    print(f"Com DOI: {len(with_doi)}")
    print(f"DOIs únicos: {with_doi['doi_clean'].nunique()}")

no_doi = df[df["doi_clean"].fillna("").astype(str).str.strip() == ""].copy() if "doi_clean" in df.columns else pd.DataFrame()
if len(no_doi) > 0:
    dup_no_doi = no_doi.duplicated(subset=["title_clean", "publication_year", "journal_clean"], keep=False).sum()
    print(f"Registros em grupos duplicados sem DOI: {dup_no_doi}")
else:
    print("Registros sem DOI: 0")

print("\n=== TOP 30 ARTIGOS POR CITAÇÕES ===")
if "citation_count_unified" in df.columns:
    cols = ["title", "publication_year", "journal", "citation_count_unified", "thematic_bucket", "query_term_clean"]
    cols = [c for c in cols if c in df.columns]
    print(
        df.sort_values("citation_count_unified", ascending=False)[cols]
        .head(30)
        .to_string(index=False)
    )