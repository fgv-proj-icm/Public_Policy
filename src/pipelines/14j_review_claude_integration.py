from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

KEEP_FILE = FINAL_DIR / "bibliometric_corpus_final_v3.csv"
REVIEW_FILE = FINAL_DIR / "bibliometric_corpus_review_queue.csv"
EXCLUDED_FILE = FINAL_DIR / "bibliometric_corpus_excluded.csv"
READING_FILE = FINAL_DIR / "reading_corpus_final_v3.csv"
TOP80_FILE = FINAL_DIR / "reading_corpus_final_v3_top80.csv"

keep_df = pd.read_csv(KEEP_FILE, low_memory=False)
review_df = pd.read_csv(REVIEW_FILE, low_memory=False)
excluded_df = pd.read_csv(EXCLUDED_FILE, low_memory=False)
reading_df = pd.read_csv(READING_FILE, low_memory=False)
top80_df = pd.read_csv(TOP80_FILE, low_memory=False)

print("\n=== CORPUS FINAL V3 (CLAUDE INTEGRADO) ===")
print(f"Linhas: {len(keep_df)}")
print(f"Colunas: {len(keep_df.columns)}")

print("\n=== REVIEW QUEUE ===")
print(f"Linhas: {len(review_df)}")

print("\n=== EXCLUÍDOS ===")
print(f"Linhas: {len(excluded_df)}")

print("\n=== THEMATIC BUCKET | FINAL V3 ===")
if "thematic_bucket" in keep_df.columns:
    print(keep_df["thematic_bucket"].value_counts().to_string())

print("\n=== FONTES | FINAL V3 ===")
if "source_file" in keep_df.columns:
    print(keep_df["source_file"].value_counts().to_string())

print("\n=== DECISÃO CLAUDE | REVIEW QUEUE ===")
if "claude_curated_decision" in review_df.columns:
    print(review_df["claude_curated_decision"].value_counts().to_string())

print("\n=== RAZÕES DE EXCLUSÃO MAIS FREQUENTES ===")
if "claude_curated_reason" in excluded_df.columns:
    print(excluded_df["claude_curated_reason"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== LEITURA FINAL V3 ===")
print(f"Linhas: {len(reading_df)}")

print("\n=== LEITURA TOP80 ===")
print(f"Linhas: {len(top80_df)}")

print("\n=== FONTES | TOP80 ===")
if "source_file" in top80_df.columns:
    print(top80_df["source_file"].value_counts().to_string())

print("\n=== THEMATIC BUCKET | TOP80 ===")
if "thematic_bucket" in top80_df.columns:
    print(top80_df["thematic_bucket"].value_counts().to_string())

print("\n=== TOP 30 DO TOP80 ===")
cols = [
    "title",
    "publication_year",
    "journal",
    "citation_count_unified",
    "claude_curated_relevance_level",
    "claude_curated_reason",
    "thematic_bucket",
    "source_file",
]
cols = [c for c in cols if c in top80_df.columns]
print(top80_df[cols].head(30).to_string(index=False))