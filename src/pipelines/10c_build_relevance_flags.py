from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_step10b.csv"
OUTPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_v2.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

ANCHORS = [
    "judicial", "judiciary", "court", "courts", "tribunal", "tribunals",
    "justice", "constitutional court", "supreme court", "judiciária", "judiciário",
]

CORE_CONCEPT_HINTS = [
    "law", "legal", "judicial", "court", "courts", "tribunal", "justice",
    "constitutional", "judiciary",
]

BAD_JOURNAL_HINTS = [
    "lepidopterología",
    "entomology",
    "zoology",
]

def norm(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()

df["title_clean"] = df["title_clean"].apply(norm) if "title_clean" in df.columns else ""
df["journal_clean"] = df["journal_clean"].apply(norm) if "journal_clean" in df.columns else ""
df["concepts_norm"] = df["concepts"].apply(norm) if "concepts" in df.columns else ""

def classify_relevance(row):
    title = row.get("title_clean", "")
    journal = row.get("journal_clean", "")
    concepts = row.get("concepts_norm", "")

    title_journal = f"{title} {journal}".strip()

    has_anchor_title = any(a in title_journal for a in ANCHORS)
    has_anchor_concept = any(c in concepts for c in CORE_CONCEPT_HINTS)
    has_bad_journal = any(b in journal for b in BAD_JOURNAL_HINTS)

    if has_bad_journal:
        return 0, "bad_journal_hint"
    if has_anchor_title:
        return 1, "anchor_title_journal"
    if has_anchor_concept:
        return 1, "anchor_concept"
    return 0, "no_anchor"

flags = df.apply(classify_relevance, axis=1)
df["relevance_flag"] = [x[0] for x in flags]
df["relevance_reason"] = [x[1] for x in flags]

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print("\nRelevance flag:")
print(df["relevance_flag"].value_counts().to_string())
print("\nRelevance reason:")
print(df["relevance_reason"].value_counts().to_string())
