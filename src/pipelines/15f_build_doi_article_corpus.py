from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "bibliometric_corpus_final_v3.csv"

OUTPUT_FILE = FINAL_DIR / "bibliometric_corpus_final_v3_articles_doi_reviews_no_doi.csv"
OUTPUT_TOP50 = FINAL_DIR / "reading_list_final_articles_doi_reviews_no_doi_top50.csv"
OUTPUT_REPORT = FINAL_DIR / "articles_doi_reviews_no_doi_report.json"


def main() -> None:
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    for col in [
        "primary_type",
        "doi_clean",
        "citation_count_unified",
        "publication_year",
        "title",
        "journal",
        "thematic_bucket",
        "source_file",
    ]:
        if col not in df.columns:
            df[col] = ""

    df["primary_type"] = df["primary_type"].fillna("").astype(str).str.strip().str.lower()
    df["doi_clean"] = df["doi_clean"].fillna("").astype(str).str.strip().str.lower()
    df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")

    # Regra nova:
    # 1) artigo -> só entra se tiver DOI
    # 2) review -> só entra se NÃO tiver DOI
    mixed_df = df[
        (
            (df["primary_type"] == "article") & (df["doi_clean"] != "")
        )
        |
        (
            (df["primary_type"] == "review") & (df["doi_clean"] == "")
        )
    ].copy()

    # deduplicação:
    # - artigos com DOI: dedup por DOI
    # - reviews sem DOI: dedup por título + ano + periódico
    articles_with_doi = mixed_df[
        (mixed_df["primary_type"] == "article") & (mixed_df["doi_clean"] != "")
    ].copy()

    reviews_no_doi = mixed_df[
        (mixed_df["primary_type"] == "review") & (mixed_df["doi_clean"] == "")
    ].copy()

    articles_with_doi = articles_with_doi.sort_values(
        by=["citation_count_unified", "publication_year"],
        ascending=[False, False],
    ).drop_duplicates(subset=["doi_clean"], keep="first")

    reviews_no_doi = reviews_no_doi.sort_values(
        by=["citation_count_unified", "publication_year"],
        ascending=[False, False],
    ).drop_duplicates(
        subset=["title", "publication_year", "journal"],
        keep="first",
    )

    final_df = pd.concat([articles_with_doi, reviews_no_doi], ignore_index=True)

    # DOI URL só para quem tiver DOI
    final_df["doi_url"] = final_df["doi_clean"].apply(
        lambda x: f"https://doi.org/{x}" if str(x).strip() else ""
    )

    top50 = final_df.sort_values(
        by=["citation_count_unified", "publication_year"],
        ascending=[False, False],
    )[
        [
            "title",
            "publication_year",
            "journal",
            "primary_type",
            "doi_clean",
            "doi_url",
            "citation_count_unified",
            "thematic_bucket",
            "source_file",
        ]
    ].head(50).copy()

    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    top50.to_csv(OUTPUT_TOP50, index=False, encoding="utf-8-sig")

    report = {
        "input_rows": int(len(df)),
        "output_rows_total": int(len(final_df)),
        "output_rows_articles_with_doi": int(len(articles_with_doi)),
        "output_rows_reviews_without_doi": int(len(reviews_no_doi)),
        "top50_rows": int(len(top50)),
        "n_unique_article_doi": int(articles_with_doi["doi_clean"].nunique()),
        "n_unique_buckets": int(final_df["thematic_bucket"].nunique()),
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {OUTPUT_FILE}")
    print(f"Arquivo salvo em: {OUTPUT_TOP50}")
    print(f"Relatório salvo em: {OUTPUT_REPORT}")
    print(f"Total entrada: {len(df)}")
    print(f"Total final: {len(final_df)}")
    print(f"Artigos com DOI: {len(articles_with_doi)}")
    print(f"Reviews sem DOI: {len(reviews_no_doi)}")
    print(f"Total top50: {len(top50)}")


if __name__ == "__main__":
    main()
    