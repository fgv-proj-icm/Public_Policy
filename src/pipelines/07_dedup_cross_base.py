"""
07_dedup_cross_base.py
======================
PRISMA — Etapa "Duplicates removed"

Remove duplicatas entre bases, preservando o registro com mais metadados.
Registra quantas bases indexaram cada artigo (cobertura cruzada).

Entrada : data/interim/01_merged_all_sources.csv
Saída   : data/interim/02_deduplicated.csv

Uso:
    python src/pipelines/07_dedup_cross_base.py
"""

from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = INTERIM_DIR / "01_merged_all_sources.csv"
OUTPUT_FILE = INTERIM_DIR / "02_deduplicated.csv"
OUTPUT_IMPACT = LOGS_DIR / "dedup_impact.csv"


def compute_metadata_score(row) -> int:
    """Pontua completude de metadados para decidir qual registro manter."""
    score = 0
    if row.get("doi_norm", "") not in ("", "nan"):
        score += 3
    if row.get("abstract", "") not in ("", "nan"):
        score += 2
    if row.get("authors", "") not in ("", "nan"):
        score += 1
    if row.get("journal_norm", "") not in ("", "nan"):
        score += 1
    if row.get("language", "") not in ("", "nan"):
        score += 1
    return score


def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)
    df["doi_norm"] = df["doi_norm"].fillna("").astype(str).str.strip()
    df["title_norm"] = df["title_norm"].fillna("").astype(str).str.strip()
    df["journal_norm"] = df["journal_norm"].fillna("").astype(str).str.strip()

    total_antes = len(df)
    print(f"Registros de entrada: {total_antes:,}")

    # ── Passo 1: mapear cobertura cruzada ──────────────────────────────────
    # Para cada registro, anotar em quantas bases ele aparece
    # Agrupar por DOI (quando disponível)
    doi_sources = (
        df[df["doi_norm"] != ""]
        .groupby("doi_norm")["source"]
        .apply(lambda x: "; ".join(sorted(set(x))))
        .reset_index()
        .rename(columns={"source": "indexed_in"})
    )

    doi_source_count = (
        df[df["doi_norm"] != ""]
        .groupby("doi_norm")["source"]
        .apply(lambda x: len(set(x)))
        .reset_index()
        .rename(columns={"source": "n_bases"})
    )

    # ── Passo 2: pontuar e ordenar ─────────────────────────────────────────
    df["meta_score"] = df.apply(compute_metadata_score, axis=1)
    df = df.sort_values(
        ["cited_by_count", "meta_score"], ascending=[False, False]
    )

    # ── Passo 3: deduplicar por DOI ────────────────────────────────────────
    df_with_doi = df[df["doi_norm"] != ""].copy()
    df_without_doi = df[df["doi_norm"] == ""].copy()

    dedup_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")

    # Anotar cobertura cruzada nos registros mantidos
    dedup_doi = dedup_doi.merge(doi_sources, on="doi_norm", how="left")
    dedup_doi = dedup_doi.merge(doi_source_count, on="doi_norm", how="left")

    removed_by_doi = len(df_with_doi) - len(dedup_doi)

    # ── Passo 4: deduplicar sem DOI por título+ano+periódico ───────────────
    dedup_no_doi = df_without_doi.drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"],
        keep="first",
    )
    dedup_no_doi["indexed_in"] = dedup_no_doi["source"]
    dedup_no_doi["n_bases"] = 1

    removed_by_title = len(df_without_doi) - len(dedup_no_doi)

    # ── Passo 5: consolidar ────────────────────────────────────────────────
    df_final = pd.concat([dedup_doi, dedup_no_doi], ignore_index=True)
    df_final = df_final.sort_values("cited_by_count", ascending=False)

    total_duplicatas = removed_by_doi + removed_by_title
    total_apos = len(df_final)

    df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    now = datetime.now(timezone.utc).isoformat()
    impact = pd.DataFrame([
        {
            "passo": "entrada",
            "regra": "registros identificados multibase",
            "linhas_removidas": 0,
            "linhas_restantes": total_antes,
            "motivo": "base antes da deduplicacao",
            "timestamp": now,
            "script": "src/pipelines/07_dedup_cross_base.py",
        },
        {
            "passo": "deduplicacao_doi",
            "regra": "doi_norm",
            "linhas_removidas": removed_by_doi,
            "linhas_restantes": len(dedup_doi) + len(df_without_doi),
            "motivo": "mesmo DOI normalizado em uma ou mais bases",
            "timestamp": now,
            "script": "src/pipelines/07_dedup_cross_base.py",
        },
        {
            "passo": "deduplicacao_sem_doi",
            "regra": "title_norm + publication_year + journal_norm",
            "linhas_removidas": removed_by_title,
            "linhas_restantes": total_apos,
            "motivo": "fallback para registros sem DOI",
            "timestamp": now,
            "script": "src/pipelines/07_dedup_cross_base.py",
        },
    ])
    impact.to_csv(OUTPUT_IMPACT, index=False, encoding="utf-8-sig")

    # ── Relatório ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRISMA — DUPLICATES REMOVED")
    print(f"{'='*60}")
    print(f"Total identificado (N bruto):      {total_antes:>7,}")
    print(f"Duplicatas removidas por DOI:       {removed_by_doi:>7,}")
    print(f"Duplicatas removidas por título:    {removed_by_title:>7,}")
    print(f"Total duplicatas removidas:         {total_duplicatas:>7,}")
    print(f"Total após deduplicação:            {total_apos:>7,}")
    print(f"Relatório de impacto:               {OUTPUT_IMPACT}")
    print(f"\nCobertura cruzada (registros com DOI):")
    if "n_bases" in df_final.columns:
        print(df_final["n_bases"].value_counts().sort_index().to_string())
    print(f"\nSalvo em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
