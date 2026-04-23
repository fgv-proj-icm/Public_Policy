from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "focus_corpus_policy_admin.csv"
OUTPUT_ALL = FINAL_DIR / "reading_agenda_top.csv"
OUTPUT_TOP50 = FINAL_DIR / "reading_agenda_top50.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

for col in [
    "doi_clean",
    "has_journal",
    "has_authors",
    "has_abstract",
    "primary_type",
    "query_term_clean",
    "relevance_flag",
    "citation_count_unified",
    "publication_year",
]:
    if col not in df.columns:
        df[col] = ""

df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")

for col in ["has_journal", "has_authors", "has_abstract"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

df["relevance_flag"] = pd.to_numeric(df["relevance_flag"], errors="coerce").fillna(0).astype(int)
df["primary_type"] = df["primary_type"].fillna("nd").astype(str).str.strip().str.lower()
df["query_term_clean"] = df["query_term_clean"].fillna("nd").astype(str).str.strip().str.lower()

CORE_QUERY_TERMS = {
    "judicial policy",
    "judicial policies",
    "judicial governance",
    "judicial administration",
    "court administration",
    "court governance",
    "judicial reform",
    "política judiciária",
    "políticas judiciárias",
    "governança judicial",
    "administração judiciária",
    "reforma do judiciário",
    "reforma judicial",
    "conselho nacional de justiça",
}

citation_median = df["citation_count_unified"].median()

df["score_doi"] = df["doi_clean"].fillna("").astype(str).str.strip().ne("").astype(int)
df["score_journal"] = df["has_journal"].astype(int)
df["score_authors"] = df["has_authors"].astype(int)
df["score_abstract"] = df["has_abstract"].astype(int)
df["score_type"] = df["primary_type"].isin(["article", "review"]).astype(int)
df["score_query_core"] = df["query_term_clean"].isin(CORE_QUERY_TERMS).astype(int)
df["score_relevance"] = (df["relevance_flag"] == 1).astype(int)
df["score_citation"] = (df["citation_count_unified"] >= citation_median).astype(int)

score_cols = [
    "score_doi",
    "score_journal",
    "score_authors",
    "score_abstract",
    "score_type",
    "score_query_core",
    "score_relevance",
    "score_citation",
]

df["agenda_score"] = df[score_cols].sum(axis=1)

def bucket(row) -> str:
    if row["citation_count_unified"] >= 100:
        return "foundational"
    if row["agenda_score"] >= 7:
        return "priority"
    return "supporting"

df["agenda_bucket"] = df.apply(bucket, axis=1)

agenda = df[df["agenda_score"] >= 5].copy()
agenda = agenda.sort_values(
    by=["agenda_score", "citation_count_unified", "publication_year"],
    ascending=[False, False, False],
)

agenda_top50 = agenda.head(50).copy()

agenda.to_csv(OUTPUT_ALL, index=False, encoding="utf-8-sig")
agenda_top50.to_csv(OUTPUT_TOP50, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_ALL}")
print(f"Arquivo salvo em: {OUTPUT_TOP50}")
print(f"Mediana de citações do focus corpus: {citation_median}")
print(f"Total agenda (score >= 5): {len(agenda)}")
print(f"Total top50: {len(agenda_top50)}")
