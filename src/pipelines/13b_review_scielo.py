"""
13b_review_scielo.py
====================
Revisão dos resultados coletados do SciELO.

Entrada : data/raw/scielo_results.csv
Saída   : Console (relatório)

Uso:
    python src/pipelines/13b_review_scielo.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FILE = BASE_DIR / "data" / "raw" / "scielo_results.csv"

if not RAW_FILE.exists():
    print(f"Arquivo não encontrado: {RAW_FILE}")
    print("Execute primeiro: python src/pipelines/13_collect_scielo.py")
    exit(1)

df = pd.read_csv(RAW_FILE)

print(f"\n{'='*60}")
print("REVISÃO — SCIELO")
print(f"{'='*60}")
print(f"Total de registros: {len(df)}")
print(f"Colunas: {df.columns.tolist()}")

print(f"\n=== POR QUERY ===")
print(df["query_term"].value_counts().to_string())

print(f"\n=== POR IDIOMA ===")
print(df["language"].fillna("N/D").value_counts().head(10).to_string())

print(f"\n=== TOP 15 PERIÓDICOS ===")
print(df["journal"].fillna("N/D").value_counts().head(15).to_string())

print(f"\n=== POR ANO ===")
year_counts = df["publication_year"].fillna("N/D").value_counts().sort_index()
print(year_counts.tail(15).to_string())

print(f"\n=== METADADOS ===")
has_doi = (df["doi"].fillna("").astype(str).str.strip() != "").sum()
has_abstract = (df["abstract"].fillna("").astype(str).str.strip() != "").sum()
has_authors = (df["authors"].fillna("").astype(str).str.strip() != "").sum()
has_journal = (df["journal"].fillna("").astype(str).str.strip() != "").sum()
print(f"Com DOI:      {has_doi}/{len(df)} ({has_doi/len(df)*100:.1f}%)")
print(f"Com abstract: {has_abstract}/{len(df)} ({has_abstract/len(df)*100:.1f}%)")
print(f"Com autores:  {has_authors}/{len(df)} ({has_authors/len(df)*100:.1f}%)")
print(f"Com periódico:{has_journal}/{len(df)} ({has_journal/len(df)*100:.1f}%)")

print(f"\n=== AMOSTRA (10 primeiros) ===")
sample_cols = ["title", "publication_year", "journal", "query_term"]
available = [c for c in sample_cols if c in df.columns]
print(df[available].head(10).to_string(index=False))
