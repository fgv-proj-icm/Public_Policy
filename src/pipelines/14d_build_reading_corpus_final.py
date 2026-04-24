from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

BIBLIO_FILE = FINAL_DIR / "bibliometric_corpus_final.csv"
AGENDA_FILE = FINAL_DIR / "reading_agenda_rebalanced.csv"

OUTPUT_ALL = FINAL_DIR / "reading_corpus_final.csv"
OUTPUT_TOP100 = FINAL_DIR / "reading_corpus_final_top100.csv"


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def build_key(row: pd.Series) -> str:
    doi = norm_text(row.get("doi_clean", ""))
    title = norm_text(row.get("title_clean", ""))
    year = str(row.get("publication_year", "")).strip()
    journal = norm_text(row.get("journal_clean", ""))

    if doi:
        return f"doi::{doi}"
    return f"txt::{title}::{year}::{journal}"


biblio = pd.read_csv(BIBLIO_FILE, low_memory=False)
agenda = pd.read_csv(AGENDA_FILE, low_memory=False)

for df in [biblio, agenda]:
    for col in [
        "doi_clean",
        "title_clean",
        "journal_clean",
        "publication_year",
        "citation_count_unified",
        "has_abstract",
        "has_authors",
        "source_file",
        "thematic_bucket",
    ]:
        if col not in df.columns:
            df[col] = ""

biblio["record_key"] = biblio.apply(build_key, axis=1)
agenda["record_key"] = agenda.apply(build_key, axis=1)

merged = agenda.merge(
    biblio.drop_duplicates(subset=["record_key"]),
    on="record_key",
    how="inner",
    suffixes=("_agenda", ""),
)

# normalizações
for col in ["citation_count_unified", "agenda_score", "agenda_score_rebalanced"]:
    if col not in merged.columns:
        merged[col] = 0
    merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0)

for col in ["has_abstract", "has_authors"]:
    if col not in merged.columns:
        merged[col] = False
    merged[col] = (
        merged[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

if "publication_year" in merged.columns:
    merged["publication_year"] = pd.to_numeric(merged["publication_year"], errors="coerce")

citation_q3 = float(merged["citation_count_unified"].quantile(0.75)) if len(merged) > 0 else 0

merged["reading_score"] = (
    merged["agenda_score_rebalanced"]
    + merged["has_abstract"].astype(int)
    + merged["has_authors"].astype(int)
    + (merged["citation_count_unified"] >= citation_q3).astype(int)
    + (merged["publication_year"] >= 2018).fillna(False).astype(int)
)

merged = merged.sort_values(
    by=["reading_score", "agenda_score_rebalanced", "citation_count_unified", "publication_year"],
    ascending=[False, False, False, False],
)

reading_all = merged.copy()

# top100 balanceado por fonte e bucket
source_cap = 35
bucket_cap = 45
target_n = 100

source_counts = {}
bucket_counts = {}
selected_rows = []

for _, row in reading_all.iterrows():
    source = row.get("source_file", "unknown")
    bucket = row.get("thematic_bucket", "unknown")

    if source_counts.get(source, 0) >= source_cap:
        continue
    if bucket_counts.get(bucket, 0) >= bucket_cap:
        continue

    selected_rows.append(row)
    source_counts[source] = source_counts.get(source, 0) + 1
    bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    if len(selected_rows) >= target_n:
        break

# segunda passagem, se faltar completar
if len(selected_rows) < target_n:
    already_keys = {row["record_key"] for row in selected_rows}
    for _, row in reading_all.iterrows():
        if row["record_key"] in already_keys:
            continue
        selected_rows.append(row)
        already_keys.add(row["record_key"])
        if len(selected_rows) >= target_n:
            break

reading_top100 = pd.DataFrame(selected_rows)

reading_all.to_csv(OUTPUT_ALL, index=False, encoding="utf-8-sig")
reading_top100.to_csv(OUTPUT_TOP100, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_ALL}")
print(f"Arquivo salvo em: {OUTPUT_TOP100}")
print(f"Total reading corpus final: {len(reading_all)}")
print(f"Total top100 final: {len(reading_top100)}")
print("Distribuição por fonte no top100:")
if len(reading_top100) > 0:
    print(reading_top100["source_file"].value_counts().to_string())