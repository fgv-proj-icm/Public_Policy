from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "bibliometric_corpus_core_v1.csv"

OUTPUT_CANDIDATES = FINAL_DIR / "reading_list_final_candidates.csv"
OUTPUT_TOP60 = FINAL_DIR / "reading_list_final_top60.csv"
OUTPUT_BY_BUCKET = FINAL_DIR / "reading_list_final_top20_by_bucket.csv"


def to_bool(series: pd.Series) -> pd.Series:
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes", "y", "sim"])
    )


def main() -> None:
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    for col in [
        "citation_count_unified",
        "publication_year",
        "completeness_score",
        "thematic_bucket",
        "claude_curated_relevance_level",
        "title",
        "journal",
        "source_file",
    ]:
        if col not in df.columns:
            df[col] = 0 if col in ["citation_count_unified", "publication_year", "completeness_score"] else ""

    for col in ["in_strict_seed", "has_abstract", "has_authors"]:
        if col not in df.columns:
            df[col] = False

    df["citation_count_unified"] = pd.to_numeric(df["citation_count_unified"], errors="coerce").fillna(0)
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
    df["completeness_score"] = pd.to_numeric(df["completeness_score"], errors="coerce").fillna(0)

    df["in_strict_seed"] = to_bool(df["in_strict_seed"])
    df["has_abstract"] = to_bool(df["has_abstract"])
    df["has_authors"] = to_bool(df["has_authors"])

    max_cit = df["citation_count_unified"].max() if len(df) else 1
    max_comp = df["completeness_score"].max() if len(df) else 1

    df["impact_norm"] = df["citation_count_unified"] / max_cit if max_cit > 0 else 0
    df["completeness_norm"] = df["completeness_score"] / max_comp if max_comp > 0 else 0
    df["recency_bonus"] = (df["publication_year"] >= 2018).fillna(False).astype(int)

    df["reading_final_score"] = (
        4 * df["impact_norm"]
        + 2 * df["in_strict_seed"].astype(int)
        + 1 * df["has_abstract"].astype(int)
        + 1 * df["has_authors"].astype(int)
        + 1 * df["recency_bonus"]
        + 1 * df["completeness_norm"]
    )

    df = df.sort_values(
        by=["thematic_bucket", "reading_final_score", "citation_count_unified", "publication_year"],
        ascending=[True, False, False, False],
    )

    caps = {
        "policy_admin_governance": 20,
        "reform": 20,
        "cnj_brazil": 20,
    }

    selected = []
    counts = {k: 0 for k in caps}
    seen_titles = set()

    for _, row in df.iterrows():
        bucket = str(row.get("thematic_bucket", "")).strip().lower()
        title = str(row.get("title", "")).strip().lower()

        if bucket not in caps:
            continue
        if counts[bucket] >= caps[bucket]:
            continue
        if title in seen_titles:
            continue

        selected.append(row)
        counts[bucket] += 1
        seen_titles.add(title)

        if sum(counts.values()) >= 60:
            break

    top60 = pd.DataFrame(selected)
    by_bucket = (
        df.groupby("thematic_bucket", group_keys=False)
        .head(20)[
            [
                "title",
                "publication_year",
                "journal",
                "citation_count_unified",
                "thematic_bucket",
                "source_file",
                "reading_final_score",
            ]
        ]
    )

    df.to_csv(OUTPUT_CANDIDATES, index=False, encoding="utf-8-sig")
    top60.to_csv(OUTPUT_TOP60, index=False, encoding="utf-8-sig")
    by_bucket.to_csv(OUTPUT_BY_BUCKET, index=False, encoding="utf-8-sig")

    print(f"Arquivo salvo em: {OUTPUT_CANDIDATES}")
    print(f"Arquivo salvo em: {OUTPUT_TOP60}")
    print(f"Arquivo salvo em: {OUTPUT_BY_BUCKET}")
    print(f"Total top60: {len(top60)}")


if __name__ == "__main__":
    main()