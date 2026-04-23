from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

INPUT_FILE = FINAL_DIR / "focus_corpus_policy_admin.csv"
OUTPUT_FILE = FINAL_DIR / "focus_corpus_policy_clustered.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

for col in ["title_clean", "journal_clean", "query_term_clean"]:
    if col not in df.columns:
        df[col] = ""

df["title_clean"] = df["title_clean"].fillna("").astype(str).str.strip().str.lower()
df["journal_clean"] = df["journal_clean"].fillna("").astype(str).str.strip().str.lower()
df["query_term_clean"] = df["query_term_clean"].fillna("nd").astype(str).str.strip().str.lower()

def classify_cluster(row) -> str:
    text = " ".join([row["title_clean"], row["journal_clean"], row["query_term_clean"]])

    if any(x in text for x in [
        "conselho nacional de justiça", "cnj", "política judiciária",
        "políticas judiciárias", "governança judicial", "administração judiciária"
    ]):
        return "cnj_brazil"

    if any(x in text for x in [
        "judicial administration", "court administration", "court management",
        "judicial management", "case management", "judicial performance",
        "court performance", "judicial efficiency", "court efficiency",
        "e-justice", "digital justice"
    ]):
        return "policy_admin_governance"

    if any(x in text for x in [
        "judicial governance", "court governance", "judicial policy",
        "judicial policies", "policy"
    ]):
        return "policy_admin_governance"

    if any(x in text for x in [
        "judicial reform", "reforma judicial", "reforma do judiciário"
    ]):
        return "reform"

    if any(x in text for x in [
        "judicial review", "constitutional court", "supreme court",
        "constitutional law", "checks and balances"
    ]):
        return "judicial_review_constitutional"

    if any(x in text for x in [
        "access to justice", "legal aid", "dispute resolution", "adr", "mediation"
    ]):
        return "access_to_justice"

    return "other_focus"

df["focus_cluster"] = df.apply(classify_cluster, axis=1)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo em: {OUTPUT_FILE}")
print(df["focus_cluster"].value_counts().to_string())
