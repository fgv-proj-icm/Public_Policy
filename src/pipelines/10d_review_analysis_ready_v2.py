from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_v2.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")

print("\n=== QUERY TERM CLEAN ===")
if "query_term_clean" in df.columns:
    print(df["query_term_clean"].value_counts().head(20).to_string())

print("\n=== PRIMARY TYPE ===")
if "primary_type" in df.columns:
    print(df["primary_type"].value_counts().head(20).to_string())

print("\n=== RELEVÂNCIA ===")
if "relevance_flag" in df.columns:
    print(df["relevance_flag"].value_counts().to_string())
if "relevance_reason" in df.columns:
    print(df["relevance_reason"].value_counts().to_string())

print("\n=== DUPLICATAS SEM DOI POR title_clean + year_clean ===")
if {"doi_clean", "title_clean", "year_clean"}.issubset(df.columns):
    sub = df[df["doi_clean"].fillna("").astype(str).str.strip() == ""].copy()
    n_dup = sub.duplicated(subset=["title_clean", "year_clean"], keep=False).sum()
    print(f"Registros em grupos duplicados sem DOI: {n_dup}")

print("\n=== TOP 20 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(20).to_string())
