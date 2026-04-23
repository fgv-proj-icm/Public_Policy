from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parents[2]

SCRIPTS = [
    "src/pipelines/01b_collect_crossref_refined.py",
    "src/pipelines/01c_review_crossref_refined.py",
    "src/pipelines/03_collect_scopus.py",
    "src/pipelines/03b_review_scopus.py",
    "src/pipelines/04_build_unified_base.py",
]

for script in SCRIPTS:
    print(f"\n>>> Rodando {script}")
    result = subprocess.run([sys.executable, str(BASE_DIR / script)], check=False)
    if result.returncode != 0:
        raise SystemExit(f"Falha em {script} (código {result.returncode})")

print("\nPipeline concluída até a base unificada.")
print("Pausa aqui para análise manual.")