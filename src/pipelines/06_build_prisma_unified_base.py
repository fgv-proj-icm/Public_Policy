from pathlib import Path
import json
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
FINAL_DIR = BASE_DIR / "data" / "final"

SOURCE_FILES = [
    ("openalex_results_refined.csv", "openalex", 3),
    ("crossref_results_refined.csv", "crossref", 4),
    ("scopus_results_refined.csv", "scopus", 2),
    ("semantic_scholar_results_core.csv", "semantic_scholar", 1),
]

OUTPUT_IDENTIFIED = FINAL_DIR / "prisma_identified_dedup.csv"
OUTPUT_CORE = FINAL_DIR / "prisma_core_ex.csv"
OUTPUT_ADJ = FINAL_DIR / "prisma_adjacent.csv"
OUTPUT_EXCLUDED = FINAL_DIR / "prisma_excluded.csv"
OUTPUT_LOG = FINAL_DIR / "prisma_screening_log.csv"
OUTPUT_REPORT = FINAL_DIR / "prisma_report.json"

ALLOWED_DOC_GROUPS = {"article", "review", "paper"}

CORE_STRONG_PATTERNS = [
    r"\bpol[ií]tica judici[aá]ria\b",
    r"\bpol[ií]ticas judici[aá]rias\b",
    r"\bjudicial policies\b",
    r"\bjudiciary policies\b",
    r"\bjudiciary policy\b",
    r"\bpol[ií]tica judicial\b",
    r"\bpol[ií]ticas judiciales\b",
]

CORE_WEAK_PATTERNS = [
    r"\bjudicial policy\b",
]

INSTITUTIONAL_SUPPORT_PATTERNS = [
    r"\bjudicial administration\b",
    r"\bcourt administration\b",
    r"\bjudicial governance\b",
    r"\bcourt governance\b",
    r"\bcourt management\b",
    r"\bjudicial management\b",
    r"\bcase management\b",
    r"\bjudicial performance\b",
    r"\bcourt performance\b",
    r"\be-justice\b",
    r"\bdigital justice\b",
    r"\bconselho nacional de justi[cç]a\b",
    r"\bcnj\b",
    r"\bpoder judici[aá]rio\b",
    r"\badministra[cç][aã]o judici[aá]ria\b",
    r"\bgovernan[cç]a judicial\b",
    r"\bgest[aã]o judicial\b",
    r"\bgest[aã]o de tribunais\b",
    r"\badministra[cç][aã]o da justi[cç]a\b",
]

ADJACENT_PATTERNS = [
    r"\bjudicial administration\b",
    r"\bcourt administration\b",
    r"\bjudicial governance\b",
    r"\bcourt governance\b",
    r"\bjudicial reform\b",
    r"\bcourt reform\b",
    r"\bjudicial management\b",
    r"\bcourt management\b",
    r"\bcase management\b",
    r"\bjudicial performance\b",
    r"\bcourt performance\b",
    r"\be-justice\b",
    r"\bdigital justice\b",
    r"\badministra[cç][aã]o judici[aá]ria\b",
    r"\bgovernan[cç]a judicial\b",
    r"\breforma judicial\b",
    r"\breforma do judici[aá]rio\b",
    r"\bgest[aã]o judicial\b",
    r"\bgest[aã]o de tribunais\b",
    r"\badministra[cç][aã]o da justi[cç]a\b",
    r"\bpol[ií]tica p[úu]blica do poder judici[aá]rio\b",
    r"\bpol[ií]ticas p[úu]blicas do poder judici[aá]rio\b",
    r"\bpublic policy of the judiciary\b",
    r"\bpublic policy for the judiciary\b",
    r"\bjudiciary public policy\b",
    r"\bjudiciary public policies\b",
]

NOISE_PATTERNS = [
    r"\bjudicial review\b",
    r"\bconstitutional court\b",
    r"\bsupreme court\b",
    r"\bcourts of appeals\b",
    r"\bconstitutional justice\b",
    r"\bjudicialization\b",
    r"\bjudicializa[cç][aã]o\b",
    r"\bactivis[mt]\b",
    r"\bjudicial policymaking\b",
]

TEXT_FIELDS_CORE = ["title", "abstract", "concepts"]
TEXT_FIELDS_ANY = ["title", "abstract", "concepts", "journal", "query_term", "query_norm"]


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_doi(value) -> str:
    text = norm_text(value)
    text = text.replace("https://doi.org/", "")
    text = text.replace("http://doi.org/", "")
    text = text.replace("doi:", "")
    return text.strip().strip("/")


