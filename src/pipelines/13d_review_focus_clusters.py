from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

AGENDA_FILE = FINAL_DIR / "reading_agenda_rebalanced.csv"
TOP50_FILE = FINAL_DIR / "reading_agenda_rebalanced_top50.csv"

agenda = pd.read_csv(AGENDA_FILE, low_memory=False)
top50 = pd.read_csv(TOP50_FILE, low_memory=False)

print("\n=== READING AGENDA REBALANCED ===")
print(f"Linhas: {len(agenda)}")

print("\n=== TOP50 REBALANCED ===")
print(f"Linhas: {len(top50)}")

print("\n=== FONTES | TOP50 REBALANCED ===")
print(top50["source_file"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN | TOP50 REBALANCED ===")
if "query_term_clean" in top50.columns:
    print(top50["query_term_clean"].value_counts().head(20).to_string())

print("\n=== TOP 30 DA AGENDA REBALANCED ===")
cols = [
    "title",
    "publication_year",
    "journal",
    "citation_count_unified",
    "agenda_score",
    "agenda_score_rebalanced",
    "query_term_clean",
    "source_file",
]
cols = [c for c in cols if c in top50.columns]
print(top50[cols].head(30).to_string(index=False))
