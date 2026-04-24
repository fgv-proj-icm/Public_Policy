from pathlib import Path
import json
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

BIBLIO_FILE = FINAL_DIR / "bibliometric_corpus_final.csv"
AGENDA_FILE = FINAL_DIR / "reading_agenda_rebalanced.csv"

OUTPUT_BIBLIO_V2 = FINAL_DIR / "bibliometric_corpus_final_v2.csv"
OUTPUT_REMOVED = FINAL_DIR / "bibliometric_removed_by_curated_filter.csv"
OUTPUT_READING = FINAL_DIR / "reading_corpus_final_curated.csv"
OUTPUT_READING_TOP100 = FINAL_DIR / "reading_corpus_final_curated_top100.csv"
OUTPUT_REPORT = FINAL_DIR / "curated_corpora_report.json"


CORE_KEEP_HINTS = [
    "judicial administration",
    "court administration",
    "judicial governance",
    "court governance",
    "judicial policy",
    "judicial policies",
    "judicial reform",
    "reforma judicial",
    "reforma do judiciário",
    "política judiciária",
    "políticas judiciárias",
    "administração judiciária",
    "governança judicial",
    "conselho nacional de justiça",
    "court management",
    "judicial management",
    "case management",
    "judicial performance",
    "court performance",
    "judicial efficiency",
    "court efficiency",
    "video-hearings",
    "online dispute resolution",
    "smart court",
    "smart courts",
    "judicial transparency",
    "court finance",
    "court staff",
    "specialized courts",
    "self-governance",
]

DROP_HINTS = [
    "environmental management",
    "environmental courts",
    "land and environment court",
    "psychotraumatology",
    "sexual offenders",
    "sexual assault",
    "marriage law",
    "child victimization",
    "refugee",
    "bail decisions",
    "homestead",
    "lepidopter",
    "climate change litigation",
    "journal of peace research",
]


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
    doi = norm_text(row.get("doi_clean", ""))
    title = norm_text(row.get("title_clean", ""))
    year = str(row.get("publication_year", "")).strip()
    journal = norm_text(row.get("journal_clean", ""))

    if doi:
        return f"doi::{doi}"
    return f"txt::{title}::{year}::{journal}"


def has_any_hint(text: str, hints: list[str]) -> bool:
    return any(h in text for h in hints)


