from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Iterable

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
DATA_DIR = BASE_DIR / "data"

AUTO_FILE = FINAL_DIR / "bibliometric_corpus_final_v2.csv"

CLAUDE_CANDIDATES = [
    FINAL_DIR / "corpus_curated_v3_claude.csv",
    DATA_DIR / "corpus_curated_v3_claude.csv",
    FINAL_DIR / "claude_curation.csv",
    DATA_DIR / "claude_curation.csv",
]

OUTPUT_KEEP = FINAL_DIR / "bibliometric_corpus_final_v3.csv"
OUTPUT_REVIEW = FINAL_DIR / "bibliometric_corpus_review_queue.csv"
OUTPUT_EXCLUDED = FINAL_DIR / "bibliometric_corpus_excluded.csv"
OUTPUT_READING = FINAL_DIR / "reading_corpus_final_v3.csv"
OUTPUT_READING_TOP80 = FINAL_DIR / "reading_corpus_final_v3_top80.csv"
OUTPUT_REPORT = FINAL_DIR / "claude_integration_report.json"


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def to_bool(series: pd.Series) -> pd.Series:
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes", "y", "sim"])
    )


def find_existing_file(candidates: Iterable[Path]) -> Path:
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Não encontrei o arquivo da curadoria do Claude. "
        "Procurei por: " + ", ".join(str(p) for p in candidates)
    )


