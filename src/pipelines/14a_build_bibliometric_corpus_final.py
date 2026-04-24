from pathlib import Path
import json
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

FOCUS_FILE = FINAL_DIR / "focus_corpus_policy_admin.csv"
STRICT_FILE = FINAL_DIR / "focus_corpus_strict.csv"

OUTPUT_FILE = FINAL_DIR / "bibliometric_corpus_final.csv"
REPORT_FILE = FINAL_DIR / "bibliometric_corpus_final_report.json"


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
        .isin(["true", "1", "yes"])
    )


def build_key(row: pd.Series) -> str:
    doi = str(row.get("doi_clean", "")).strip().lower()
    title = str(row.get("title_clean", "")).strip().lower()
    year = str(row.get("publication_year", "")).strip()
    journal = str(row.get("journal_clean", "")).strip().lower()

    if doi:
        return f"doi::{doi}"
    return f"txt::{title}::{year}::{journal}"


def classify_thematic_bucket(row: pd.Series) -> str:
    text = " ".join(
        [
            norm_text(row.get("title_clean", "")),
            norm_text(row.get("journal_clean", "")),
            norm_text(row.get("query_term_clean", "")),
        ]
    )

    if any(x in text for x in [
        "conselho nacional de justiça",
        "cnj",
        "política judiciária",
        "políticas judiciárias",
        "administração judiciária",
        "governança judicial",
        "poder judiciário",
    ]):
        return "cnj_brazil"

    if any(x in text for x in [
        "judicial administration",
        "court administration",
        "judicial governance",
        "court governance",
        "judicial policy",
        "judicial policies",
        "court management",
        "judicial management",
        "case management",
        "judicial performance",
        "court performance",
        "judicial efficiency",
        "court efficiency",
        "e-justice",
        "digital justice",
        "smart court",
        "smart courts",
    ]):
        return "policy_admin_governance"

    if any(x in text for x in [
        "judicial reform",
        "reforma judicial",
        "reforma do judiciário",
    ]):
        return "reform"

    if any(x in text for x in [
        "judicial review",
        "constitutional court",
        "supreme court",
        "constitutional law",
        "checks and balances",
    ]):
        return "judicial_review_constitutional"

    if any(x in text for x in [
        "access to justice",
        "legal aid",
        "mediation",
        "dispute resolution",
        "adr",
    ]):
        return "access_to_justice"

    return "other_focus"


def main() -> None:
    focus = pd.read_csv(FOCUS_FILE, low_memory=False)
    strict = pd.read_csv(STRICT_FILE, low_memory=False)

    # colunas mínimas
    for df in [focus, strict]:
        for col in [
            "title_clean",
            "journal_clean",
            "query_term_clean",
            "primary_type",
            "doi_clean",
            "citation_count_unified",
            "source_priority",
            "completeness_score",
            "publication_year",
        ]:
            if col not in df.columns:
                df[col] = ""

        for col in [
            "has_journal",
            "has_authors",
            "has_abstract",
            "journal_suspect_flag",
            "focus_title_flag",
            "focus_query_flag",
            "relevance_flag",
        ]:
            if col not in df.columns:
                df[col] = False

    # normalizações
    for col in ["title_clean", "journal_clean", "query_term_clean", "primary_type", "doi_clean"]:
        focus[col] = focus[col].apply(norm_text)
        strict[col] = strict[col].apply(norm_text)

    for col in ["has_journal", "has_authors", "has_abstract", "journal_suspect_flag", "focus_title_flag", "focus_query_flag"]:
        focus[col] = to_bool(focus[col])
        strict[col] = to_bool(strict[col])

    focus["relevance_flag"] = pd.to_numeric(focus["relevance_flag"], errors="coerce").fillna(0).astype(int)
    strict["relevance_flag"] = pd.to_numeric(strict["relevance_flag"], errors="coerce").fillna(0).astype(int)

    for col in ["citation_count_unified", "source_priority", "completeness_score"]:
        focus[col] = pd.to_numeric(focus[col], errors="coerce").fillna(0)
        strict[col] = pd.to_numeric(strict[col], errors="coerce").fillna(0)

    focus["record_key"] = focus.apply(build_key, axis=1)
    strict["record_key"] = strict.apply(build_key, axis=1)

    strict_keys = set(strict["record_key"].tolist())

    focus["in_strict_seed"] = focus["record_key"].isin(strict_keys)
    focus["thematic_bucket"] = focus.apply(classify_thematic_bucket, axis=1)

    citation_median = float(focus["citation_count_unified"].median())

    focus["biblio_score"] = (
        2 * focus["in_strict_seed"].astype(int)
        + 2 * focus["focus_title_flag"].astype(int)
        + 1 * focus["focus_query_flag"].astype(int)
        + 1 * focus["has_authors"].astype(int)
        + 1 * focus["has_abstract"].astype(int)
        + 1 * (focus["relevance_flag"] == 1).astype(int)
        + 1 * (focus["citation_count_unified"] >= citation_median).astype(int)
    )

    allowed_buckets = {"policy_admin_governance", "reform", "cnj_brazil"}

    bibliometric = focus[
        (focus["primary_type"].isin(["article", "review"]))
        & (focus["has_journal"])
        & (~focus["journal_suspect_flag"])
        & (focus["thematic_bucket"].isin(allowed_buckets))
        & (focus["biblio_score"] >= 4)
    ].copy()

    bibliometric = bibliometric.sort_values(
        by=["biblio_score", "completeness_score", "source_priority", "citation_count_unified"],
        ascending=[False, False, False, False],
    )

    with_doi = bibliometric[bibliometric["doi_clean"] != ""].copy()
    without_doi = bibliometric[bibliometric["doi_clean"] == ""].copy()

    with_doi = with_doi.drop_duplicates(subset=["doi_clean"], keep="first")
    without_doi = without_doi.drop_duplicates(
        subset=["title_clean", "publication_year", "journal_clean"],
        keep="first",
    )

    bibliometric_final = pd.concat([with_doi, without_doi], ignore_index=True)

    bibliometric_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    report = {
        "input_focus_rows": int(len(focus)),
        "input_strict_rows": int(len(strict)),
        "citation_median_focus": citation_median,
        "pre_dedup_rows": int(len(bibliometric)),
        "final_rows": int(len(bibliometric_final)),
        "allowed_buckets": sorted(list(allowed_buckets)),
        "score_threshold": 4,
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {OUTPUT_FILE}")
    print(f"Relatório salvo em: {REPORT_FILE}")
    print(f"Total focus entrada: {len(focus)}")
    print(f"Total strict semente: {len(strict)}")
    print(f"Total pré-dedup: {len(bibliometric)}")
    print(f"Total final: {len(bibliometric_final)}")


if __name__ == "__main__":
    main()