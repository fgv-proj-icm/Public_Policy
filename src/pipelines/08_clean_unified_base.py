from __future__ import annotations

from pathlib import Path
import json
import re

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base.csv"
OUTPUT_FILE = FINAL_DIR / "unified_base_clean.csv"
REPORT_FILE = FINAL_DIR / "unified_base_clean_report.json"

COMPLETENESS_FIELDS = [
    "abstract",
    "authors",
    "publication_date",
    "journal",
    "language",
    "url",
    "concepts",
    "institutions",
]

TYPE_MAP = {
    "article": "article",
    "journal-article": "article",
    "journalarticle": "article",
    "review": "review",
    "book chapter": "book_chapter",
    "bookchapter": "book_chapter",
    "chapter": "book_chapter",
}


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_doi(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.strip()


def harmonize_type(value) -> str:
    text = norm_text(value)
    return TYPE_MAP.get(text, text)


def completeness_score(row: pd.Series) -> int:
    score = 0
    for field in COMPLETENESS_FIELDS:
        value = row.get(field, "")
        if pd.notna(value) and str(value).strip() not in ("", "nan", "N/D"):
            score += 1
    return score


def source_priority(row: pd.Series) -> int:
    source_file = str(row.get("source_file", "")).lower()
    if "crossref" in source_file:
        return 4
    if "semantic_scholar" in source_file:
        return 3
    if "scopus" in source_file:
        return 2
    if "openalex" in source_file:
        return 1
    return 0


def dedup_by_best_record(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    work = df.copy()
    work["completeness_score"] = work.apply(completeness_score, axis=1)
    work["source_priority"] = work.apply(source_priority, axis=1)
    work["citation_count_unified"] = pd.to_numeric(
        work.get("citation_count_unified", 0), errors="coerce"
    ).fillna(0)

    work = work.sort_values(
        by=["completeness_score", "source_priority", "citation_count_unified"],
        ascending=[False, False, False],
    )

    return work.drop_duplicates(subset=subset, keep="first")


def main() -> None:
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    n_initial = len(df)

    df["doi_clean"] = df["doi"].apply(clean_doi) if "doi" in df.columns else ""
    df["title_clean"] = df["title"].apply(norm_text) if "title" in df.columns else ""
    df["journal_clean"] = df["journal"].apply(norm_text) if "journal" in df.columns else ""
    df["type_clean"] = df["type"].apply(harmonize_type) if "type" in df.columns else ""
    df["year_clean"] = df["publication_year"].fillna("").astype(str).str.strip()

    with_doi = df[df["doi_clean"] != ""].copy()
    without_doi = df[df["doi_clean"] == ""].copy()

    n_with_doi = len(with_doi)
    n_unique_doi = with_doi["doi_clean"].nunique()
    n_dup_doi = n_with_doi - n_unique_doi

    fallback_subset = ["title_clean", "year_clean", "journal_clean"]
    n_without_doi = len(without_doi)
    n_unique_fallback = without_doi[fallback_subset].drop_duplicates().shape[0]
    n_dup_fallback = n_without_doi - n_unique_fallback

    dedup_doi = dedup_by_best_record(with_doi, ["doi_clean"])
    dedup_no_doi = dedup_by_best_record(without_doi, fallback_subset)

    df_clean = pd.concat([dedup_doi, dedup_no_doi], ignore_index=True)

    n_final = len(df_clean)

    df_clean.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    report = {
        "input_file": str(INPUT_FILE),
        "output_file": str(OUTPUT_FILE),
        "n_initial": int(n_initial),
        "n_with_doi": int(n_with_doi),
        "n_unique_doi_clean": int(n_unique_doi),
        "n_removed_by_doi_clean": int(n_dup_doi),
        "n_without_doi": int(n_without_doi),
        "n_unique_title_year_journal_no_doi": int(n_unique_fallback),
        "n_removed_by_title_year_journal_no_doi": int(n_dup_fallback),
        "n_final": int(n_final),
        "n_total_removed": int(n_initial - n_final),
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {OUTPUT_FILE}")
    print(f"Relatório salvo em: {REPORT_FILE}")
    print(f"Total inicial: {n_initial}")
    print(f"Removidos por DOI limpo: {n_dup_doi}")
    print(f"Removidos por título+ano+periódico sem DOI: {n_dup_fallback}")
    print(f"Total final: {n_final}")


if __name__ == "__main__":
    main()
