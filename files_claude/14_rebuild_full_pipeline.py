"""
14_rebuild_full_pipeline.py
===========================
Script de conveniência que re-executa o pipeline completo
a partir do merge (06), incorporando todas as bases incluindo SciELO.

Executa em sequência:
  06 → 07 → 08 → 08b → 08c → 08d → 09 → 10 → 11 → 12

Uso:
    python src/pipelines/14_rebuild_full_pipeline.py

Nota: o script 11 (enriquecimento via OpenAlex) faz chamadas à API
      e pode levar alguns minutos. Para pular, use --skip-enrich.
"""

from pathlib import Path
import subprocess
import sys
import time

BASE_DIR = Path(__file__).resolve().parents[2]
PIPELINES_DIR = BASE_DIR / "src" / "pipelines"

PIPELINE_STEPS = [
    ("06_merge_cross_base.py",           "Merge cross-base (5 bases)"),
    ("07_dedup_cross_base.py",           "Deduplicação inter-bases"),
    ("08_screen_prisma.py",              "Triagem PRISMA"),
    ("08b_clean_and_enrich.py",          "Limpeza pós-triagem"),
    ("08c_reclassify_nuclear.py",        "Reclassificação nuclear (3 acepções)"),
    ("08d_final_nuclear_adjustment.py",  "Ajuste final do nuclear"),
    ("09_prisma_flow.py",               "PRISMA flow diagram"),
    ("10_export_bibliometrix.py",        "Exportação corpus final"),
]

ENRICH_STEPS = [
    ("11_enrich_references.py",          "Enriquecimento referências (OpenAlex API)"),
    ("12_metadata_completeness.py",      "Completude de metadados"),
]


def run_script(script_name: str, description: str) -> bool:
    script_path = PIPELINES_DIR / script_name
    if not script_path.exists():
        print(f"  ⚠ {script_name} não encontrado — pulando")
        return True  # Não bloqueia o pipeline

    print(f"\n{'─'*60}")
    print(f"  ▶ {description}")
    print(f"    {script_name}")
    print(f"{'─'*60}")

    start = time.time()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(BASE_DIR),
        capture_output=False,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\n  ✗ FALHA em {script_name} (código {result.returncode})")
        print(f"    Tempo: {elapsed:.1f}s")
        return False

    print(f"\n  ✓ {script_name} concluído ({elapsed:.1f}s)")
    return True


def main():
    skip_enrich = "--skip-enrich" in sys.argv

    print("=" * 60)
    print("REBUILD COMPLETO DO PIPELINE")
    print("=" * 60)
    print(f"Diretório base: {BASE_DIR}")
    print(f"Enriquecimento: {'DESABILITADO (--skip-enrich)' if skip_enrich else 'HABILITADO'}")

    # Pipeline principal
    for script, desc in PIPELINE_STEPS:
        if not run_script(script, desc):
            print(f"\n✗ Pipeline interrompido em {script}")
            sys.exit(1)

    # Enriquecimento (opcional)
    if not skip_enrich:
        for script, desc in ENRICH_STEPS:
            if not run_script(script, desc):
                print(f"\n⚠ Enriquecimento falhou em {script}, mas pipeline principal está OK.")
                break
    else:
        # Rodar só o 12 (completude) sem o 11 (referências)
        run_script("12_metadata_completeness.py", "Completude de metadados (sem re-enriquecimento)")

    print(f"\n{'='*60}")
    print("PIPELINE CONCLUÍDO")
    print(f"{'='*60}")
    print(f"Corpus congelado: data/interim/06_frozen_corpus.csv")
    print(f"Exportações:      data/final/corpus_*.csv")
    print(f"PRISMA flow:      docs/04_prisma_flow.md")
    print(f"\nPróximo passo: quarto render relatorio_bibliometrico_politica_judiciaria.qmd")


if __name__ == "__main__":
    main()
