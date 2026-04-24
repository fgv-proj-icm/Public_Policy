from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

FILES = [
    ("base_mestre_v3", FINAL_DIR / "unified_base_analysis_ready_v3.csv"),
    ("focus_corpus", FINAL_DIR / "focus_corpus_policy_admin.csv"),
    ("strict_corpus", FINAL_DIR / "focus_corpus_strict.csv"),
    ("biblio_v2", FINAL_DIR / "bibliometric_corpus_final_v2.csv"),
    ("biblio_v3", FINAL_DIR / "bibliometric_corpus_final_v3.csv"),
    ("biblio_core_v1", FINAL_DIR / "bibliometric_corpus_core_v1.csv"),
]

REVIEW_FILE = FINAL_DIR / "bibliometric_corpus_review_queue.csv"
EXCLUDED_FILE = FINAL_DIR / "bibliometric_corpus_excluded.csv"

OUTPUT_FUNNEL = FINAL_DIR / "funnel_impact_table.csv"
OUTPUT_CLEANING = FINAL_DIR / "cleaning_impact_table.csv"


def safe_count(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return len(pd.read_csv(path, low_memory=False))
    except Exception:
        return None


def main() -> None:
    rows = []
    previous_count = None

    for step_name, path in FILES:
        count = safe_count(path)
        removed = None
        retained_pct = None

        if previous_count is not None and count is not None:
            removed = previous_count - count
            retained_pct = (count / previous_count) * 100 if previous_count > 0 else None

        rows.append(
            {
                "step_name": step_name,
                "file_name": path.name,
                "n_records": count,
                "removed_from_previous": removed,
                "retained_pct_from_previous": retained_pct,
            }
        )
        if count is not None:
            previous_count = count

    funnel_df = pd.DataFrame(rows)

    review_count = safe_count(REVIEW_FILE)
    excluded_count = safe_count(EXCLUDED_FILE)

    cleaning_df = pd.DataFrame(
        [
            {
                "operation": "curadoria_claude_manter",
                "file_name": "bibliometric_corpus_final_v3.csv",
                "n_records": safe_count(FILES[4][1]),
            },
            {
                "operation": "curadoria_claude_revisar",
                "file_name": REVIEW_FILE.name,
                "n_records": review_count,
            },
            {
                "operation": "curadoria_claude_excluir",
                "file_name": EXCLUDED_FILE.name,
                "n_records": excluded_count,
            },
        ]
    )

    funnel_df.to_csv(OUTPUT_FUNNEL, index=False, encoding="utf-8-sig")
    cleaning_df.to_csv(OUTPUT_CLEANING, index=False, encoding="utf-8-sig")

    print(f"Arquivo salvo em: {OUTPUT_FUNNEL}")
    print(f"Arquivo salvo em: {OUTPUT_CLEANING}")


if __name__ == "__main__":
    main()
