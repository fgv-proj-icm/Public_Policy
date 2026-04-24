from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "reading_sheet_top60.csv"
TOP20_FILE = FINAL_DIR / "reading_sheet_top20_priority.csv"

sheet = pd.read_csv(INPUT_FILE, low_memory=False)
top20 = pd.read_csv(TOP20_FILE, low_memory=False)

print("\n=== READING SHEET TOP60 ===")
print(f"Linhas: {len(sheet)}")
print(f"Colunas: {len(sheet.columns)}")

print("\n=== PRIORIDADE DE LEITURA ===")
if "reading_priority_tier" in sheet.columns:
    print(sheet["reading_priority_tier"].value_counts().to_string())

print("\n=== DISTRIBUIÇÃO POR BUCKET ===")
if "thematic_bucket" in sheet.columns:
    print(sheet["thematic_bucket"].value_counts().to_string())

print("\n=== DISTRIBUIÇÃO POR FONTE ===")
if "source_file" in sheet.columns:
    print(sheet["source_file"].value_counts().to_string())

print("\n=== TOP20 PRIORITÁRIO ===")
print(f"Linhas: {len(top20)}")

print("\n=== TOP20 POR BUCKET ===")
if "thematic_bucket" in top20.columns:
    print(top20["thematic_bucket"].value_counts().to_string())

print("\n=== TOP20 PARA COMEÇAR A LEITURA ===")
cols = [
    "reading_order",
    "reading_priority_tier",
    "title",
    "publication_year",
    "journal",
    "citation_count_unified",
    "thematic_bucket",
    "source_file",
]
cols = [c for c in cols if c in top20.columns]
print(top20[cols].to_string(index=False))