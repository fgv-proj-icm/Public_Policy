"""
10_export_bibliometrix.py
=========================
Exporta o corpus triado para formatos consumíveis pelo R/bibliometrix.

Produz:
  - CSV do anel nuclear
  - CSV do anel estendido
  - CSV completo (ambos os anéis)
  - Relatório descritivo final

Entrada : data/interim/03_screened.csv
Saída   : data/final/corpus_nuclear.csv
          data/final/corpus_extended.csv
          data/final/corpus_complete.csv

Uso:
    python src/pipelines/10_export_bibliometrix.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"
FINAL_DIR = BASE_DIR / "data" / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# Cascata: 06 (congelado) → 05 → 04 → 03
INPUT_FILE = INTERIM_DIR / "06_frozen_corpus.csv"
if not INPUT_FILE.exists():
    INPUT_FILE = INTERIM_DIR / "05_reclassified.csv"
if not INPUT_FILE.exists():
    INPUT_FILE = INTERIM_DIR / "04_cleaned.csv"
if not INPUT_FILE.exists():
    INPUT_FILE = INTERIM_DIR / "03_screened.csv"

OUTPUT_NUCLEAR = FINAL_DIR / "corpus_nuclear.csv"
OUTPUT_EXTENDED = FINAL_DIR / "corpus_extended.csv"
OUTPUT_COMPLETE = FINAL_DIR / "corpus_complete.csv"

# Colunas para exportação final (limpas, sem colunas auxiliares)
EXPORT_COLS = [
    "title",
    "doi",
    "publication_year",
    "journal",
    "type",
    "language",
    "cited_by_count",
    "authors",
    "abstract",
    "source",
    "ring",
    "indexed_in",
    "n_bases",
    "query_term",
]


def describe_corpus(df: pd.DataFrame, label: str):
    """Imprime estatísticas descritivas do corpus."""
    print(f"\n{'─'*50}")
    print(f"  {label}")
    print(f"{'─'*50}")
    print(f"  Total de registros:  {len(df):,}")

    if "publication_year" in df.columns:
        years = pd.to_numeric(df["publication_year"], errors="coerce").dropna()
        if len(years) > 0:
            print(f"  Período:             {int(years.min())}–{int(years.max())}")

    if "language" in df.columns:
        langs = df["language"].fillna("N/D").value_counts().head(5)
        print(f"  Idiomas (top 5):")
        for lang, cnt in langs.items():
            print(f"    {lang:15s}: {cnt:>5,}")

    if "journal" in df.columns:
        journals = df["journal"].fillna("N/D").value_counts()
        n_journals = journals[journals.index != "N/D"].shape[0]
        print(f"  Periódicos distintos: {n_journals:,}")
        print(f"  Top 10 periódicos:")
        for j, cnt in journals.head(10).items():
            print(f"    {j[:45]:45s}: {cnt:>4,}")

    if "cited_by_count" in df.columns:
        cit = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)
        print(f"  Citações — total: {cit.sum():,.0f}  média: {cit.mean():.1f}  mediana: {cit.median():.0f}  max: {cit.max():.0f}")

    if "source" in df.columns:
        print(f"  Por base de origem:")
        for src, cnt in df["source"].value_counts().items():
            print(f"    {src:25s}: {cnt:>5,}")


def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)

    # Selecionar apenas colunas disponíveis
    available_cols = [c for c in EXPORT_COLS if c in df.columns]

    nuclear = df[df["ring"] == "nuclear"][available_cols].copy()
    extended = df[df["ring"] == "extended"][available_cols].copy()
    complete = df[available_cols].copy()

    nuclear = nuclear.sort_values("cited_by_count", ascending=False)
    extended = extended.sort_values("cited_by_count", ascending=False)
    complete = complete.sort_values("cited_by_count", ascending=False)

    # ── Salvar ─────────────────────────────────────────────────────────
    nuclear.to_csv(OUTPUT_NUCLEAR, index=False, encoding="utf-8-sig")
    extended.to_csv(OUTPUT_EXTENDED, index=False, encoding="utf-8-sig")
    complete.to_csv(OUTPUT_COMPLETE, index=False, encoding="utf-8-sig")

    # ── Relatório ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("EXPORTAÇÃO FINAL — CORPUS PARA BIBLIOMETRIX")
    print(f"{'='*60}")

    describe_corpus(nuclear, "ANEL NUCLEAR — 'judicial policy' / 'política judiciária'")
    describe_corpus(extended, "ANEL ESTENDIDO — termos cognatos")
    describe_corpus(complete, "CORPUS COMPLETO")

    print(f"\n{'='*60}")
    print(f"Arquivos exportados:")
    print(f"  Nuclear:   {OUTPUT_NUCLEAR}")
    print(f"  Estendido: {OUTPUT_EXTENDED}")
    print(f"  Completo:  {OUTPUT_COMPLETE}")
    print(f"\nPróximo passo: carregar em R com bibliometrix::convert2df()")


if __name__ == "__main__":
    main()
