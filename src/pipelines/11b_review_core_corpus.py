from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

MASTER_FILE = FINAL_DIR / "unified_base_analysis_ready_v3.csv"
BROAD_FILE = FINAL_DIR / "core_corpus_broad.csv"
JOURNAL_FILE = FINAL_DIR / "core_corpus_journal.csv"

master = pd.read_csv(MASTER_FILE, low_memory=False)
broad = pd.read_csv(BROAD_FILE, low_memory=False)
journal = pd.read_csv(JOURNAL_FILE, low_memory=False)

print("\n=== BASE MESTRE V3 ===")
print(f"Linhas: {len(master)}")

print("\n=== CORE BROAD ===")
print(f"Linhas: {len(broad)}")

print("\n=== CORE JOURNAL ===")
print(f"Linhas: {len(journal)}")

print("\n=== PRIMARY TYPE | CORE BROAD ===")
if "primary_type" in broad.columns:
    print(broad["primary_type"].value_counts().to_string())

print("\n=== FONTES | CORE BROAD ===")
if "source_file" in broad.columns:
    print(broad["source_file"].value_counts().to_string())

print("\n=== FONTES | CORE JOURNAL ===")
if "source_file" in journal.columns:
    print(journal["source_file"].value_counts().to_string())

print("\n=== TOP 20 PERIÓDICOS | CORE JOURNAL ===")
if "journal" in journal.columns:
    print(journal["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== QUERY TERM CLEAN | CORE BROAD ===")
if "query_term_clean" in broad.columns:
    print(broad["query_term_clean"].value_counts().head(20).to_string())

print("\n=== FLAGS SUSPEITAS | BASE MESTRE V3 ===")
if "journal_suspect_flag" in master.columns:
    print(master["journal_suspect_flag"].value_counts().to_string())

print("\n=== TOP 20 ARTIGOS POR CITAÇÕES | CORE BROAD ===")
if "citation_count_unified" in broad.columns:
    top = broad.sort_values("citation_count_unified", ascending=False)[
        ["title", "publication_year", "journal", "citation_count_unified", "query_term_clean"]
    ].head(20)
    print(top.to_string(index=False))
