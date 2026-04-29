"""
18_brazil_curation_merge.py
============================
Curadoria humana do suplemento Brasil e integração ao corpus principal.

FASE A — gerar planilha de revisão (executa sempre):
  Lê data/brazil_supplement_candidates.csv, compara com corpus congelado
  e grava data/manual/brazil_curation_decisions.csv (apenas se ainda não
  existir, para não sobrescrever decisões já preenchidas).

FASE B — aplicar decisões (só executa se a coluna `decision` tiver entradas):
  Lê as decisões humanas, incorpora os registros aprovados ao corpus e
  grava artefatos rastreáveis:
    - data/interim/07_frozen_corpus_v2.csv
    - logs/prisma_flow_v2.csv
    - outputs/tables/brazil_inclusion_summary.csv

Uso:
    python src/pipelines/18_brazil_curation_merge.py
    python src/pipelines/18_brazil_curation_merge.py --force-review
        (--force-review recria a planilha mesmo se já existir)
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src"))
from utils.normalize import (
    normalize_doi,
    normalize_title,
    normalize_journal,
    extract_year,
    compute_metadata_score,
)

# ── Paths ────────────────────────────────────────────────────────────────────
INTERIM_DIR = BASE_DIR / "data" / "interim"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_TABLES = BASE_DIR / "outputs" / "tables"
MANUAL_DIR = BASE_DIR / "data" / "manual"

CANDIDATES_FILE = BASE_DIR / "data" / "brazil_supplement_candidates.csv"
FROZEN_V1 = INTERIM_DIR / "06_frozen_corpus.csv"
DECISIONS_FILE = MANUAL_DIR / "brazil_curation_decisions.csv"
FROZEN_V2 = INTERIM_DIR / "07_frozen_corpus_v2.csv"
PRISMA_V2 = LOGS_DIR / "prisma_flow_v2.csv"
INCLUSION_SUMMARY = OUTPUT_TABLES / "brazil_inclusion_summary.csv"

NUCLEAR_PATTERNS = [
    r"\bjudicial\s+polic(?:y|ies)\b",
    r"\bpol[ií]tica[s]?\s+judici[aá]ri[ao]s?\b",
    r"\bpol[ií]tica[s]?\s+judicial(?:es)?\b",
]

REVIEW_COLS = [
    "id_local", "doi", "title", "year", "journal",
    "source", "match_status", "suggested_ring", "decision", "reason",
]


def _classify_ring(row: pd.Series) -> str:
    text = " ".join(
        str(row.get(c, "")).lower()
        for c in ["title", "abstract", "criteria_note"]
    )
    for pat in NUCLEAR_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return "nuclear"
    return "extended"


def _dedup_key(row: pd.Series) -> str:
    doi = normalize_doi(row.get("doi", ""))
    if doi:
        return doi
    title = normalize_title(row.get("title", ""))
    year = extract_year(str(row.get("publication_year", "")))
    journal = normalize_journal(row.get("journal", ""))
    return f"{title}::{year}::{journal}"


def load_frozen_keys() -> set[str]:
    if not FROZEN_V1.exists():
        print(f"  AVISO: corpus congelado não encontrado em {FROZEN_V1}")
        return set()
    df = pd.read_csv(FROZEN_V1, dtype=str)
    keys = set()
    for _, row in df.iterrows():
        keys.add(_dedup_key(row))
    return keys


def phase_a(force: bool) -> None:
    """Gera planilha de revisão para curadoria humana."""
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)

    if DECISIONS_FILE.exists() and not force:
        df_existing = pd.read_csv(DECISIONS_FILE, dtype=str)
        filled = df_existing["decision"].apply(
            lambda v: str(v).strip().lower() not in ("", "nan", "none")
        ).sum()
        print(f"Planilha já existe ({len(df_existing)} linhas, {filled} com decisão).")
        print("  Use --force-review para recriá-la (apaga decisões existentes).")
        return

    if not CANDIDATES_FILE.exists():
        print(f"ERRO: candidatos não encontrados em {CANDIDATES_FILE}")
        print("  Execute primeiro: python src/pipelines/16_brazil_supplement_compare.py")
        sys.exit(1)

    candidates = pd.read_csv(CANDIDATES_FILE, dtype=str)
    print(f"Candidatos carregados: {len(candidates)}")

    frozen_keys = load_frozen_keys()
    print(f"Chaves no corpus congelado: {len(frozen_keys)}")

    rows = []
    for i, row in candidates.iterrows():
        key = _dedup_key(row)
        match_status = "already_in" if key in frozen_keys else "new"
        ring = _classify_ring(row)
        rows.append({
            "id_local": i,
            "doi": row.get("doi", ""),
            "title": row.get("title", ""),
            "year": extract_year(str(row.get("publication_year", ""))),
            "journal": row.get("journal", ""),
            "source": row.get("source", ""),
            "match_status": match_status,
            "suggested_ring": ring,
            "decision": "",
            "reason": "",
        })

    df_review = pd.DataFrame(rows, columns=REVIEW_COLS)
    df_review.to_csv(DECISIONS_FILE, index=False, encoding="utf-8-sig")

    n_new = (df_review["match_status"] == "new").sum()
    n_already = (df_review["match_status"] == "already_in").sum()
    n_nuclear_sug = (df_review["suggested_ring"] == "nuclear").sum()

    print(f"\nPlanilha de revisão gerada: {DECISIONS_FILE}")
    print(f"  Total de candidatos:  {len(df_review)}")
    print(f"  Já no corpus (skip):  {n_already}")
    print(f"  Novos (requerem decisão): {n_new}")
    print(f"  Anel nuclear sugerido: {n_nuclear_sug}")
    print()
    print("PRÓXIMO PASSO:")
    print(f"  1. Abra {DECISIONS_FILE}")
    print("  2. Para cada linha com match_status='new', preencha:")
    print("       decision  ->  'include' ou 'exclude'")
    print("       reason    ->  breve justificativa")
    print("  3. Salve o arquivo e execute este script novamente.")


def phase_b() -> None:
    """Aplica decisões humanas e gera corpus v2."""
    if not DECISIONS_FILE.exists():
        print("Planilha de decisões não encontrada. Execute a Fase A primeiro.")
        return

    decisions = pd.read_csv(DECISIONS_FILE, dtype=str)
    decisions["decision"] = decisions["decision"].fillna("").str.strip().str.lower()
    to_include = decisions[decisions["decision"] == "include"].copy()

    if to_include.empty:
        print("Nenhuma decisão 'include' encontrada. Fase B pulada.")
        print("Preencha a coluna 'decision' na planilha e execute novamente.")
        return

    print(f"Decisões 'include': {len(to_include)}")

    # Recarregar candidatos completos pelo id_local
    candidates = pd.read_csv(CANDIDATES_FILE, dtype=str)
    to_include["id_local"] = pd.to_numeric(to_include["id_local"], errors="coerce")
    selected = candidates.loc[candidates.index.isin(to_include["id_local"].dropna().astype(int))]

    if selected.empty:
        print("AVISO: nenhum candidato correspondeu aos id_local aprovados.")
        return

    # Carregar corpus v1
    frozen_v1 = pd.read_csv(FROZEN_V1, dtype=str)
    frozen_keys = set()
    for _, row in frozen_v1.iterrows():
        frozen_keys.add(_dedup_key(row))

    # Preparar registros a adicionar (deduplica contra corpus atual)
    new_records = []
    skipped_dup = 0
    for _, row in selected.iterrows():
        key = _dedup_key(row)
        if key in frozen_keys:
            skipped_dup += 1
            continue
        frozen_keys.add(key)
        # Classificar anel
        dec_row = to_include[
            pd.to_numeric(to_include["id_local"], errors="coerce") == row.name
        ]
        ring = dec_row["suggested_ring"].iloc[0] if len(dec_row) else _classify_ring(row)
        record = row.to_dict()
        record["ring"] = ring
        record["doi_norm"] = normalize_doi(record.get("doi", ""))
        record["title_norm"] = normalize_title(record.get("title", ""))
        record["journal_norm"] = normalize_journal(record.get("journal", ""))
        record["publication_year"] = extract_year(str(record.get("publication_year", "")))
        record["source_brazil_curation"] = "true"
        new_records.append(record)

    print(f"  Duplicatas ignoradas (já no corpus): {skipped_dup}")
    print(f"  Registros a incorporar: {len(new_records)}")

    if not new_records:
        print("Nenhum registro novo após deduplicação. Corpus v2 não gerado.")
        return

    df_new = pd.DataFrame(new_records)

    # Alinhar colunas com o corpus v1
    for col in frozen_v1.columns:
        if col not in df_new.columns:
            df_new[col] = ""
    df_new = df_new[[c for c in frozen_v1.columns if c in df_new.columns] +
                    [c for c in df_new.columns if c not in frozen_v1.columns]]

    frozen_v2 = pd.concat([frozen_v1, df_new], ignore_index=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    frozen_v2.to_csv(FROZEN_V2, index=False, encoding="utf-8-sig")
    print(f"Corpus v2 salvo: {FROZEN_V2} ({len(frozen_v2)} registros)")

    # PRISMA v2
    n_nuclear_new = sum(1 for r in new_records if r.get("ring") == "nuclear")
    n_extended_new = len(new_records) - n_nuclear_new

    # Carregar prisma v1 para base
    prisma_v1_path = LOGS_DIR / "prisma_flow.csv"
    if prisma_v1_path.exists():
        prisma_v1 = pd.read_csv(prisma_v1_path, dtype=str)
        base = {row["etapa"]: row["n"] for _, row in prisma_v1.iterrows()} if "etapa" in prisma_v1.columns else {}
    else:
        base = {}

    now = datetime.now(timezone.utc).isoformat()
    prisma_rows = []

    def _val(key: str, fallback: int = 0) -> int:
        try:
            return int(base.get(key, fallback))
        except (ValueError, TypeError):
            return fallback

    prisma_rows = [
        {"etapa": "identified", "n": _val("identified"), "note": "v1 — todas as bases"},
        {"etapa": "duplicates_removed", "n": _val("duplicates_removed"), "note": "v1"},
        {"etapa": "screened", "n": _val("screened"), "note": "v1"},
        {"etapa": "excluded", "n": _val("excluded"), "note": "v1"},
        {"etapa": "included_total_v1", "n": _val("included_total"), "note": "v1 — antes do suplemento Brasil"},
        {"etapa": "brazil_supplement_added", "n": len(new_records), "note": "Suplemento Brasil — aprovados na curadoria"},
        {"etapa": "brazil_supplement_nuclear", "n": n_nuclear_new, "note": "Suplemento Brasil — anel nuclear"},
        {"etapa": "brazil_supplement_extended", "n": n_extended_new, "note": "Suplemento Brasil — anel estendido"},
        {"etapa": "included_total_v2", "n": _val("included_total") + len(new_records), "note": "v2 — corpus + suplemento Brasil"},
        {"etapa": "included_core_ex_v2",
         "n": _val("included_core_ex") + n_nuclear_new,
         "note": "v2 — anel nuclear total"},
        {"etapa": "included_adj_v2",
         "n": _val("included_adj") + n_extended_new,
         "note": "v2 — anel estendido total"},
        {"etapa": "_timestamp", "n": 0, "note": now},
        {"etapa": "_script", "n": 0, "note": "src/pipelines/18_brazil_curation_merge.py"},
    ]

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(prisma_rows).to_csv(PRISMA_V2, index=False, encoding="utf-8-sig")
    print(f"PRISMA v2 salvo: {PRISMA_V2}")

    # Sumário de inclusão
    summary_rows = []
    for r in new_records:
        dec_row_list = [
            d for _, d in to_include.iterrows()
            if str(d.get("id_local", "")) == str(r.get("id_local_orig", ""))
        ]
        reason = dec_row_list[0].get("reason", "") if dec_row_list else ""
        summary_rows.append({
            "doi": r.get("doi", ""),
            "title": r.get("title", "")[:80],
            "year": r.get("publication_year", ""),
            "ring": r.get("ring", ""),
            "source": r.get("source", ""),
            "reason": reason,
        })

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary_rows).to_csv(INCLUSION_SUMMARY, index=False, encoding="utf-8-sig")
    print(f"Sumário de inclusão: {INCLUSION_SUMMARY}")

    print(f"\n{'='*60}")
    print("BRASIL SUPPLEMENT — RESUMO FASE B")
    print(f"{'='*60}")
    print(f"Aprovados na curadoria:  {len(to_include)}")
    print(f"Incorporados (novos):    {len(new_records)}")
    print(f"  Anel nuclear:          {n_nuclear_new}")
    print(f"  Anel estendido:        {n_extended_new}")
    print(f"Corpus v2 total:         {len(frozen_v2)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Curadoria do suplemento Brasil")
    parser.add_argument(
        "--force-review",
        action="store_true",
        help="Recria a planilha de revisão mesmo se já existir.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("PASSO 18 — Curadoria do suplemento Brasil")
    print("=" * 60)

    phase_a(force=args.force_review)
    phase_b()


if __name__ == "__main__":
    main()
