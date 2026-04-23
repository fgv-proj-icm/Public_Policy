from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_FILE = BASE_DIR / "data" / "final" / "unified_base.csv"

df = pd.read_csv(FINAL_FILE)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")
print(df.columns.tolist())

print("\n=== FONTES DE ORIGEM ===")
if "source_file" in df.columns:
    print(df["source_file"].fillna("N/D").value_counts().to_string())

print("\n=== TOP 20 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== TOP 20 ANOS ===")
if "publication_year" in df.columns:
    print(df["publication_year"].fillna("N/D").astype(str).value_counts().head(20).to_string())

print("\n=== TOP 30 ARTIGOS POR CITAÇÕES ===")
citation_col = "citation_count_unified" if "citation_count_unified" in df.columns else "cited_by_count"
top = df.sort_values(citation_col, ascending=False)[
    ["title", "publication_year", "journal", citation_col, "source_file"]
].head(30)
print(top.to_string(index=False))