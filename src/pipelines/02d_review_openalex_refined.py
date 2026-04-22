from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FILE = BASE_DIR / "data" / "raw" / "openalex_results_refined.csv"

df = pd.read_csv(RAW_FILE)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")

print("\n=== POR IDIOMA ===")
print(df["language"].fillna("N/D").value_counts().to_string())

print("\n=== TOP 15 PERIÓDICOS ===")
print(df["journal"].fillna("N/D").value_counts().head(15).to_string())

print("\n=== TOP 20 ARTIGOS POR CITAÇÕES ===")
top = df.sort_values("cited_by_count", ascending=False)[
    ["title", "publication_year", "journal", "cited_by_count", "query_term"]
].head(20)
print(top.to_string(index=False))