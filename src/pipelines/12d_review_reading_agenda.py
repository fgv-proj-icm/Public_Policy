from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

AGENDA_FILE = FINAL_DIR / "reading_agenda_top.csv"
TOP50_FILE = FINAL_DIR / "reading_agenda_top50.csv"

agenda = pd.read_csv(AGENDA_FILE, low_memory=False)
top50 = pd.read_csv(TOP50_FILE, low_memory=False)

print("\n=== READING AGENDA ===")
print(f"Linhas: {len(agenda)}")

print("\n=== READING AGENDA TOP50 ===")
print(f"Linhas: {len(top50)}")

print("\n=== AGENDA SCORE ===")
if "agenda_score" in agenda.columns:
    print(agenda["agenda_score"].value_counts().sort_index(ascending=False).to_string())

print("\n=== AGENDA BUCKET ===")
if "agenda_bucket" in agenda.columns:
    print(agenda["agenda_bucket"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN | AGENDA ===")
if "query_term_clean" in agenda.columns:
    print(agenda["query_term_clean"].value_counts().head(20).to_string())

print("\n=== FONTES | TOP50 ===")
if "source_file" in top50.columns:
    print(top50["source_file"].value_counts().to_string())

print("\n=== TOP 30 DA AGENDA ===")
cols = [
    "title",
    "publication_year",
    "journal",
    "citation_count_unified",
    "agenda_score",
    "agenda_bucket",
    "query_term_clean",
]
cols = [c for c in cols if c in top50.columns]
print(top50[cols].head(30).to_string(index=False))
