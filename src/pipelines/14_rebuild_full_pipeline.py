"""
14_rebuild_full_pipeline.py
===========================
Reexecuta o pipeline reproduzivel a partir dos snapshots em data/raw.

Uso:
    python src/pipelines/14_rebuild_full_pipeline.py --offline
    python src/pipelines/14_rebuild_full_pipeline.py --with-pop --skip-enrich
"""

from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import time

import pandas as pd
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
PIPELINES_DIR = BASE_DIR / "src" / "pipelines"
RAW_DIR = BASE_DIR / "data" / "raw"

PIPELINE_STEPS = [
    ("06_merge_cross_base.py", "Merge cross-base"),
    ("07_dedup_cross_base.py", "Deduplicacao inter-bases"),
    ("08_screen_prisma.py", "Triagem PRISMA"),
    ("08b_clean_and_enrich.py", "Limpeza pos-triagem"),
    ("08c_reclassify_nuclear.py", "Reclassificacao nuclear"),
    ("08d_final_nuclear_adjustment.py", "Ajuste final do nuclear"),
    ("09_prisma_flow.py", "PRISMA flow e logs"),
    ("10_export_bibliometrix.py", "Exportacao corpus final"),
    ("16_brazil_supplement_compare.py", "Comparacao suplemento Brasil"),
    ("17_export_network_snapshot.py", "Exportacao offline da rede de co-citacao"),
]

ENRICH_STEPS = [
    ("11_enrich_references.py", "Enriquecimento de referencias OpenAlex"),
    ("12_metadata_completeness.py", "Completude de metadados"),
]


def load_config() -> dict:
    config_path = BASE_DIR / "config.yml"
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def run_script(script_name: str, description: str) -> None:
    script_path = PIPELINES_DIR / script_name
    if not script_path.exists():
        print(f"  AVISO: {script_name} nao encontrado; pulando.")
        return

    print(f"\n{'-' * 60}\n{description}\n{script_name}\n{'-' * 60}")
    start = time.time()
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    result = subprocess.run([sys.executable, str(script_path)], cwd=str(BASE_DIR), env=env)
    elapsed = time.time() - start
    if result.returncode != 0:
        raise SystemExit(f"Falha em {script_name} (codigo {result.returncode}, {elapsed:.1f}s)")
    print(f"OK: {script_name} ({elapsed:.1f}s)")


def import_pop_snapshot(label: str, input_name: str, output_name: str) -> Path | None:
    source = RAW_DIR / input_name
    if not source.exists():
        print(f"  PoP ausente: {source.name}")
        return None
    run_script_args = [
        sys.executable,
        str(PIPELINES_DIR / "04_import_pop_scholar.py"),
        "--input",
        str(source),
        "--query-term",
        label,
        "--output",
        output_name,
    ]
    print(f"Importando snapshot PoP: {source.name}")
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    result = subprocess.run(run_script_args, cwd=str(BASE_DIR), env=env)
    if result.returncode != 0:
        raise SystemExit(f"Falha ao importar {source.name}")
    return RAW_DIR / output_name


def prepare_pop(with_pop: bool) -> None:
    consolidated = RAW_DIR / "google_scholar_pop_results.csv"
    if not with_pop:
        if consolidated.exists():
            disabled = RAW_DIR / "google_scholar_pop_results.disabled.csv"
            shutil.move(str(consolidated), str(disabled))
            print(f"Snapshot PoP desabilitado para a rodada principal: {disabled.name}")
        return

    parts = []
    for label, input_name, output_name in [
        ("pop_nuclear", "google_scholar_pop_nuclear_results.csv", "google_scholar_pop_nuclear.csv"),
        ("pop_extended", "google_scholar_pop_extended_results.csv", "google_scholar_pop_extended.csv"),
    ]:
        out = import_pop_snapshot(label, input_name, output_name)
        if out and out.exists():
            parts.append(pd.read_csv(out, dtype=str))

    if parts:
        merged = pd.concat(parts, ignore_index=True)
        merged.to_csv(consolidated, index=False, encoding="utf-8-sig")
        print(f"Snapshot PoP consolidado: {consolidated} ({len(merged):,} linhas)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Usa apenas snapshots locais.")
    parser.add_argument("--with-pop", action="store_true", help="Inclui snapshot Google Scholar/PoP no corpus principal.")
    parser.add_argument("--skip-enrich", action="store_true", help="Nao chama OpenAlex para referencias.")
    args = parser.parse_args()

    config = load_config()
    with_pop = bool(args.with_pop or config.get("pipeline", {}).get("include_google_scholar_pop", False))

    print("=" * 60)
    print("REBUILD REPRODUZIVEL DO PIPELINE")
    print("=" * 60)
    print(f"Base: {BASE_DIR}")
    print(f"Offline: {args.offline or config.get('offline', True)}")
    print(f"Incluir PoP no corpus principal: {with_pop}")

    prepare_pop(with_pop)

    for script, desc in PIPELINE_STEPS:
        run_script(script, desc)

    if args.skip_enrich or not config.get("pipeline", {}).get("refresh_openalex_references", False):
        run_script("12_metadata_completeness.py", "Completude de metadados")
    else:
        for script, desc in ENRICH_STEPS:
            run_script(script, desc)

    print("\nPipeline concluido.")
    print("Render final: quarto render relatorio_bibliometrico_politica_judiciaria.qmd --to docx")


if __name__ == "__main__":
    main()