def main() -> None:
    biblio = pd.read_csv(BIBLIO_FILE, low_memory=False)
    agenda = pd.read_csv(AGENDA_FILE, low_memory=False)

    for df in [biblio, agenda]:
        for col in [
            "title",
            "title_clean",
            "journal",
            "journal_clean",
            "query_term_clean",
            "doi_clean",
            "publication_year",
            "source_file",
            "thematic_bucket",
            "citation_count_unified",
            "completeness_score",
            "source_priority",
            "has_authors",
            "has_abstract",
            "has_journal",
            "focus_title_flag",
            "in_strict_seed",
        ]:
            if col not in df.columns:
                df[col] = ""

    # normalização
    for col in ["title", "title_clean", "journal", "journal_clean", "query_term_clean", "doi_clean", "thematic_bucket", "source_file"]:
        biblio[col] = biblio[col].apply(norm_text)
        agenda[col] = agenda[col].apply(norm_text)

    for col in ["has_authors", "has_abstract", "has_journal", "focus_title_flag", "in_strict_seed"]:
        biblio[col] = to_bool(biblio[col])

    for col in ["citation_count_unified", "completeness_score", "source_priority"]:
        biblio[col] = pd.to_numeric(biblio[col], errors="coerce").fillna(0)

    # chave e dedup estrutural mais dura
    biblio["record_key"] = biblio.apply(build_key, axis=1)

    biblio = biblio.sort_values(
        by=["completeness_score", "source_priority", "citation_count_unified"],
        ascending=[False, False, False],
    )

    # 1) por DOI
    with_doi = biblio[biblio["doi_clean"] != ""].copy()
    without_doi = biblio[biblio["doi_clean"] == ""].copy()

    with_doi = with_doi.drop_duplicates(subset=["doi_clean"], keep="first")
    without_doi = without_doi.drop_duplicates(
        subset=["title_clean", "publication_year", "journal_clean"],
        keep="first",
    )

    biblio_v2 = pd.concat([with_doi, without_doi], ignore_index=True)

    # 2) dedup extra por título+ano+jornal mesmo quando houver DOI diferente
    biblio_v2 = biblio_v2.sort_values(
        by=["completeness_score", "source_priority", "citation_count_unified"],
        ascending=[False, False, False],
    ).drop_duplicates(
        subset=["title_clean", "publication_year", "journal_clean"],
        keep="first",
    )

    # filtro temático fino
    combined_text = (
        biblio_v2["title_clean"].fillna("")
        + " "
        + biblio_v2["journal_clean"].fillna("")
        + " "
        + biblio_v2["query_term_clean"].fillna("")
    )

    biblio_v2["curated_keep_signal"] = combined_text.apply(lambda x: has_any_hint(x, CORE_KEEP_HINTS))
    biblio_v2["curated_drop_signal"] = combined_text.apply(lambda x: has_any_hint(x, DROP_HINTS))

    # buckets aceitos para bibliometria final
    allowed_buckets = {"policy_admin_governance", "reform", "cnj_brazil"}

    biblio_v2["curated_keep_flag"] = (
        biblio_v2["thematic_bucket"].isin(allowed_buckets)
        & biblio_v2["curated_keep_signal"]
        & (~biblio_v2["curated_drop_signal"])
    )

    removed = biblio_v2[~biblio_v2["curated_keep_flag"]].copy()
    biblio_curated = biblio_v2[biblio_v2["curated_keep_flag"]].copy()

    # reading corpus curado = agenda rebalanceada intersectada com bibliométrico curado
    agenda["record_key"] = agenda.apply(build_key, axis=1)

    reading = agenda.merge(
        biblio_curated.drop_duplicates(subset=["record_key"]),
        on="record_key",
        how="inner",
        suffixes=("_agenda", ""),
    )

    for col in ["agenda_score", "agenda_score_rebalanced"]:
        if col not in reading.columns:
            reading[col] = 0
        reading[col] = pd.to_numeric(reading[col], errors="coerce").fillna(0)

    for col in ["has_authors", "has_abstract", "focus_title_flag", "in_strict_seed"]:
        if col not in reading.columns:
            reading[col] = False
        reading[col] = to_bool(reading[col])

    reading["citation_count_unified"] = pd.to_numeric(reading["citation_count_unified"], errors="coerce").fillna(0)
    reading["publication_year"] = pd.to_numeric(reading["publication_year"], errors="coerce")

    citation_q3 = float(reading["citation_count_unified"].quantile(0.75)) if len(reading) else 0

    reading["reading_score_curated"] = (
        reading["agenda_score_rebalanced"]
        + reading["has_authors"].astype(int)
        + reading["has_abstract"].astype(int)
        + reading["focus_title_flag"].astype(int)
        + reading["in_strict_seed"].astype(int)
        + (reading["citation_count_unified"] >= citation_q3).astype(int)
    )

    reading = reading.sort_values(
        by=["reading_score_curated", "agenda_score_rebalanced", "citation_count_unified", "publication_year"],
        ascending=[False, False, False, False],
    )

    # top100 balanceado
    source_cap = {
        "semantic_scholar_results_core.csv": 30,
        "crossref_results_refined.csv": 30,
        "openalex_results_refined.csv": 30,
        "scopus_results_refined.csv": 10,
    }
    bucket_cap = {
        "policy_admin_governance": 45,
        "reform": 40,
        "cnj_brazil": 20,
    }

    source_counts = {}
    bucket_counts = {}
    selected_rows = []
    seen_keys = set()

    for _, row in reading.iterrows():
        key = row["record_key"]
        if key in seen_keys:
            continue

        source = row.get("source_file", "")
        bucket = row.get("thematic_bucket", "")

        if source_counts.get(source, 0) >= source_cap.get(source, 10):
            continue
        if bucket_counts.get(bucket, 0) >= bucket_cap.get(bucket, 15):
            continue

        selected_rows.append(row)
        seen_keys.add(key)
        source_counts[source] = source_counts.get(source, 0) + 1
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        if len(selected_rows) >= 100:
            break

    if len(selected_rows) < 100:
        for _, row in reading.iterrows():
            key = row["record_key"]
            if key in seen_keys:
                continue
            selected_rows.append(row)
            seen_keys.add(key)
            if len(selected_rows) >= 100:
                break

    reading_top100 = pd.DataFrame(selected_rows)

    biblio_curated.to_csv(OUTPUT_BIBLIO_V2, index=False, encoding="utf-8-sig")
    removed.to_csv(OUTPUT_REMOVED, index=False, encoding="utf-8-sig")
    reading.to_csv(OUTPUT_READING, index=False, encoding="utf-8-sig")
    reading_top100.to_csv(OUTPUT_READING_TOP100, index=False, encoding="utf-8-sig")

    report = {
        "input_bibliometric_rows": int(len(biblio)),
        "biblio_v2_rows_after_dedup": int(len(biblio_v2)),
        "biblio_curated_rows": int(len(biblio_curated)),
        "removed_rows": int(len(removed)),
        "reading_rows": int(len(reading)),
        "reading_top100_rows": int(len(reading_top100)),
        "citation_q3_reading": citation_q3,
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {OUTPUT_BIBLIO_V2}")
    print(f"Arquivo salvo em: {OUTPUT_REMOVED}")
    print(f"Arquivo salvo em: {OUTPUT_READING}")
    print(f"Arquivo salvo em: {OUTPUT_READING_TOP100}")
    print(f"Relatório salvo em: {OUTPUT_REPORT}")
    print(f"Total bibliometric original: {len(biblio)}")
    print(f"Total bibliometric v2: {len(biblio_curated)}")
    print(f"Total reading curated: {len(reading)}")
    print(f"Total top100 curated: {len(reading_top100)}")


if __name__ == "__main__":
    main()