from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

READING_FILE = FINAL_DIR / "reading_corpus_final.csv"
TOP100_FILE = FINAL_DIR / "reading_corpus_final_top100.csv"

reading = pd.read_csv(READING_FILE, low_memory=False)
top100 = pd.read_csv(TOP100_FILE, low_memory=False)

print("\n=== READING CORPUS FINAL ===")
print(f"Linhas: {len(reading)}")

print("\n=== READING CORPUS FINAL TOP100 ===")
print(f"Linhas: {len(top100)}")

print("\n=== FONTES | TOP100 ===")
if "source_file" in top100.columns:
    print(top100["source_file"].value_counts().to_string())

print("\n=== THEMATIC BUCKET | TOP100 ===")
if "thematic_bucket" in top100.columns:
    print(top100["thematic_bucket"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN | TOP100 ===")
if "query_term_clean" in top100.columns:
    print(top100["query_term_clean"].value_counts().head(20).to_string())

print("\n=== TOP 30 DO READING CORPUS FINAL ===")
cols = [
    "title",
    "publication_year",
    "journal",
    "citation_count_unified",
    "reading_score",
    "thematic_bucket",
    "query_term_clean",
    "source_file",
]
cols = [c for c in cols if c in top100.columns]
print(top100[cols].head(30).to_string(index=False))