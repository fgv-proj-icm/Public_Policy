from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "reading_list_final_top60.csv"
OUTPUT_FILE = FINAL_DIR / "reading_sheet_top60.csv"
OUTPUT_TOP20 = FINAL_DIR / "reading_sheet_top20_priority.csv"


def build_priority_tier(row: pd.Series) -> str:
    citations = pd.to_numeric(row.get("citation_count_unified", 0), errors="coerce")
    score = pd.to_numeric(row.get("reading_final_score", 0), errors="coerce")
    year = pd.to_numeric(row.get("publication_year", 0), errors="coerce")

    citations = 0 if pd.isna(citations) else citations
    score = 0 if pd.isna(score) else score
    year = 0 if pd.isna(year) else year

    if citations >= 20 or score >= 5:
        return "alta"
    if citations >= 5 or year >= 2018:
        return "media"
    return "baixa"


def main() -> None:
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    for col in [
        "title",
        "publication_year",
        "journal",
        "citation_count_unified",
        "thematic_bucket",
        "source_file",
        "reading_final_score",
    ]:
        if col not in df.columns:
            df[col] = ""

    df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
    df["reading_final_score"] = pd.to_numeric(df["reading_final_score"], errors="coerce").fillna(0)
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")

    df = df.sort_values(
        by=["thematic_bucket", "reading_final_score", "citation_count_unified", "publication_year"],
        ascending=[True, False, False, False],
    ).copy()

    df["reading_priority_tier"] = df.apply(build_priority_tier, axis=1)
    df["reading_order"] = range(1, len(df) + 1)

    # colunas para fichamento
    df["read_status"] = "nao_lido"
    df["pdf_found"] = ""
    df["problem_focus"] = ""
    df["country_or_case"] = ""
    df["institution_focus"] = ""
    df["method"] = ""
    df["data_type"] = ""
    df["main_argument"] = ""
    df["main_findings"] = ""
    df["relevance_for_research"] = ""
    df["use_in_writing"] = ""
    df["quote_or_note"] = ""
    df["final_keep_for_review"] = ""
    df["reviewer_notes"] = ""

    output_cols = [
        "reading_order",
        "reading_priority_tier",
        "read_status",
        "final_keep_for_review",
        "pdf_found",
        "title",
        "publication_year",
        "journal",
        "doi_clean"
        "citation_count_unified",
        "reading_final_score",
        "thematic_bucket",
        "source_file",
        "problem_focus",
        "country_or_case",
        "institution_focus",
        "method",
        "data_type",
        "main_argument",
        "main_findings",
        "relevance_for_research",
        "use_in_writing",
        "quote_or_note",
        "reviewer_notes",
    ]

    reading_sheet = df[output_cols].copy()

    # top20 prioritário: 7 por reform, 7 por policy_admin_governance, 6 por cnj_brazil
    caps = {
        "reform": 7,
        "policy_admin_governance": 7,
        "cnj_brazil": 6,
    }

    selected_rows = []
    counts = {k: 0 for k in caps}

    for _, row in reading_sheet.iterrows():
        bucket = str(row.get("thematic_bucket", "")).strip().lower()
        if bucket not in caps:
            continue
        if counts[bucket] >= caps[bucket]:
            continue

        selected_rows.append(row)
        counts[bucket] += 1

        if len(selected_rows) >= 20:
            break

    top20 = pd.DataFrame(selected_rows)

    reading_sheet.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    top20.to_csv(OUTPUT_TOP20, index=False, encoding="utf-8-sig")

    print(f"Arquivo salvo em: {OUTPUT_FILE}")
    print(f"Arquivo salvo em: {OUTPUT_TOP20}")
    print(f"Total reading sheet: {len(reading_sheet)}")
    print(f"Total top20 prioritario: {len(top20)}")


if __name__ == "__main__":
    main()