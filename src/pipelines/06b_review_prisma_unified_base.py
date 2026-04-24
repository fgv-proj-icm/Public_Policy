from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"

IDENTIFIED_FILE = FINAL_DIR / "prisma_identified_dedup.csv"
CORE_FILE = FINAL_DIR / "prisma_core_ex.csv"
ADJ_FILE = FINAL_DIR / "prisma_adjacent.csv"
EXCLUDED_FILE = FINAL_DIR / "prisma_excluded.csv"
LOG_FILE = FINAL_DIR / "prisma_screening_log.csv"
REPORT_FILE = FINAL_DIR / "prisma_report.json"

identified_df = pd.read_csv(IDENTIFIED_FILE, low_memory=False)
core_df = pd.read_csv(CORE_FILE, low_memory=False)
adj_df = pd.read_csv(ADJ_FILE, low_memory=False)
excluded_df = pd.read_csv(EXCLUDED_FILE, low_memory=False)
log_df = pd.read_csv(LOG_FILE, low_memory=False)

with open(REPORT_FILE, "r", encoding="utf-8") as f:
    report = json.load(f)

print("\n=== RELATÓRIO PRISMA ===")
print(report["prisma_counts"])

print("\n=== CORE_EX ===")
print(f"Linhas: {len(core_df)}")

print("\n=== ADJ ===")
print(f"Linhas: {len(adj_df)}")

print("\n=== EXCLUÍDOS ===")
print(f"Linhas: {len(excluded_df)}")

print("\n=== DISTRIBUIÇÃO POR FONTE | CORE_EX ===")
if "source_file" in core_df.columns:
    print(core_df["source_file"].value_counts().to_string())

print("\n=== DISTRIBUIÇÃO POR TIPO | CORE_EX ===")
if "doc_type_group" in core_df.columns:
    print(core_df["doc_type_group"].value_counts().to_string())

print("\n=== RAZÕES DE INCLUSÃO | CORE_EX ===")
if "prisma_reason" in core_df.columns:
    print(core_df["prisma_reason"].value_counts().to_string())

print("\n=== RAZÕES DE INCLUSÃO | ADJ ===")
if "prisma_reason" in adj_df.columns:
    print(adj_df["prisma_reason"].value_counts().head(20).to_string())

print("\n=== RAZÕES DE EXCLUSÃO ===")
if "prisma_reason" in excluded_df.columns:
    print(excluded_df["prisma_reason"].value_counts().head(20).to_string())

print("\n=== TOP 30 CORE_EX POR CITAÇÕES ===")
cols = [
    "title",
    "publication_year",
    "journal",
    "doc_type_group",
    "doi_clean",
    "citation_count_unified",
    "query_term",
    "source_file",
    "prisma_reason",
    "core_strong_hits",
    "core_weak_hits",
    "support_core_hits",
]
cols = [c for c in cols if c in core_df.columns]
print(
    core_df.sort_values(["citation_count_unified", "publication_year"], ascending=[False, False])[cols]
    .head(30)
    .to_string(index=False)
)

print("\n=== TOP 30 ADJ POR CITAÇÕES ===")
cols_adj = [
    "title",
    "publication_year",
    "journal",
    "doc_type_group",
    "doi_clean",
    "citation_count_unified",
    "query_term",
    "source_file",
    "prisma_reason",
    "adjacent_any_hits",
]
cols_adj = [c for c in cols_adj if c in adj_df.columns]
print(
    adj_df.sort_values(["citation_count_unified", "publication_year"], ascending=[False, False])[cols_adj]
    .head(30)
    .to_string(index=False)
)