from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FILE = BASE_DIR / "data" / "raw" / "openalex_results.csv"

df = pd.read_csv(RAW_FILE)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")
print("\nColunas:")
print(df.columns.tolist())

print("\n=== AMOSTRA ===")
print(df.head(10).to_string(index=False))

# Padronizações leves
if "doi" in df.columns:
    df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
else:
    df["doi_norm"] = ""

if "title" in df.columns:
    df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()
else:
    df["title_norm"] = ""

if "openalex_id" not in df.columns:
    df["openalex_id"] = ""

print("\n=== DUPLICATAS ===")
print(f"IDs OpenAlex únicos: {df['openalex_id'].nunique(dropna=True)}")
print(f"DOIs únicos (não vazios): {(df['doi_norm'] != '').sum()} linhas com DOI")
print(f"DOIs distintos (não vazios): {df.loc[df['doi_norm'] != '', 'doi_norm'].nunique()}")

dup_id = df.duplicated(subset=["openalex_id"]).sum()
print(f"Duplicatas por openalex_id: {dup_id}")

doi_nonempty = df[df["doi_norm"] != ""].copy()
dup_doi = doi_nonempty.duplicated(subset=["doi_norm"]).sum()
print(f"Duplicatas por DOI: {dup_doi}")

print("\n=== POR IDIOMA ===")
if "language" in df.columns:
    print(df["language"].fillna("N/D").value_counts(dropna=False).head(10).to_string())
else:
    print("Coluna language não encontrada.")

print("\n=== POR ANO ===")
year_col = "publication_year" if "publication_year" in df.columns else "year"
if year_col in df.columns:
    year_counts = (
        df[year_col]
        .value_counts(dropna=False)
        .sort_index()
    )
    print(year_counts.tail(20).to_string())
else:
    print("Nenhuma coluna de ano encontrada.")

print("\n=== TOP 15 QUERIES ===")
if "query_term" in df.columns:
    print(df["query_term"].value_counts().head(15).to_string())
else:
    print("Coluna query_term não encontrada.")

print("\n=== TOP 15 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(15).to_string())
else:
    print("Coluna journal não encontrada.")

print("\n=== TOP 20 ARTIGOS POR CITAÇÕES ===")
if "cited_by_count" in df.columns:
    top = (
        df.sort_values("cited_by_count", ascending=False)
          [["title", year_col, "journal", "cited_by_count", "query_term"]]
          .head(20)
    )
    print(top.to_string(index=False))
else:
    print("Coluna cited_by_count não encontrada.")