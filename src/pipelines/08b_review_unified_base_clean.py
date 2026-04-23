from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_FILE = BASE_DIR / "data" / "final" / "unified_base_clean.csv"

df = pd.read_csv(FINAL_FILE, low_memory=False)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")

print("\n=== FONTES ===")
if "source_file" in df.columns:
    print(df["source_file"].fillna("N/D").value_counts().to_string())

print("\n=== TYPE CLEAN ===")
if "type_clean" in df.columns:
    print(df["type_clean"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== DOI CLEAN ===")
if "doi_clean" in df.columns:
    nonempty = (df["doi_clean"].fillna("") != "").sum()
    unique_nonempty = df.loc[df["doi_clean"].fillna("") != "", "doi_clean"].nunique()
    print(f"Com DOI limpo: {nonempty}")
    print(f"DOIs limpos únicos: {unique_nonempty}")

print("\n=== TOP 20 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(20).to_string())
