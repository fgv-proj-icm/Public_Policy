from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
FINAL_DIR = BASE_DIR / "data" / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

files = [
    RAW_DIR / "openalex_results_refined.csv",
    RAW_DIR / "crossref_results_refined.csv",
    RAW_DIR / "scopus_results.csv",
]

dfs = []
for file in files:
    if file.exists():
        df = pd.read_csv(file)
        df["source_file"] = file.name
        dfs.append(df)

if not dfs:
    raise RuntimeError("Nenhuma base encontrada para unificação.")

df = pd.concat(dfs, ignore_index=True)

for col in ["doi", "title", "journal", "publication_year", "cited_by_count"]:
    if col not in df.columns:
        df[col] = ""

df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()
df["journal_norm"] = df["journal"].fillna("").astype(str).str.strip().str.lower()
df["year_norm"] = df["publication_year"].fillna("").astype(str).str.strip()

df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)

df = df.sort_values("cited_by_count", ascending=False)

df_with_doi = df[df["doi_norm"] != ""].copy()
df_without_doi = df[df["doi_norm"] == ""].copy()

df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
df_without_doi = df_without_doi.drop_duplicates(
    subset=["title_norm", "year_norm", "journal_norm"],
    keep="first",
)

df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)

output_csv = FINAL_DIR / "unified_base.csv"
df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {output_csv}")
print(f"Total bruto unificado: {len(df)}")
print(f"Total final deduplicado: {len(df_final)}")