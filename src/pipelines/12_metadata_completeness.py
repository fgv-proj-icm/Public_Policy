"""
12_metadata_completeness.py
===========================
Análise de completude de metadados do corpus completo e do anel nuclear.

Produz métricas de cobertura para cada campo relevante:
  - DOI, título, periódico, idioma, autores, abstract, ano
  - Para o nuclear enriquecido: referências e abstract via OpenAlex

Essas métricas entram na seção de Método do artigo como indicador
de qualidade dos dados e justificativa para escolhas analíticas.

Entrada : data/interim/06_frozen_corpus.csv
          data/interim/07_nuclear_enriched.csv   (se disponível)
Saída   : data/interim/08_metadata_completeness.csv
          data/interim/08_metadata_report.txt

Uso:
    python src/pipelines/12_metadata_completeness.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_CORPUS = INTERIM_DIR / "06_frozen_corpus.csv"
INPUT_ENRICHED = INTERIM_DIR / "07_nuclear_enriched.csv"

OUTPUT_CSV = INTERIM_DIR / "08_metadata_completeness.csv"
OUTPUT_REPORT = INTERIM_DIR / "08_metadata_report.txt"


def is_present(value) -> bool:
    """Verifica se um valor de metadado está efetivamente preenchido."""
    if pd.isna(value):
        return False
    s = str(value).strip().lower()
    return s not in ("", "nan", "n/d", "none", "na", "null")


def compute_completeness(df: pd.DataFrame, label: str) -> dict:
    """Calcula métricas de completude para cada campo."""
    n = len(df)
    if n == 0:
        return {}

    fields = {
        "title": "Título",
        "doi": "DOI",
        "publication_year": "Ano de publicação",
        "journal": "Periódico",
        "language": "Idioma",
        "authors": "Autores",
        "abstract": "Resumo (abstract)",
        "cited_by_count": "Contagem de citações",
    }

    results = []
    for col, col_label in fields.items():
        if col not in df.columns:
            present = 0
        elif col == "cited_by_count":
            # Para citações, "presente" = valor numérico >= 0
            present = pd.to_numeric(df[col], errors="coerce").notna().sum()
        else:
            present = df[col].apply(is_present).sum()

        missing = n - present
        pct = present / n * 100

        results.append({
            "corpus": label,
            "campo": col_label,
            "campo_id": col,
            "total": n,
            "preenchidos": present,
            "faltantes": missing,
            "pct_preenchido": round(pct, 1),
        })

    return results


def main():
    # ── Carregar corpus ────────────────────────────────────────────────
    df = pd.read_csv(INPUT_CORPUS, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)

    nuclear = df[df["ring"] == "nuclear"].copy()
    extended = df[df["ring"] == "extended"].copy()

    print(f"Corpus total:  {len(df):,}")
    print(f"Nuclear:       {len(nuclear):,}")
    print(f"Estendido:     {len(extended):,}")

    # ── Completude por corpus ──────────────────────────────────────────
    all_results = []
    all_results.extend(compute_completeness(df, "Corpus completo"))
    all_results.extend(compute_completeness(nuclear, "Anel nuclear"))
    all_results.extend(compute_completeness(extended, "Anel estendido"))

    # ── Completude por base de dados ───────────────────────────────────
    for source in df["source"].dropna().unique():
        subset = df[df["source"] == source]
        all_results.extend(compute_completeness(subset, f"Base: {source}"))

    # ── Enriquecimento (se disponível) ─────────────────────────────────
    enrichment_stats = None
    if INPUT_ENRICHED.exists():
        df_enriched = pd.read_csv(INPUT_ENRICHED, dtype=str)
        n_enriched = len(df_enriched)
        n_found = df_enriched["found_in_openalex"].apply(
            lambda x: str(x).strip().lower() == "true"
        ).sum()
        n_with_refs = pd.to_numeric(
            df_enriched["n_references"], errors="coerce"
        ).fillna(0).gt(0).sum()
        n_with_abstract = df_enriched["abstract_enriched"].apply(is_present).sum()

        refs_values = pd.to_numeric(df_enriched["n_references"], errors="coerce").fillna(0)

        enrichment_stats = {
            "total": n_enriched,
            "found": int(n_found),
            "with_refs": int(n_with_refs),
            "with_abstract": int(n_with_abstract),
            "refs_mean": refs_values[refs_values > 0].mean() if (refs_values > 0).any() else 0,
            "refs_median": refs_values[refs_values > 0].median() if (refs_values > 0).any() else 0,
        }

        all_results.extend([
            {
                "corpus": "Nuclear (enriquecido)",
                "campo": "Encontrado no OpenAlex",
                "campo_id": "found_openalex",
                "total": n_enriched,
                "preenchidos": int(n_found),
                "faltantes": n_enriched - int(n_found),
                "pct_preenchido": round(n_found / n_enriched * 100, 1),
            },
            {
                "corpus": "Nuclear (enriquecido)",
                "campo": "Com referências (referenced_works)",
                "campo_id": "has_references",
                "total": n_enriched,
                "preenchidos": int(n_with_refs),
                "faltantes": n_enriched - int(n_with_refs),
                "pct_preenchido": round(n_with_refs / n_enriched * 100, 1),
            },
            {
                "corpus": "Nuclear (enriquecido)",
                "campo": "Com abstract (via OpenAlex)",
                "campo_id": "has_abstract_enriched",
                "total": n_enriched,
                "preenchidos": int(n_with_abstract),
                "faltantes": n_enriched - int(n_with_abstract),
                "pct_preenchido": round(n_with_abstract / n_enriched * 100, 1),
            },
        ])

    # ── Salvar CSV ─────────────────────────────────────────────────────
    df_results = pd.DataFrame(all_results)
    df_results.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # ── Relatório textual ──────────────────────────────────────────────
    lines = []
    lines.append("=" * 70)
    lines.append("ANÁLISE DE COMPLETUDE DE METADADOS")
    lines.append("=" * 70)

    for corpus_label in df_results["corpus"].unique():
        subset = df_results[df_results["corpus"] == corpus_label]
        lines.append(f"\n{'─'*50}")
        lines.append(f"  {corpus_label}")
        lines.append(f"{'─'*50}")
        for _, row in subset.iterrows():
            lines.append(
                f"  {row['campo']:35s}  "
                f"{row['preenchidos']:>6,}/{row['total']:>6,}  "
                f"({row['pct_preenchido']:>5.1f}%)"
            )

    if enrichment_stats:
        lines.append(f"\n{'─'*50}")
        lines.append("  ENRIQUECIMENTO VIA OPENALEX (nuclear)")
        lines.append(f"{'─'*50}")
        lines.append(f"  Referências por artigo (média):  {enrichment_stats['refs_mean']:.1f}")
        lines.append(f"  Referências por artigo (mediana): {enrichment_stats['refs_median']:.0f}")

    report = "\n".join(lines)
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    # ── Console ────────────────────────────────────────────────────────
    print(f"\n{report}")
    print(f"\nArquivos salvos:")
    print(f"  CSV:       {OUTPUT_CSV}")
    print(f"  Relatório: {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
