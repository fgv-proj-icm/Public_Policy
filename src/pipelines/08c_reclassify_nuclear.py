"""
08c_reclassify_nuclear.py
=========================
Reclassificação do anel nuclear — Caminho B.

Restringe o anel nuclear à acepção PROGRAMÁTICA de "política judiciária":
  - governança institucional do sistema de justiça
  - políticas nacionais (CNJ, conselhos, cortes superiores)
  - gestão judicial, administração da justiça
  - resolução de conflitos como política institucional

Move para o anel ESTENDIDO:
  - "judicial policy-making" (juízes criando direito via decisão)
  - "criminal judicial policy" (política de sentenciamento penal)
  - usos genéricos ou inclassificáveis

Entrada : data/interim/04_cleaned.csv
Saída   : data/interim/05_reclassified.csv
          data/interim/05_reclassification_log.csv  (registro de cada decisão)

Uso:
    python src/pipelines/08c_reclassify_nuclear.py
"""

from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src"))
from utils.acepcoes import (
    PROGRAMMATIC_PATTERNS as PROGRAMMATIC_SIGNALS,
    BEHAVIORAL_PATTERNS as POLICYMAKING_PATTERNS,
    PENAL_PATTERNS as CRIMINAL_PATTERNS,
    _match_any,
    _first_match,
)

INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_FILE = INTERIM_DIR / "04_cleaned.csv"
OUTPUT_FILE = INTERIM_DIR / "05_reclassified.csv"
OUTPUT_LOG = INTERIM_DIR / "05_reclassification_log.csv"

# Os padrões vivem em src/utils/acepcoes.py, compartilhados com
# 10b_classify_acepcoes.py. Os apelidos acima preservam os nomes originais e a
# decisão de anel permanece idêntica à que produziu o corpus congelado.


def reclassify_nuclear(row) -> tuple[str, str, str]:
    """
    Retorna (new_ring, reclassification_reason, matched_pattern).
    new_ring = 'nuclear' | 'extended'
    """
    title = str(row.get("title", "")).lower() if pd.notna(row.get("title")) else ""
    abstract = str(row.get("abstract", "")).lower() if pd.notna(row.get("abstract")) else ""
    journal = str(row.get("journal", "")).lower() if pd.notna(row.get("journal")) else ""
    search_text = f"{title} {abstract} {journal}"

    # Se tem sinal programático claro, mantém nuclear
    if _match_any(search_text, PROGRAMMATIC_SIGNALS):
        match = _first_match(search_text, PROGRAMMATIC_SIGNALS)
        return "nuclear", "programático_confirmado", match

    # Se é judicial policy-making, move para estendido
    if _match_any(search_text, POLICYMAKING_PATTERNS):
        match = _first_match(search_text, POLICYMAKING_PATTERNS)
        return "extended", "reclassificado_policymaking", match

    # Se é criminal judicial policy, move para estendido
    if _match_any(search_text, CRIMINAL_PATTERNS):
        match = _first_match(search_text, CRIMINAL_PATTERNS)
        return "extended", "reclassificado_criminal", match

    # Sem sinal claro — mantém nuclear mas sinaliza para revisão
    return "nuclear", "sem_sinal_claro_manter", ""


def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)

    total = len(df)
    nuclear_before = len(df[df["ring"] == "nuclear"])
    extended_before = len(df[df["ring"] == "extended"])

    print(f"Entrada: {total:,} registros")
    print(f"  Nuclear antes:   {nuclear_before:,}")
    print(f"  Estendido antes: {extended_before:,}")

    # ── Aplicar reclassificação apenas ao anel nuclear ──────────────────
    nuclear_mask = df["ring"] == "nuclear"
    nuclear_df = df[nuclear_mask].copy()
    extended_df = df[~nuclear_mask].copy()

    results = nuclear_df.apply(reclassify_nuclear, axis=1, result_type="expand")
    nuclear_df["ring"] = results[0]
    nuclear_df["reclassification_reason"] = results[1]
    nuclear_df["matched_pattern"] = results[2]

    # Log de reclassificação
    log_df = nuclear_df[["title", "ring", "reclassification_reason", "matched_pattern", "journal", "publication_year"]].copy()
    log_df.to_csv(OUTPUT_LOG, index=False, encoding="utf-8-sig")

    # Reconsolidar
    extended_df["reclassification_reason"] = ""
    extended_df["matched_pattern"] = ""
    df_final = pd.concat([nuclear_df, extended_df], ignore_index=True)
    df_final = df_final.sort_values("cited_by_count", ascending=False)

    nuclear_after = len(df_final[df_final["ring"] == "nuclear"])
    extended_after = len(df_final[df_final["ring"] == "extended"])
    moved_to_extended = nuclear_before - nuclear_after

    df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    # ── Relatório ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("RECLASSIFICAÇÃO DO ANEL NUCLEAR — CAMINHO B")
    print(f"{'='*60}")
    print(f"Nuclear antes:              {nuclear_before:>7,}")
    print(f"Movidos para estendido:     {moved_to_extended:>7,}")
    print(f"Nuclear após:               {nuclear_after:>7,}")
    print(f"Estendido após:             {extended_after:>7,}")

    # Breakdown
    reason_counts = nuclear_df["reclassification_reason"].value_counts()
    print(f"\nBreakdown da reclassificação:")
    for reason, cnt in reason_counts.items():
        print(f"  {reason:40s}: {cnt:>5,}")

    # Mostrar o que foi movido
    moved = nuclear_df[nuclear_df["ring"] == "extended"]
    if len(moved) > 0:
        print(f"\nArtigos movidos para estendido ({len(moved)}):")
        for _, row in moved.iterrows():
            title = str(row["title"])[:80]
            reason = row["reclassification_reason"]
            print(f"  [{reason}] {title}")

    # Mostrar nucleares sem sinal claro (para revisão manual)
    unclear = nuclear_df[nuclear_df["reclassification_reason"] == "sem_sinal_claro_manter"]
    if len(unclear) > 0:
        print(f"\nNucleares sem sinal claro — REVISAR MANUALMENTE ({len(unclear)}):")
        for _, row in unclear.iterrows():
            title = str(row["title"])[:80]
            journal = str(row.get("journal", ""))[:30]
            print(f"  {title}  [{journal}]")

    print(f"\nArquivos salvos:")
    print(f"  Corpus:  {OUTPUT_FILE}")
    print(f"  Log:     {OUTPUT_LOG}")


if __name__ == "__main__":
    main()
