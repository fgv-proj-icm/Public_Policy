from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_FILE = BASE_DIR / "data" / "final" / "unified_base_analysis_ready.csv"

df = pd.read_csv(FINAL_FILE, low_memory=False)

print("\n=== VISÃO GERAL ===")
print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")

print("\n=== IDIOMA PADRONIZADO ===")
if "language_clean" in df.columns:
    print(df["language_clean"].value_counts().head(20).to_string())

print("\n=== TYPE CLEAN ===")
if "type_clean" in df.columns:
    print(df["type_clean"].value_counts().head(20).to_string())

print("\n=== FLAGS ===")
for col in ["has_doi", "has_abstract", "has_authors", "has_journal", "journal_missing_flag"]:
    if col in df.columns:
        print(f"\n{col}")
        print(df[col].value_counts().to_string())

print("\n=== TOP 20 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(20).to_string())
