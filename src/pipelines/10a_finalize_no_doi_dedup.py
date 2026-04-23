from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready.csv"
OUTPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_step10a.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

for col in ["title_clean", "year_clean", "journal_clean", "citation_count_unified", "completeness_score", "source_priority"]:
    if col not in df.columns:
        df[col] = ""

df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
df["completeness_score"] = pd.to_numeric(df["completeness_score"], errors="coerce").fillna(0)
df["source_priority"] = pd.to_numeric(df["source_priority"], errors="coerce").fillna(0)

df["has_doi"] = df["doi_clean"].fillna("").astype(str).str.strip() != ""
df["has_journal"] = df["journal_clean"].fillna("").astype(str).str.strip() != ""
df["has_url"] = df["url"].fillna("").astype(str).str.strip() != ""

with_doi = df[df["has_doi"]].copy()
without_doi = df[~df["has_doi"]].copy()

without_doi = without_doi.sort_values(
    by=["completeness_score", "has_journal", "has_url", "source_priority", "citation_count_unified"],
    ascending=[False, False, False, False, False],
)

without_doi_dedup = without_doi.drop_duplicates(
    subset=["title_clean", "year_clean"],
    keep="first",
)

df_final = pd.concat([with_doi, without_doi_dedup], ignore_index=True)

df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(f"Total entrada: {len(df)}")
print(f"Total sem DOI antes: {len(without_doi)}")
print(f"Total sem DOI depois: {len(without_doi_dedup)}")
print(f"Total final: {len(df_final)}")