def normalize_title(value) -> str:
    text = norm_text(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9áàâãéèêíïóôõöúçñ\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_doc_type(value) -> str:
    text = norm_text(value)

    article_values = {
        "article",
        "journal-article",
        "journal article",
        "journalarticle",
        "research-article",
        "research article",
    }
    review_values = {
        "review",
        "systematic review",
        "literature review",
    }
    paper_values = {
        "paper",
        "conference paper",
        "conference-paper",
        "proceedings article",
        "proceedings-article",
    }

    if text in article_values:
        return "article"
    if text in review_values:
        return "review"
    if text in paper_values:
        return "paper"

    if "review" in text and "book" not in text:
        return "review"
    if "article" in text:
        return "article"
    if "paper" in text:
        return "paper"

    return "other"


def ensure_columns(df: pd.DataFrame, source_name: str, source_file: str, source_priority: int) -> pd.DataFrame:
    needed = [
        "paper_id",
        "openalex_id",
        "scopus_id",
        "crossref_doi",
        "title",
        "journal",
        "abstract",
        "concepts",
        "authors",
        "url",
        "type",
        "language",
        "query_term",
        "query_norm",
        "publication_year",
        "publication_date",
        "doi",
        "citation_count",
        "cited_by_count",
    ]
    for col in needed:
        if col not in df.columns:
            df[col] = ""

    df["source"] = source_name
    df["source_file"] = source_file
    df["source_priority"] = source_priority

    text_cols = [
        "title",
        "journal",
        "abstract",
        "concepts",
        "authors",
        "url",
        "type",
        "language",
        "query_term",
        "query_norm",
        "publication_date",
        "doi",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("")

    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
    df["citation_count"] = pd.to_numeric(df["citation_count"], errors="coerce")
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce")

    df["title_clean"] = df["title"].apply(normalize_title)
    df["journal_clean"] = df["journal"].apply(normalize_title)
    df["doi_clean"] = df["doi"].apply(clean_doi)
    df["doc_type_group"] = df["type"].apply(normalize_doc_type)
    df["citation_count_unified"] = df["citation_count"].combine_first(df["cited_by_count"]).fillna(0)

    return df


def has_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def fields_with_pattern(row: pd.Series, fields: list[str], patterns: list[str]) -> list[str]:
    hits = []
    for field in fields:
        if has_pattern(norm_text(row.get(field, "")), patterns):
            hits.append(field)
    return hits


def completeness_score(row: pd.Series) -> int:
    cols = [
        "doi_clean",
        "title",
        "journal",
        "abstract",
        "authors",
        "publication_date",
        "language",
        "url",
        "concepts",
    ]
    return sum(1 for c in cols if norm_text(row.get(c, "")))


def load_sources() -> pd.DataFrame:
    frames = []

    for filename, source_name, source_priority in SOURCE_FILES:
        path = RAW_DIR / filename
        if not path.exists():
            print(f"Aviso: arquivo não encontrado -> {path.name}")
            continue

        df = pd.read_csv(path, low_memory=False)
        df = ensure_columns(df, source_name, filename, source_priority)
        frames.append(df)

    if not frames:
        raise RuntimeError("Nenhuma base refinada encontrada em data/raw.")

    return pd.concat(frames, ignore_index=True)


def classify_row(row: pd.Series) -> pd.Series:
    strong_core_hits = fields_with_pattern(row, TEXT_FIELDS_CORE, CORE_STRONG_PATTERNS)
    weak_core_hits = fields_with_pattern(row, TEXT_FIELDS_CORE, CORE_WEAK_PATTERNS)
    support_core_hits = fields_with_pattern(row, TEXT_FIELDS_CORE, INSTITUTIONAL_SUPPORT_PATTERNS)

    strong_any_hits = fields_with_pattern(row, TEXT_FIELDS_ANY, CORE_STRONG_PATTERNS)
    weak_any_hits = fields_with_pattern(row, TEXT_FIELDS_ANY, CORE_WEAK_PATTERNS)
    adjacent_any_hits = fields_with_pattern(row, TEXT_FIELDS_ANY, ADJACENT_PATTERNS)
    noise_any_hits = fields_with_pattern(row, TEXT_FIELDS_ANY, NOISE_PATTERNS)

    has_core_strong = len(strong_core_hits) > 0
    has_core_weak = len(weak_core_hits) > 0
    has_support = len(support_core_hits) > 0
    has_adjacent = len(adjacent_any_hits) > 0
    has_noise = len(noise_any_hits) > 0
    has_exact_any_outside_core = len(strong_any_hits + weak_any_hits) > 0 and not (has_core_strong or has_core_weak)

    if has_core_strong:
        prisma_decision = "include_core"
        prisma_reason = "exact_explicit_term_in_title_abstract_keywords"
        suggested_ring = "CORE_EX"
    elif has_core_weak and has_support:
        prisma_decision = "include_core"
        prisma_reason = "judicial_policy_singular_plus_institutional_support"
        suggested_ring = "CORE_EX"
    elif has_adjacent:
        prisma_decision = "include_adjacent"
        prisma_reason = "adjacent_cognate_term"
        suggested_ring = "ADJ"
    elif has_exact_any_outside_core:
        prisma_decision = "include_adjacent"
        prisma_reason = "exact_term_outside_core_fields"
        suggested_ring = "ADJ"
    elif has_noise:
        prisma_decision = "exclude"
        prisma_reason = "constitutional_review_or_judicialization_noise"
        suggested_ring = "EXCLUDE"
    else:
        prisma_decision = "exclude"
        prisma_reason = "no_core_or_adjacent_signal"
        suggested_ring = "EXCLUDE"

    return pd.Series(
        {
            "core_strong_hits": ";".join(strong_core_hits),
            "core_weak_hits": ";".join(weak_core_hits),
            "support_core_hits": ";".join(support_core_hits),
            "adjacent_any_hits": ";".join(adjacent_any_hits),
            "noise_any_hits": ";".join(noise_any_hits),
            "prisma_decision": prisma_decision,
            "prisma_reason": prisma_reason,
            "suggested_ring": suggested_ring,
        }
    )


def main() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    all_df = load_sources()
    identified_total = len(all_df)

    eligible_df = all_df[all_df["doc_type_group"].isin(ALLOWED_DOC_GROUPS)].copy()
    after_doc_type = len(eligible_df)

    eligible_df["has_doi"] = eligible_df["doi_clean"].fillna("").astype(str).str.strip().ne("")
    eligible_df["completeness_score"] = eligible_df.apply(completeness_score, axis=1)

    eligible_df = eligible_df.sort_values(
        by=["has_doi", "completeness_score", "source_priority", "citation_count_unified"],
        ascending=[False, False, False, False],
    )

    with_doi = eligible_df[eligible_df["has_doi"]].copy()
    without_doi = eligible_df[~eligible_df["has_doi"]].copy()

    before_dedup_doi = len(with_doi)
    before_dedup_no_doi = len(without_doi)

    with_doi = with_doi.drop_duplicates(subset=["doi_clean"], keep="first")
    without_doi = without_doi.drop_duplicates(
        subset=["title_clean", "publication_year", "journal_clean"],
        keep="first",
    )

    duplicates_removed_doi = before_dedup_doi - len(with_doi)
    duplicates_removed_no_doi = before_dedup_no_doi - len(without_doi)

    dedup_df = pd.concat([with_doi, without_doi], ignore_index=True)
    after_dedup = len(dedup_df)

    class_df = dedup_df.apply(classify_row, axis=1)
    screen_df = pd.concat([dedup_df, class_df], axis=1)

    core_df = screen_df[screen_df["prisma_decision"] == "include_core"].copy()
    adjacent_df = screen_df[screen_df["prisma_decision"] == "include_adjacent"].copy()
    excluded_df = screen_df[screen_df["prisma_decision"] == "exclude"].copy()

    screening_log = screen_df[
        [
            "source_file",
            "source",
            "title",
            "publication_year",
            "journal",
            "doi_clean",
            "doc_type_group",
            "query_term",
            "query_norm",
            "prisma_decision",
            "prisma_reason",
            "suggested_ring",
            "core_strong_hits",
            "core_weak_hits",
            "support_core_hits",
            "adjacent_any_hits",
            "noise_any_hits",
        ]
    ].copy()

    dedup_df.to_csv(OUTPUT_IDENTIFIED, index=False, encoding="utf-8-sig")
    core_df.to_csv(OUTPUT_CORE, index=False, encoding="utf-8-sig")
    adjacent_df.to_csv(OUTPUT_ADJ, index=False, encoding="utf-8-sig")
    excluded_df.to_csv(OUTPUT_EXCLUDED, index=False, encoding="utf-8-sig")
    screening_log.to_csv(OUTPUT_LOG, index=False, encoding="utf-8-sig")

    report = {
        "prisma_counts": {
            "identified_total": int(identified_total),
            "after_doc_type_filter": int(after_doc_type),
            "duplicates_removed_doi": int(duplicates_removed_doi),
            "duplicates_removed_fallback": int(duplicates_removed_no_doi),
            "after_dedup": int(after_dedup),
            "screened": int(len(screen_df)),
            "included_core_ex": int(len(core_df)),
            "included_adjacent": int(len(adjacent_df)),
            "excluded": int(len(excluded_df)),
        },
        "doc_groups_included": sorted(list(ALLOWED_DOC_GROUPS)),
        "core_by_source": core_df["source_file"].value_counts().to_dict(),
        "adjacent_by_source": adjacent_df["source_file"].value_counts().to_dict(),
        "excluded_by_reason": excluded_df["prisma_reason"].value_counts().to_dict(),
        "core_by_reason": core_df["prisma_reason"].value_counts().to_dict(),
        "adjacent_by_reason": adjacent_df["prisma_reason"].value_counts().to_dict(),
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {OUTPUT_IDENTIFIED}")
    print(f"Arquivo salvo em: {OUTPUT_CORE}")
    print(f"Arquivo salvo em: {OUTPUT_ADJ}")
    print(f"Arquivo salvo em: {OUTPUT_EXCLUDED}")
    print(f"Arquivo salvo em: {OUTPUT_LOG}")
    print(f"Relatório salvo em: {OUTPUT_REPORT}")
    print(f"Identificados: {identified_total}")
    print(f"Após filtro documental: {after_doc_type}")
    print(f"Após deduplicação: {after_dedup}")
    print(f"Incluídos CORE_EX: {len(core_df)}")
    print(f"Incluídos ADJ: {len(adjacent_df)}")
    print(f"Excluídos: {len(excluded_df)}")


if __name__ == "__main__":
    main()