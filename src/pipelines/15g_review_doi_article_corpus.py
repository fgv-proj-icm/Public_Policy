from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

CORPUS_FILE = FINAL_DIR / "bibliometric_corpus_final_v3_articles_doi_reviews_no_doi.csv"
TOP50_FILE = FINAL_DIR / "reading_list_final_articles_doi_reviews_no_doi_top50.csv"
REPORT_FILE = FINAL_DIR / "articles_doi_reviews_no_doi_report.json"

df = pd.read_csv(CORPUS_FILE, low_memory=False)
top50 = pd.read_csv(TOP50_FILE, low_memory=False)

with open(REPORT_FILE, "r", encoding="utf-8") as f:
    report = json.load(f)

print("\n=== RELATÓRIO GERAL ===")
print(report)

print("\n=== CORPUS FINAL ===")
print(f"Linhas: {len(df)}")
print(f"Colunas: {len(df.columns)}")

print("\n=== DISTRIBUIÇÃO POR TIPO ===")
if "primary_type" in df.columns:
    print(df["primary_type"].value_counts().to_string())

print("\n=== DISTRIBUIÇÃO POR BUCKET ===")
if "thematic_bucket" in df.columns:
    print(df["thematic_bucket"].value_counts().to_string())

print("\n=== DISTRIBUIÇÃO POR FONTE ===")
if "source_file" in df.columns:
    print(df["source_file"].value_counts().to_string())

print("\n=== CHECK DOI ===")
if "doi_clean" in df.columns:
    print("Artigos com DOI:")
    print(
        df[df["primary_type"] == "article"]["doi_clean"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )
    print("Reviews sem DOI:")
    print(
        df[df["primary_type"] == "review"]["doi_clean"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

print("\n=== TOP 20 PERIÓDICOS ===")
if "journal" in df.columns:
    print(df["journal"].fillna("N/D").value_counts().head(20).to_string())

print("\n=== TOP50 PARA LEITURA/LOCALIZAÇÃO ===")
print(f"Linhas: {len(top50)}")
print(top50.head(30).to_string(index=False))
