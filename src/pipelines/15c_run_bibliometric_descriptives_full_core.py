from pathlib import Path
from collections import Counter
import json
import re
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
OUT_DIR = FINAL_DIR / "bibliometrics_full_core"

FULL_FILE = FINAL_DIR / "bibliometric_corpus_full_v1.csv"
CORE_FILE = FINAL_DIR / "bibliometric_corpus_core_v1.csv"

STOPWORDS = {
    "the", "of", "and", "in", "on", "for", "to", "a", "an", "with", "from", "by", "at", "or",
    "de", "da", "do", "das", "dos", "e", "em", "para", "por", "com", "na", "no", "nas", "nos",
    "la", "el", "en", "del", "y", "con", "los", "las",
    "judicial", "court", "courts", "justice", "policy", "policies", "reform", "governance",
    "administration"
}


def save_barplot(series: pd.Series, title: str, xlabel: str, ylabel: str, output_file: Path) -> None:
    plt.figure(figsize=(12, 6))
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_file, dpi=200)
    plt.close()


def tokenize(text: str) -> list[str]:
    text = str(text).lower()
    text = re.sub(r"[^a-záàâãéèêíïóôõöúçñ0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = []
    for token in text.split():
        if len(token) < 3:
            continue
        if token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def summarize_dataset(df: pd.DataFrame, label: str) -> None:
    out = OUT_DIR / label
    out.mkdir(parents=True, exist_ok=True)

    for col in ["publication_year", "citation_count_unified"]:
        if col not in df.columns:
            df[col] = 0

    for col in ["source_file", "thematic_bucket", "journal", "primary_type", "title_clean"]:
        if col not in df.columns:
            df[col] = ""

    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
    df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)

    publications_by_year = (
        df.dropna(subset=["publication_year"])
        .assign(publication_year=lambda x: x["publication_year"].astype(int))
        .groupby("publication_year")
        .size()
        .reset_index(name="n_publications")
        .sort_values("publication_year")
    )

    by_source = df.groupby("source_file").size().reset_index(name="n_records").sort_values("n_records", ascending=False)
    by_bucket = df.groupby("thematic_bucket").size().reset_index(name="n_records").sort_values("n_records", ascending=False)
    by_type = df.groupby("primary_type").size().reset_index(name="n_records").sort_values("n_records", ascending=False)

    top_journals = (
        df.assign(journal=df["journal"].fillna("N/D"))
        .groupby("journal")
        .agg(
            n_records=("journal", "size"),
            total_citations=("citation_count_unified", "sum"),
            mean_citations=("citation_count_unified", "mean"),
        )
        .reset_index()
        .sort_values(["n_records", "total_citations"], ascending=[False, False])
        .head(30)
    )

    top_articles = (
        df.sort_values(["citation_count_unified", "publication_year"], ascending=[False, False])
        [["title", "publication_year", "journal", "citation_count_unified", "thematic_bucket", "source_file"]]
        .head(50)
    )

    term_counter = Counter()
    for text in df["title_clean"].fillna("").astype(str):
        term_counter.update(tokenize(text))

    top_terms = pd.DataFrame(
        [{"term": term, "count": count} for term, count in term_counter.most_common(50)]
    )

    overview = {
        "label": label,
        "n_rows": int(len(df)),
        "n_columns": int(len(df.columns)),
        "total_citations": float(df["citation_count_unified"].sum()),
        "mean_citations": float(df["citation_count_unified"].mean()),
        "median_citations": float(df["citation_count_unified"].median()),
    }

    publications_by_year.to_csv(out / "publications_by_year.csv", index=False, encoding="utf-8-sig")
    by_source.to_csv(out / "records_by_source.csv", index=False, encoding="utf-8-sig")
    by_bucket.to_csv(out / "records_by_thematic_bucket.csv", index=False, encoding="utf-8-sig")
    by_type.to_csv(out / "records_by_primary_type.csv", index=False, encoding="utf-8-sig")
    top_journals.to_csv(out / "top_journals.csv", index=False, encoding="utf-8-sig")
    top_articles.to_csv(out / "top_articles_by_citations.csv", index=False, encoding="utf-8-sig")
    top_terms.to_csv(out / "top_title_terms.csv", index=False, encoding="utf-8-sig")

    with open(out / "overview.json", "w", encoding="utf-8") as f:
        json.dump(overview, f, ensure_ascii=False, indent=2)

    if len(publications_by_year):
        save_barplot(
            publications_by_year.set_index("publication_year")["n_publications"],
            f"Publicações por ano - {label.upper()}",
            "Ano",
            "Número de publicações",
            out / "publications_by_year.png",
        )

    if len(by_source):
        save_barplot(
            by_source.set_index("source_file")["n_records"],
            f"Registros por fonte - {label.upper()}",
            "Fonte",
            "Número de registros",
            out / "records_by_source.png",
        )

    if len(by_bucket):
        save_barplot(
            by_bucket.set_index("thematic_bucket")["n_records"],
            f"Registros por eixo temático - {label.upper()}",
            "Eixo temático",
            "Número de registros",
            out / "records_by_thematic_bucket.png",
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    full_df = pd.read_csv(FULL_FILE, low_memory=False)
    core_df = pd.read_csv(CORE_FILE, low_memory=False)

    summarize_dataset(full_df, "full")
    summarize_dataset(core_df, "core")

    print(f"Resultados salvos em: {OUT_DIR}")


if __name__ == "__main__":
    main()