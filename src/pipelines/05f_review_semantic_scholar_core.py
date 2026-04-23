from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_FILE = BASE_DIR / "data" / "raw" / "semantic_scholar_results_core.csv"

df = pd.read_csv(RAW_FILE)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")

print("\n=== TOP 15 QUERIES ===")
print(df["query_term"].value_counts().head(15).to_string())

print("\n=== TOP 15 PERIÓDICOS ===")
print(df["journal"].fillna("N/D").value_counts().head(15).to_string())

print("\n=== TOP 20 ARTIGOS POR CITAÇÕES ===")
top = df.sort_values("citation_count", ascending=False)[
    ["title", "publication_year", "journal", "citation_count", "query_term"]
].head(20)
print(top.to_string(index=False))