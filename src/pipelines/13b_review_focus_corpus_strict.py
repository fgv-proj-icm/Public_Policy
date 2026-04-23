from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

STRICT_FILE = FINAL_DIR / "focus_corpus_strict.csv"
TOP200_FILE = FINAL_DIR / "focus_corpus_strict_top200.csv"

strict = pd.read_csv(STRICT_FILE, low_memory=False)
top200 = pd.read_csv(TOP200_FILE, low_memory=False)

print("\n=== FOCUS CORPUS STRICT ===")
print(f"Linhas: {len(strict)}")

print("\n=== TOP200 STRICT ===")
print(f"Linhas: {len(top200)}")

print("\n=== PRIMARY TYPE | STRICT ===")
print(strict["primary_type"].value_counts().to_string())

print("\n=== FONTES | STRICT ===")
if "source_file" in strict.columns:
    print(strict["source_file"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN | STRICT ===")
if "query_term_clean" in strict.columns:
    print(strict["query_term_clean"].value_counts().head(20).to_string())

print("\n=== TOP 20 PERIÓDICOS | STRICT ===")
print(strict["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== TOP 20 ARTIGOS POR CITAÇÕES | STRICT ===")
cols = ["title", "publication_year", "journal", "citation_count_unified", "query_term_clean"]
print(
    strict.sort_values("citation_count_unified", ascending=False)[cols]
    .head(20)
    .to_string(index=False)
)
