"""
08d_final_nuclear_adjustment.py
===============================
Ajuste final do anel nuclear antes do congelamento.

Decisões aplicadas:
  1. Tradição russa/pós-soviética ("judicial policy" como doutrina jurídica) → estendido
  2. Artigos históricos (política imperial/estatal pré-moderna) → estendido
  3. Programáticos brasileiros que escaparam do 08c → confirmados como nuclear

Entrada : data/interim/05_reclassified.csv
Saída   : data/interim/06_frozen_corpus.csv
          data/interim/06_adjustment_log.csv

Uso:
    python src/pipelines/08d_final_nuclear_adjustment.py
"""

from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_FILE = INTERIM_DIR / "05_reclassified.csv"
OUTPUT_FILE = INTERIM_DIR / "06_frozen_corpus.csv"
OUTPUT_LOG = INTERIM_DIR / "06_adjustment_log.csv"

# ── PADRÕES: tradição russa/pós-soviética ──────────────────────────────────
# "Judicial policy" como doutrina jurídica geral, teoria do direito judicial
RUSSIAN_POSTSOVIET = [
    r"\bkemerovo\b",
    r"\blex\s+russica\b",
    r"\brussian\s+justice\b",
    r"\brussian\s+civil\s+society\b",
    r"\bgosudarstvo\s+i\s+pravo\b",
    r"\bvestnik\b.*\b(?:osset|state)\b",
    r"\bencyclopedia\s+of\s+law\b",
    r"\buzhhorod\b",
    r"\bpravnik\b",
    r"\bvolga\s+region\b",
    r"\buniversity\s+proceedings\s+volga\b",
    r"\blaw\s+and\s+safety\b",
    r"\bprinciples\s+of\s+judicial\s+policy\s+in\s+the\s+system\b",
    r"\blegal\s+goal[\s-]?setting\s+and\s+the\s+function\s+of\s+judicial\b",
    r"\blegal\s+acts\s+as\s+means\s+of\s+judicial\s+policy\b",
    r"\btechniques\s+of\s+judicial\s+policy\b",
    r"\bevolution\s+of\s+views\s+on\s+judicial\s+policy\b",
    r"\bmediation\s+innovations?\s+in\s+the\s+context\b",
    r"\bdirections\s+for\s+improving\s+state\s+judicial\s+policy\b",
    r"\bjudicial\s+policy\s+of\s+russia\s+and\s+kazakhstan\b",
    r"\bjudicial\s+policy\s+in\s+the\s+russian\b",
    r"\bconsolidation\s+of\s+the\s+judicial\s+system\b",
]

# ── PADRÕES: artigos históricos ────────────────────────────────────────────
HISTORICAL = [
    r"\bimperial\s+judicial\s+policy\b",
    r"\breligious\s+factor\s+in\s+the\s+imperial\b",
    r"\btemporary\s+government\b",
    r"\bgreat\s+patriotic\s+war\b",
    r"\bstavropol\s+territory\b",
    r"\bright[\s-]?bank\s+ukraine\b",
    r"\b19th\s*[–-]\s*(?:early\s+)?20th\s+centur\b",
    r"\bsecond\s+half\s+of\s+the\s+19th\b",
    r"\bjapanese\s+american\s+resistance\s+to\s+world\s+war\b",
    r"\bhistory\s+of\s+british\s+india\b",
]

# ── PADRÕES: programáticos que devem ser CONFIRMADOS ───────────────────────
# Títulos em PT que contêm "política judiciária" sem "nacional"
PROGRAMMATIC_CONFIRM = [
    r"\bpolítica\s+judiciária\b",
    r"\bpolíticas\s+judiciárias\b",
    r"\bpolítica\s+judiciária\s+brasileira\b",
    r"\bjustiça\s+restaurativa\b.*\bpolítica\b",
    r"\btratamento\s+(?:adequado|dos)\s+(?:de\s+)?conflitos\b",
    r"\bcejusc\b",
    r"\btribunal\s+multiportas\b",
    r"\bresolução\s+cnj\b",
    r"\bcnj\b",
    r"\brazoável\s+duração\s+do\s+processo\b",
    r"\bdigital\s+justice\b.*\bjudicial\b",
    r"\baccess\s+to\s+digital\s+justice\b",
    r"\bjudicial\s+policy\s+implementation\b",
    r"\bjudicial\s+policy\s+in\s+(?:england|mexico|canada)\b",
    r"\bjudicial\s+polic(?:y|ies)\s+(?:and|of)\s+(?:procedures?|lines?)\b",
    r"\bjudicial\s+policy\b.*\b(?:regulatory\s+space|new\s+labour)\b",
    r"\bjudicial\s+policy\b.*\b(?:specialised?\s+(?:state\s+)?courts?)\b",
    r"\bai\s+and\s+judicial\s+policy\b",
    r"\bneighborhood\s+justice\b",
    r"\bcollective\s+disputes?\b.*\bjudicial\s+policy\b",
    r"\bconsumer\s+rights?\b.*\bjudicial\s+policy\b",
    r"\bjudicial\s+policy\b.*\bintellectual\s+property\b",
    r"\bjudicial\s+policy\b.*\benvironmental\b",
    r"\bjudicial\s+policy\b.*\bclimate\b",
]


