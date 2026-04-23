from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "focus_corpus_policy_clustered.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

print("\n=== FOCUS CLUSTERS ===")
print(df["focus_cluster"].value_counts().to_string())

print("\n=== QUERY TERM CLEAN x CLUSTER ===")
tab = pd.crosstab(df["focus_cluster"], df["query_term_clean"])
print(tab.to_string())

print("\n=== TOP 20 PERIÓDICOS POR CLUSTER ===")
for cluster in df["focus_cluster"].dropna().unique():
    sub = df[df["focus_cluster"] == cluster]
    print(f"\n--- {cluster} ---")
    if "journal" in sub.columns:
        print(sub["journal"].fillna("N/D").value_counts().head(10).to_string())

print("\n=== TOP 10 ARTIGOS POR CITAÇÕES EM CADA CLUSTER ===")
for cluster in df["focus_cluster"].dropna().unique():
    sub = df[df["focus_cluster"] == cluster].copy()
    sub["citation_count_unified"] = pd.to_numeric(sub["citation_count_unified"], errors="coerce").fillna(0)
    print(f"\n--- {cluster} ---")
    cols = ["title", "publication_year", "journal", "citation_count_unified", "query_term_clean"]
    cols = [c for c in cols if c in sub.columns]
    print(sub.sort_values("citation_count_unified", ascending=False)[cols].head(10).to_string(index=False))
