from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

FOCUS_FILE = FINAL_DIR / "focus_corpus_policy_admin.csv"
JOURNAL_FILE = FINAL_DIR / "focus_corpus_policy_admin_journal.csv"

focus = pd.read_csv(FOCUS_FILE, low_memory=False)
journal = pd.read_csv(JOURNAL_FILE, low_memory=False)

print("\n=== FOCUS CORPUS ===")
print(f"Linhas: {len(focus)}")

print("\n=== FOCUS CORPUS JOURNAL ===")
print(f"Linhas: {len(journal)}")

print("\n=== PRIMARY TYPE | FOCUS ===")
if "primary_type" in focus.columns:
    print(focus["primary_type"].value_counts().to_string())

print("\n=== FONTES | FOCUS ===")
if "source_file" in focus.columns:
    print(focus["source_file"].value_counts().to_string())

print("\n=== FONTES | FOCUS JOURNAL ===")
if "source_file" in journal.columns:
    print(journal["source_file"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN | FOCUS ===")
if "query_term_clean" in focus.columns:
    print(focus["query_term_clean"].value_counts().head(20).to_string())

print("\n=== FOCUS REASON ===")
if "focus_reason" in focus.columns:
    print(focus["focus_reason"].value_counts().to_string())

print("\n=== TOP 20 PERIÓDICOS | FOCUS JOURNAL ===")
if "journal" in journal.columns:
    print(journal["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== TOP 20 ARTIGOS POR CITAÇÕES | FOCUS ===")
if "citation_count_unified" in focus.columns:
    top = focus.sort_values("citation_count_unified", ascending=False)[
        ["title", "publication_year", "journal", "citation_count_unified", "query_term_clean"]
    ].head(20)
    print(top.to_string(index=False))