def find_column(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    normalized = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.strip().lower() in normalized:
            return normalized[cand.strip().lower()]
    if required:
        raise KeyError(
            f"Não encontrei nenhuma das colunas esperadas: {candidates}. "
            f"Colunas disponíveis: {list(df.columns)}"
        )
    return None


def build_key(row: pd.Series) -> str:
    def pick_text(*candidates) -> str:
        for value in candidates:
            text = norm_text(value)
            if text:
                return text
        return ""

    doi = pick_text(
        row.get("doi_clean", ""),
        row.get("doi", ""),
    )

    # normalização extra de DOI
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").replace("doi:", "").strip()

    title = pick_text(
        row.get("title_clean", ""),
        row.get("title", ""),
    )

    journal = pick_text(
        row.get("journal_clean", ""),
        row.get("journal", ""),
    )

    year_raw = row.get("publication_year", "")
    year = str(year_raw).strip()
    if year.endswith(".0"):
        year = year[:-2]

    if doi:
        return f"doi::{doi}"
    return f"txt::{title}::{year}::{journal}"

def ensure_text_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    return df


def ensure_numeric_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def main() -> None:
    auto_df = pd.read_csv(AUTO_FILE, low_memory=False)
    claude_file = find_existing_file(CLAUDE_CANDIDATES)
    claude_df = pd.read_csv(claude_file, low_memory=False)

    auto_df = ensure_text_columns(
        auto_df,
        [
            "title",
            "title_clean",
            "journal",
            "journal_clean",
            "doi_clean",
            "query_term_clean",
            "source_file",
            "thematic_bucket",
            "primary_type",
            "curated_decision",
            "curated_relevance_level",
            "curated_reason",
            "curated_notes",
            "possible_duplicate_reason",
            "suggested_thematic_cluster",
            "confidence_level",
        ],
    )
    auto_df = ensure_numeric_columns(
        auto_df,
        ["citation_count_unified", "publication_year", "completeness_score", "source_priority"],
    )

    auto_df["record_key"] = auto_df.apply(build_key, axis=1)

    decision_col = find_column(
        claude_df,
        ["curated_decision", "decision", "final_decision", "claude_decision"],
        required=True,
    )
    relevance_col = find_column(
        claude_df,
        ["curated_relevance_level", "relevance_level", "relevance", "curated_relevance"],
        required=False,
    )
    reason_col = find_column(
        claude_df,
        ["curated_reason", "reason", "classification_reason"],
        required=False,
    )
    notes_col = find_column(
        claude_df,
        ["curated_notes", "notes", "note", "justification"],
        required=False,
    )
    dup_flag_col = find_column(
        claude_df,
        ["possible_duplicate_flag", "duplicate_flag", "is_duplicate"],
        required=False,
    )
    dup_reason_col = find_column(
        claude_df,
        ["possible_duplicate_reason", "duplicate_reason"],
        required=False,
    )
    cluster_col = find_column(
        claude_df,
        ["suggested_thematic_cluster", "thematic_cluster", "cluster"],
        required=False,
    )
    confidence_col = find_column(
        claude_df,
        ["confidence_level", "confidence"],
        required=False,
    )

    claude_df = ensure_text_columns(
        claude_df,
        ["title", "title_clean", "journal", "journal_clean", "doi_clean", "publication_year"],
    )
    if "publication_year" in claude_df.columns:
        claude_df["publication_year"] = pd.to_numeric(claude_df["publication_year"], errors="coerce").fillna(0)

    claude_df["record_key"] = claude_df.apply(build_key, axis=1)

    curated_cols = ["record_key", decision_col]
    rename_map = {decision_col: "claude_curated_decision"}

    optional_map = {
        relevance_col: "claude_curated_relevance_level",
        reason_col: "claude_curated_reason",
        notes_col: "claude_curated_notes",
        dup_flag_col: "claude_possible_duplicate_flag",
        dup_reason_col: "claude_possible_duplicate_reason",
        cluster_col: "claude_suggested_thematic_cluster",
        confidence_col: "claude_confidence_level",
    }
    for col, new_name in optional_map.items():
        if col is not None:
            curated_cols.append(col)
            rename_map[col] = new_name

    curated_df = claude_df[curated_cols].copy().rename(columns=rename_map)

    if "claude_possible_duplicate_flag" in curated_df.columns:
        curated_df["claude_possible_duplicate_flag"] = (
            curated_df["claude_possible_duplicate_flag"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(
                {
                    "1": 1,
                    "true": 1,
                    "yes": 1,
                    "sim": 1,
                    "0": 0,
                    "false": 0,
                    "no": 0,
                    "não": 0,
                    "nao": 0,
                }
            )
            .fillna(0)
            .astype(int)
        )

    curated_df["claude_curated_decision"] = (
        curated_df["claude_curated_decision"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    merged = auto_df.merge(curated_df, on="record_key", how="left")

    merged["claude_curated_decision"] = merged["claude_curated_decision"].fillna("revisar")

    keep_labels = {"manter", "keep"}
    review_labels = {"revisar", "review", "revise"}
    exclude_labels = {"excluir", "exclude", "drop"}

    keep_df = merged[merged["claude_curated_decision"].isin(keep_labels)].copy()
    review_df = merged[merged["claude_curated_decision"].isin(review_labels)].copy()
    excluded_df = merged[merged["claude_curated_decision"].isin(exclude_labels)].copy()

    undecided_df = merged[
        ~merged["claude_curated_decision"].isin(keep_labels | review_labels | exclude_labels)
    ].copy()
    if len(undecided_df) > 0:
        undecided_df["claude_curated_decision"] = "revisar"
        review_df = pd.concat([review_df, undecided_df], ignore_index=True)

    keep_df = keep_df.sort_values(
        by=["completeness_score", "source_priority", "citation_count_unified"],
        ascending=[False, False, False],
    )

    with_doi = keep_df[keep_df["doi_clean"].fillna("").astype(str).str.strip() != ""].copy()
    without_doi = keep_df[keep_df["doi_clean"].fillna("").astype(str).str.strip() == ""].copy()

    with_doi = with_doi.drop_duplicates(subset=["doi_clean"], keep="first")
    without_doi = without_doi.drop_duplicates(
        subset=["title_clean", "publication_year", "journal_clean"],
        keep="first",
    )

    keep_df = pd.concat([with_doi, without_doi], ignore_index=True)

    for col in ["has_authors", "has_abstract", "focus_title_flag"]:
        if col not in keep_df.columns:
            keep_df[col] = False
        keep_df[col] = to_bool(keep_df[col])

    if "claude_curated_relevance_level" not in keep_df.columns:
        keep_df["claude_curated_relevance_level"] = ""
    if "claude_confidence_level" not in keep_df.columns:
        keep_df["claude_confidence_level"] = ""

    keep_df["reading_priority_score"] = (
        keep_df["has_authors"].astype(int)
        + keep_df["has_abstract"].astype(int)
        + keep_df["focus_title_flag"].astype(int)
        + (keep_df["citation_count_unified"] > 0).astype(int)
        + keep_df["claude_curated_relevance_level"].fillna("").astype(str).str.lower().isin(
            ["central", "partially_relevant", "parcialmente_relevante", "parcialmente relevante"]
        ).astype(int)
    )

    keep_df["reading_priority_score"] += keep_df["claude_confidence_level"].fillna("").astype(str).str.lower().map(
        {"alta": 2, "high": 2, "média": 1, "media": 1, "medium": 1, "baixa": 0, "low": 0}
    ).fillna(0)

    reading_df = keep_df.sort_values(
        by=["reading_priority_score", "citation_count_unified", "publication_year"],
        ascending=[False, False, False],
    ).copy()

    bucket_caps = {
        "policy_admin_governance": 30,
        "reform": 30,
        "cnj_brazil": 20,
    }

    selected = []
    seen = set()
    bucket_counts: dict[str, int] = {}

    for _, row in reading_df.iterrows():
        key = row["record_key"]
        if key in seen:
            continue

        bucket = str(row.get("thematic_bucket", "")).strip().lower()
        cap = bucket_caps.get(bucket, 15)

        if bucket_counts.get(bucket, 0) >= cap:
            continue

        selected.append(row)
        seen.add(key)
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        if len(selected) >= 80:
            break

    if len(selected) < 80:
        for _, row in reading_df.iterrows():
            key = row["record_key"]
            if key in seen:
                continue
            selected.append(row)
            seen.add(key)
            if len(selected) >= 80:
                break

    reading_top80 = pd.DataFrame(selected)

    keep_df.to_csv(OUTPUT_KEEP, index=False, encoding="utf-8-sig")
    review_df.to_csv(OUTPUT_REVIEW, index=False, encoding="utf-8-sig")
    excluded_df.to_csv(OUTPUT_EXCLUDED, index=False, encoding="utf-8-sig")
    reading_df.to_csv(OUTPUT_READING, index=False, encoding="utf-8-sig")
    reading_top80.to_csv(OUTPUT_READING_TOP80, index=False, encoding="utf-8-sig")

    report = {
        "automatic_input_rows": int(len(auto_df)),
        "claude_input_rows": int(len(claude_df)),
        "keep_rows_final": int(len(keep_df)),
        "review_rows": int(len(review_df)),
        "excluded_rows": int(len(excluded_df)),
        "reading_rows": int(len(reading_df)),
        "reading_top80_rows": int(len(reading_top80)),
        "claude_file_used": str(claude_file),
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo usado da curadoria Claude: {claude_file}")
    print(f"Arquivo salvo em: {OUTPUT_KEEP}")
    print(f"Arquivo salvo em: {OUTPUT_REVIEW}")
    print(f"Arquivo salvo em: {OUTPUT_EXCLUDED}")
    print(f"Arquivo salvo em: {OUTPUT_READING}")
    print(f"Arquivo salvo em: {OUTPUT_READING_TOP80}")
    print(f"Relatório salvo em: {OUTPUT_REPORT}")
    print(f"Total automático de entrada: {len(auto_df)}")
    print(f"Total Claude de entrada: {len(claude_df)}")
    print(f"Total final manter: {len(keep_df)}")
    print(f"Total fila de revisão: {len(review_df)}")
    print(f"Total excluídos: {len(excluded_df)}")
    print(f"Total reading final: {len(reading_df)}")
    print(f"Total reading top80: {len(reading_top80)}")


if __name__ == "__main__":
    main()