def _match_any(text: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _first_match(text: str, patterns: list[str]) -> str:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


def adjust_nuclear(row) -> tuple[str, str, str]:
    """
    Retorna (new_ring, adjustment_reason, matched).
    Só opera sobre registros que estão no nuclear com reclassification_reason
    == 'sem_sinal_claro_manter'.
    """
    title = str(row.get("title", "")).lower() if pd.notna(row.get("title")) else ""
    journal = str(row.get("journal", "")).lower() if pd.notna(row.get("journal")) else ""
    abstract = str(row.get("abstract", "")).lower() if pd.notna(row.get("abstract")) else ""
    search_text = f"{title} {abstract} {journal}"

    # 1. Confirmar programáticos
    if _match_any(search_text, PROGRAMMATIC_CONFIRM):
        match = _first_match(search_text, PROGRAMMATIC_CONFIRM)
        return "nuclear", "programático_confirmado_08d", match

    # 2. Mover tradição russa/pós-soviética
    if _match_any(search_text, RUSSIAN_POSTSOVIET):
        match = _first_match(search_text, RUSSIAN_POSTSOVIET)
        return "extended", "tradição_russa_doutrinária", match

    # 3. Mover históricos
    if _match_any(search_text, HISTORICAL):
        match = _first_match(search_text, HISTORICAL)
        return "extended", "artigo_histórico", match

    # Sem classificação automática — mantém para revisão final
    return "nuclear", "sem_classificação_automática", ""


def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)

    nuclear_before = len(df[df["ring"] == "nuclear"])
    print(f"Entrada: {len(df):,} registros | Nuclear: {nuclear_before}")

    # Operar apenas sobre nucleares "sem_sinal_claro_manter"
    unclear_mask = (
        (df["ring"] == "nuclear")
        & (df.get("reclassification_reason", pd.Series(dtype=str)).fillna("") == "sem_sinal_claro_manter")
    )

    n_unclear = unclear_mask.sum()
    print(f"Registros 'sem_sinal_claro' a processar: {n_unclear}")

    # Aplicar ajustes
    log_entries = []

    for idx in df[unclear_mask].index:
        row = df.loc[idx]
        new_ring, reason, matched = adjust_nuclear(row)
        df.at[idx, "ring"] = new_ring
        df.at[idx, "reclassification_reason"] = reason
        df.at[idx, "matched_pattern"] = matched

        log_entries.append({
            "title": row["title"],
            "journal": row.get("journal", ""),
            "publication_year": row.get("publication_year", ""),
            "old_ring": "nuclear",
            "new_ring": new_ring,
            "reason": reason,
            "matched": matched,
        })

    # Salvar
    df = df.sort_values("cited_by_count", ascending=False)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    log_df = pd.DataFrame(log_entries)
    log_df.to_csv(OUTPUT_LOG, index=False, encoding="utf-8-sig")

    # Contagens finais
    nuclear_after = len(df[df["ring"] == "nuclear"])
    extended_after = len(df[df["ring"] == "extended"])
    moved = nuclear_before - nuclear_after

    # Breakdown
    reason_counts = log_df["reason"].value_counts() if len(log_df) > 0 else pd.Series(dtype=int)

    print(f"\n{'='*60}")
    print("AJUSTE FINAL DO ANEL NUCLEAR")
    print(f"{'='*60}")
    print(f"Nuclear antes:              {nuclear_before:>7,}")
    print(f"Movidos para estendido:     {moved:>7,}")
    print(f"Nuclear FINAL:              {nuclear_after:>7,}")
    print(f"Estendido FINAL:            {extended_after:>7,}")

    print(f"\nBreakdown dos {n_unclear} 'sem_sinal_claro':")
    for reason, cnt in reason_counts.items():
        print(f"  {reason:40s}: {cnt:>5,}")

    # Listar movidos
    moved_entries = [e for e in log_entries if e["new_ring"] == "extended"]
    if moved_entries:
        print(f"\nMovidos para estendido ({len(moved_entries)}):")
        for e in moved_entries:
            print(f"  [{e['reason']}] {str(e['title'])[:80]}")

    # Listar remanescentes sem classificação automática
    remaining = [e for e in log_entries if e["reason"] == "sem_classificação_automática"]
    if remaining:
        print(f"\n⚠ REMANESCENTES SEM CLASSIFICAÇÃO ({len(remaining)}):")
        print("  (Estes permanecerão no nuclear. Revise se necessário.)")
        for e in remaining:
            title = str(e["title"])[:75]
            journal = str(e.get("journal", ""))[:25]
            print(f"  {title}  [{journal}]")
    else:
        print(f"\n✓ Todos os registros foram classificados automaticamente.")

    print(f"\n{'='*60}")
    print(f"CORPUS CONGELADO: {OUTPUT_FILE.name}")
    print(f"{'='*60}")
    print(f"  Nuclear:   {nuclear_after:,}")
    print(f"  Estendido: {extended_after:,}")
    print(f"  Total:     {len(df):,}")


if __name__ == "__main__":
    main()
