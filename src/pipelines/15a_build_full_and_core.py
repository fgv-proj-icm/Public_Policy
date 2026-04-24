from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "bibliometric_corpus_final_v3.csv"

OUTPUT_FULL = FINAL_DIR / "bibliometric_corpus_full_v1.csv"
OUTPUT_CORE = FINAL_DIR / "bibliometric_corpus_core_v1.csv"
OUTPUT_REPORT = FINAL_DIR / "full_core_report.json"


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
        "primary_type",
        "thematic_bucket",
        "claude_curated_relevance_level",
        "source_file",
        "journal",
    ]:
        if col not in df.columns:
            df[col] = ""

    for col in [
        "has_journal",
        "claude_possible_duplicate_flag",
    ]:
        if col not in df.columns:
            df[col] = False

    df["primary_type"] = df["primary_type"].fillna("nd").astype(str).str.strip().str.lower()
    df["thematic_bucket"] = df["thematic_bucket"].fillna("nd").astype(str).str.strip().str.lower()
    df["claude_curated_relevance_level"] = (
        df["claude_curated_relevance_level"].fillna("").astype(str).str.strip().str.lower()
    )
    df["source_file"] = df["source_file"].fillna("nd").astype(str).str.strip()

    df["has_journal"] = to_bool(df["has_journal"])

    if df["claude_possible_duplicate_flag"].dtype != bool:
        df["claude_possible_duplicate_flag"] = (
            df["claude_possible_duplicate_flag"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["1", "true", "yes", "sim"])
        )

    # FULL congelado
    full_df = df.copy()

    # CORE mais estrito
    allowed_buckets = {"policy_admin_governance", "reform", "cnj_brazil"}
    allowed_relevance = {"central"}

    core_df = df[
        (df["primary_type"].isin(["article", "review"]))
        & (df["thematic_bucket"].isin(allowed_buckets))
        & (df["claude_curated_relevance_level"].isin(allowed_relevance))
        & (~df["claude_possible_duplicate_flag"])
        & (df["has_journal"])
    ].copy()

    full_df.to_csv(OUTPUT_FULL, index=False, encoding="utf-8-sig")
    core_df.to_csv(OUTPUT_CORE, index=False, encoding="utf-8-sig")

    report = {
        "input_rows": int(len(df)),
        "full_rows": int(len(full_df)),
        "core_rows": int(len(core_df)),
        "allowed_buckets": sorted(list(allowed_buckets)),
        "allowed_relevance": sorted(list(allowed_relevance)),
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {OUTPUT_FULL}")
    print(f"Arquivo salvo em: {OUTPUT_CORE}")
    print(f"Relatório salvo em: {OUTPUT_REPORT}")
    print(f"Total FULL: {len(full_df)}")
    print(f"Total CORE: {len(core_df)}")


if __name__ == "__main__":
    main()