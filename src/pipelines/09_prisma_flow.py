"""
09_prisma_flow.py
=================
Gera o diagrama PRISMA-flow com os números consolidados de todas as etapas.

Lê as contagens dos scripts 06, 07 e 08 e produz:
  - Relatório textual no console
  - Arquivo Markdown para o docs/
  - Arquivo HTML com diagrama visual

Entrada : data/interim/01_merged_all_sources.csv  (para N bruto)
          data/interim/02_deduplicated.csv         (para N pós-dedup)
          data/interim/03_screened.csv             (para N incluídos)
          data/interim/03_excluded.csv             (para N excluídos)
          data/interim/03_prisma_counts.csv
Saída   : docs/04_prisma_flow.md
          data/interim/prisma_flow.html

Uso:
    python src/pipelines/09_prisma_flow.py
"""

from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_MD = DOCS_DIR / "04_prisma_flow.md"
OUTPUT_HTML = INTERIM_DIR / "prisma_flow.html"
OUTPUT_LOG = LOGS_DIR / "prisma_flow.csv"


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    df = pd.read_csv(path, usecols=[0])
    return len(df)


def main():
    # ── Coletar números ────────────────────────────────────────────────
    n_identified = count_lines(INTERIM_DIR / "01_merged_all_sources.csv")
    n_after_dedup = count_lines(INTERIM_DIR / "02_deduplicated.csv")
    n_duplicates = n_identified - n_after_dedup

    # Cascata: 06 (congelado) → 05 → 04 → 03
    screened_path = INTERIM_DIR / "06_frozen_corpus.csv"
    if not screened_path.exists():
        screened_path = INTERIM_DIR / "05_reclassified.csv"
    if not screened_path.exists():
        screened_path = INTERIM_DIR / "04_cleaned.csv"
    if not screened_path.exists():
        screened_path = INTERIM_DIR / "03_screened.csv"

    excluded_path = INTERIM_DIR / "04_excluded_update.csv"
    if not excluded_path.exists():
        excluded_path = INTERIM_DIR / "03_excluded.csv"

    if screened_path.exists():
        df_screened = pd.read_csv(screened_path, dtype=str)
        n_nuclear = len(df_screened[df_screened["ring"] == "nuclear"])
        n_extended = len(df_screened[df_screened["ring"] == "extended"])
        n_included = len(df_screened)
    else:
        n_nuclear = n_extended = n_included = 0

    if excluded_path.exists():
        df_excluded = pd.read_csv(excluded_path, dtype=str)
        n_excluded = len(df_excluded)
        exclusion_reasons = df_excluded["exclusion_reason"].value_counts().to_dict()
    else:
        n_excluded = 0
        exclusion_reasons = {}

    # ── Fontes individuais ─────────────────────────────────────────────
    merged_path = INTERIM_DIR / "01_merged_all_sources.csv"
    source_counts = {}
    if merged_path.exists():
        df_merged = pd.read_csv(merged_path, usecols=["source"], dtype=str)
        source_counts = df_merged["source"].value_counts().to_dict()

    # ── Relatório console ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRISMA FLOW DIAGRAM — NÚMEROS CONSOLIDADOS")
    print(f"{'='*60}")
    print()
    print("┌─────────────────────────────────────────────┐")
    print("│            IDENTIFICATION                   │")
    print(f"│  Registros identificados: {n_identified:>14,}     │")
    for src, cnt in source_counts.items():
        print(f"│    {src:25s}: {cnt:>7,}     │")
    print("├─────────────────────────────────────────────┤")
    print(f"│  Duplicatas removidas:    {n_duplicates:>14,}     │")
    print("├─────────────────────────────────────────────┤")
    print("│            SCREENING                        │")
    print(f"│  Registros triados:       {n_after_dedup:>14,}     │")
    print(f"│  Excluídos na triagem:    {n_excluded:>14,}     │")
    for reason, cnt in exclusion_reasons.items():
        print(f"│    {reason:25s}: {cnt:>7,}     │")
    print("├─────────────────────────────────────────────┤")
    print("│            INCLUDED                         │")
    print(f"│  Total incluídos:         {n_included:>14,}     │")
    print(f"│    Anel nuclear:          {n_nuclear:>14,}     │")
    print(f"│    Anel estendido:        {n_extended:>14,}     │")
    print("└─────────────────────────────────────────────┘")

    # ── Markdown ───────────────────────────────────────────────────────
    reasons_text = "\n".join(
        f"  - {reason}: {cnt:,}" for reason, cnt in exclusion_reasons.items()
    )
    sources_text = "\n".join(
        f"  - {src}: {cnt:,}" for src, cnt in source_counts.items()
    )

    md = f"""# PRISMA Flow Diagram

## Identification

Registros identificados nas bases: **{n_identified:,}**

{sources_text}

## Duplicates removed

Duplicatas removidas: **{n_duplicates:,}**

Registros após deduplicação: **{n_after_dedup:,}**

## Screening

Registros triados (título + abstract): **{n_after_dedup:,}**

Excluídos: **{n_excluded:,}**

{reasons_text}

## Included

Total incluídos: **{n_included:,}**

- Anel nuclear (expressão exata "judicial policy" / "política judiciária"): **{n_nuclear:,}**
- Anel estendido (termos cognatos — governance, administration, reform): **{n_extended:,}**
"""
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(f"\nMarkdown salvo em: {OUTPUT_MD}")

    now = datetime.now(timezone.utc).isoformat()
    log_rows = [
        {"step": "identified", "n": n_identified, "rule": "registros identificados nos snapshots data/raw", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
        {"step": "duplicates_removed", "n": n_duplicates, "rule": "doi_norm; fallback title_norm + publication_year + journal_norm", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
        {"step": "screened", "n": n_after_dedup, "rule": "registros pos-deduplicacao triados por titulo/resumo", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
        {"step": "excluded", "n": n_excluded, "rule": "fora do escopo ou metadados insuficientes", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
        {"step": "included_total", "n": n_included, "rule": "anel nuclear + anel estendido", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
        {"step": "included_core_ex", "n": n_nuclear, "rule": "expressao exata/reclassificacao programatica", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
        {"step": "included_adj", "n": n_extended, "rule": "campos cognatos de governanca/administracao/reforma judicial", "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"},
    ]
    for reason, cnt in exclusion_reasons.items():
        log_rows.append({"step": f"excluded_{reason}", "n": cnt, "rule": reason, "timestamp": now, "script": "src/pipelines/09_prisma_flow.py"})
    pd.DataFrame(log_rows).to_csv(OUTPUT_LOG, index=False, encoding="utf-8-sig")
    print(f"Log PRISMA salvo em: {OUTPUT_LOG}")

    # ── HTML ───────────────────────────────────────────────────────────
    reasons_html = "".join(
        f"<div style='font-size:12px;color:#666;margin-left:10px;'>{reason}: {cnt:,}</div>"
        for reason, cnt in exclusion_reasons.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>PRISMA Flow</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; background: #f9f9f9; }}
.box {{ border: 2px solid #333; border-radius: 8px; padding: 16px; margin: 12px auto; background: #fff; text-align: center; max-width: 500px; }}
.box h3 {{ margin: 0 0 8px; font-size: 14px; color: #666; text-transform: uppercase; }}
.box .n {{ font-size: 28px; font-weight: bold; color: #1a1a1a; }}
.box .detail {{ font-size: 13px; color: #888; margin-top: 4px; }}
.arrow {{ text-align: center; font-size: 24px; color: #999; margin: 4px 0; }}
.split {{ display: flex; gap: 16px; justify-content: center; }}
.split .box {{ flex: 1; max-width: 240px; }}
.nuclear {{ border-color: #2563eb; }}
.nuclear .n {{ color: #2563eb; }}
.extended {{ border-color: #059669; }}
.extended .n {{ color: #059669; }}
.excluded {{ border-color: #dc2626; }}
.excluded .n {{ color: #dc2626; }}
</style></head>
<body>
<h1 style="text-align:center;">PRISMA Flow Diagram</h1>

<div class="box">
    <h3>Identification</h3>
    <div class="n">{n_identified:,}</div>
    <div class="detail">registros identificados nos snapshots ativos</div>
</div>
<div class="arrow">▼</div>

<div class="box">
    <h3>Duplicates Removed</h3>
    <div class="n">−{n_duplicates:,}</div>
    <div class="detail">duplicatas inter-bases</div>
</div>
<div class="arrow">▼</div>

<div class="box">
    <h3>Screening</h3>
    <div class="n">{n_after_dedup:,}</div>
    <div class="detail">registros triados por título + abstract</div>
</div>
<div class="arrow">▼</div>

<div class="split">
    <div class="box excluded">
        <h3>Excluded</h3>
        <div class="n">{n_excluded:,}</div>
        {reasons_html}
    </div>
    <div style="display:flex;flex-direction:column;gap:12px;">
        <div class="box nuclear">
            <h3>Nuclear ring</h3>
            <div class="n">{n_nuclear:,}</div>
            <div class="detail">"judicial policy" / "política judiciária"</div>
        </div>
        <div class="box extended">
            <h3>Extended ring</h3>
            <div class="n">{n_extended:,}</div>
            <div class="detail">governance, administration, reform</div>
        </div>
    </div>
</div>

<div class="box" style="margin-top:20px;">
    <h3>Total Included</h3>
    <div class="n">{n_included:,}</div>
</div>

</body></html>"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"HTML salvo em: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
