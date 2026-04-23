from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "reading_agenda_top.csv"
OUTPUT_FILE = FINAL_DIR / "reading_agenda_rebalanced.csv"
OUTPUT_TOP50 = FINAL_DIR / "reading_agenda_rebalanced_top50.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

for col in ["agenda_score", "citation_count_unified", "publication_year"]:
    if col not in df.columns:
        df[col] = 0

df["agenda_score"] = pd.to_numeric(df["agenda_score"], errors="coerce").fillna(0)
df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")

# ranking interno por fonte
df = df.sort_values(
    by=["agenda_score", "citation_count_unified", "publication_year"],
    ascending=[False, False, False],
).copy()

df["rank_within_source"] = (
    df.groupby("source_file")
      .cumcount()
      .add(1)
)

# penalização suave para domínio excessivo da fonte
def source_penalty(rank: int) -> int:
    if rank <= 10:
        return 0
    if rank <= 25:
        return 1
    return 2

df["source_penalty"] = df["rank_within_source"].apply(source_penalty)
df["agenda_score_rebalanced"] = df["agenda_score"] - df["source_penalty"]

df = df.sort_values(
    by=["agenda_score_rebalanced", "agenda_score", "citation_count_unified", "publication_year"],
    ascending=[False, False, False, False],
)

top50 = []
source_limits = {
    "semantic_scholar_results_core.csv": 15,
    "openalex_results_refined.csv": 15,
    "crossref_results_refined.csv": 10,
    "scopus_results_refined.csv": 10,
}
counts = {k: 0 for k in source_limits}

for _, row in df.iterrows():
    source = row.get("source_file", "")
    limit = source_limits.get(source, 5)
    if counts.get(source, 0) < limit:
        top50.append(row)
        counts[source] = counts.get(source, 0) + 1
    if len(top50) >= 50:
        break

top50_df = pd.DataFrame(top50)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
top50_df.to_csv(OUTPUT_TOP50, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(f"Arquivo salvo em: {OUTPUT_TOP50}")
print("Distribuição no top50:")
print(top50_df["source_file"].value_counts().to_string())
