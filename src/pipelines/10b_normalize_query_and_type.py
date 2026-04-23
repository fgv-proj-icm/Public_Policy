from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_step10a.csv"
OUTPUT_FILE = FINAL_DIR / "unified_base_analysis_ready_step10b.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

def clean_query_term(value: str) -> str:
    if pd.isna(value):
        return "nd"
    text = str(value).strip().lower()

    quoted = re.findall(r'"([^"]+)"', text)
    if quoted:
        text = quoted[0].strip()
    text = text.replace("title-abs-key(", "").replace(")", "").strip()

    mapping = {
        "judicial policy": "judicial policy",
        "judicial policies": "judicial policies",
        "judicial governance": "judicial governance",
        "judicial administration": "judicial administration",
        "court administration": "court administration",
        "court governance": "court governance",
        "judicial reform": "judicial reform",
        "judicial review": "judicial review",
        "access to justice": "access to justice",
        "política judiciária": "política judiciária",
        "políticas judiciárias": "políticas judiciárias",
        "governança judicial": "governança judicial",
        "administração judiciária": "administração judiciária",
        "reforma do judiciário": "reforma do judiciário",
        "reforma judicial": "reforma judicial",
        "conselho nacional de justiça": "conselho nacional de justiça",
    }

    return mapping.get(text, text)

def build_primary_type(value: str) -> str:
    if pd.isna(value):
        return "nd"

    text = str(value).strip().lower()
    parts = [p.strip() for p in text.split(";") if p.strip()]

    if any("review" in p for p in parts):
        return "review"
    if any(p in ("article", "journalarticle", "journal-article") or "article" in p for p in parts):
        return "article"
    if any("book_chapter" in p or "book chapter" in p or p == "chapter" for p in parts):
        return "book_chapter"
    if any("conference" in p for p in parts):
        return "conference"
    if any("editorial" in p for p in parts):
        return "editorial"
    if any("book" == p for p in parts):
        return "book"
    if any("note" in p for p in parts):
        return "note"
    if any("erratum" in p for p in parts):
        return "erratum"

    return text if text else "nd"

df["query_term_clean"] = df["query_term"].apply(clean_query_term) if "query_term" in df.columns else "nd"
df["primary_type"] = df["type_clean"].apply(build_primary_type) if "type_clean" in df.columns else "nd"

df["is_article"] = df["primary_type"] == "article"
df["is_review"] = df["primary_type"] == "review"
df["is_book_chapter"] = df["primary_type"] == "book_chapter"
df["is_conference"] = df["primary_type"] == "conference"

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(df['query_term_clean'].value_counts().head(15).to_string())
print(df['primary_type'].value_counts().head(15).to_string())
