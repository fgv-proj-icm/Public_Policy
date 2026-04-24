from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
BIB_DIR = FINAL_DIR / "bibliometrics_full_core"

FULL_OVERVIEW = BIB_DIR / "full" / "overview.json"
CORE_OVERVIEW = BIB_DIR / "core" / "overview.json"

FUNNEL_FILE = FINAL_DIR / "funnel_impact_table.csv"
CLEANING_FILE = FINAL_DIR / "cleaning_impact_table.csv"
READING_TOP60_FILE = FINAL_DIR / "reading_list_final_top60.csv"
READING_BY_BUCKET_FILE = FINAL_DIR / "reading_list_final_top20_by_bucket.csv"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    full_overview = load_json(FULL_OVERVIEW)
    core_overview = load_json(CORE_OVERVIEW)

    funnel_df = pd.read_csv(FUNNEL_FILE, low_memory=False)
    cleaning_df = pd.read_csv(CLEANING_FILE, low_memory=False)
    reading_top60 = pd.read_csv(READING_TOP60_FILE, low_memory=False)
    reading_by_bucket = pd.read_csv(READING_BY_BUCKET_FILE, low_memory=False)

    print("\n=== OVERVIEW FULL ===")
    print(full_overview)

    print("\n=== OVERVIEW CORE ===")
    print(core_overview)

    print("\n=== FUNIL DO CORPUS ===")
    print(funnel_df.to_string(index=False))

    print("\n=== IMPACTO DA LIMPEZA ===")
    print(cleaning_df.to_string(index=False))

    print("\n=== LEITURA FINAL TOP60 ===")
    print(f"Linhas: {len(reading_top60)}")

    print("\n=== DISTRIBUIÇÃO POR BUCKET | TOP60 ===")
    if "thematic_bucket" in reading_top60.columns:
        print(reading_top60["thematic_bucket"].value_counts().to_string())

    print("\n=== DISTRIBUIÇÃO POR FONTE | TOP60 ===")
    if "source_file" in reading_top60.columns:
        print(reading_top60["source_file"].value_counts().to_string())

    print("\n=== TOP 30 DA LEITURA FINAL ===")
    cols = [
        "title",
        "publication_year",
        "journal",
        "citation_count_unified",
        "thematic_bucket",
        "source_file",
        "reading_final_score",
    ]
    cols = [c for c in cols if c in reading_top60.columns]
    print(reading_top60[cols].head(30).to_string(index=False))

    print("\n=== TOP 10 POR BUCKET ===")
    for bucket, sub in reading_by_bucket.groupby("thematic_bucket"):
        print(f"\n--- {bucket} ---")
        print(sub.head(10).to_string(index=False))


if __name__ == "__main__":
    main()