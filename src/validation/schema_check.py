"""
src/validation/schema_check.py
================================
Guardrails metodológicos para o corpus bibliométrico.

Funções:
  validate_schema(df)         -> lista de erros de schema
  check_duplicates(df)        -> contagens de duplicatas
  check_prisma_consistency(p) -> lista de inconsistências PRISMA
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLS = [
    "source", "title", "doi", "publication_year",
    "journal", "type", "language", "cited_by_count",
    "authors", "abstract", "ring",
]

REQUIRED_NORM_COLS = ["doi_norm", "title_norm", "journal_norm"]

VALID_RINGS = {"nuclear", "extended"}
YEAR_RANGE = (1900, 2030)


def _is_present(value) -> bool:
    return str(value).strip().lower() not in ("", "nan", "none", "na", "null", "n/d")


def validate_schema(df: pd.DataFrame) -> list[str]:
    """Valida schema do corpus. Retorna lista de mensagens de erro (vazia = OK)."""
    errors: list[str] = []

    # 1. Colunas obrigatórias
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        errors.append(f"Colunas obrigatórias ausentes: {missing}")

    if df.empty:
        errors.append("DataFrame vazio.")
        return errors

    # 2. Colunas de normalização (se presentes, verificar consistência)
    for col in REQUIRED_NORM_COLS:
        if col not in df.columns:
            errors.append(f"Coluna de normalização ausente: {col} (rode 06_merge_cross_base.py)")

    # 3. Valores de 'ring'
    if "ring" in df.columns:
        invalid_rings = df["ring"].dropna().unique()
        bad = [r for r in invalid_rings if str(r).strip().lower() not in VALID_RINGS]
        if bad:
            n_bad = df["ring"].isin(bad).sum()
            errors.append(
                f"Valores inválidos em 'ring' ({n_bad} registros): {bad}. "
                f"Esperado: {VALID_RINGS}"
            )

    # 4. Anos plausíveis
    if "publication_year" in df.columns:
        years = pd.to_numeric(df["publication_year"], errors="coerce").dropna()
        out_of_range = years[(years < YEAR_RANGE[0]) | (years > YEAR_RANGE[1])]
        if not out_of_range.empty:
            errors.append(
                f"{len(out_of_range)} registros com ano fora do intervalo "
                f"[{YEAR_RANGE[0]}, {YEAR_RANGE[1]}]: {sorted(out_of_range.unique().tolist())}"
            )

    # 5. Títulos vazios
    if "title" in df.columns:
        n_empty = df["title"].apply(lambda v: not _is_present(v)).sum()
        if n_empty > 0:
            errors.append(f"{n_empty} registros sem título.")

    # 6. cited_by_count deve ser numérico (quando preenchido)
    if "cited_by_count" in df.columns:
        converted = pd.to_numeric(df["cited_by_count"], errors="coerce")
        non_numeric = df["cited_by_count"].apply(
            lambda v: not pd.isna(v) and pd.isna(pd.to_numeric(v, errors="coerce"))
        ).sum()
        if non_numeric > 0:
            errors.append(f"{non_numeric} registros com cited_by_count não numérico.")

    return errors


def check_duplicates(df: pd.DataFrame) -> dict[str, int]:
    """Conta duplicatas por DOI e por chave fallback (título+ano+periódico).

    Retorna dict com:
      by_doi       - pares duplicados por DOI normalizado
      by_fallback  - pares duplicados por título+ano+periódico
    """
    result: dict[str, int] = {"by_doi": 0, "by_fallback": 0}

    if "doi_norm" in df.columns:
        doi_df = df[df["doi_norm"].apply(_is_present)]
        dup_doi = doi_df.duplicated(subset=["doi_norm"], keep=False)
        result["by_doi"] = int(dup_doi.sum())

    if all(c in df.columns for c in ["title_norm", "publication_year", "journal_norm"]):
        no_doi = df[~df.get("doi_norm", pd.Series("")).apply(_is_present)] if "doi_norm" in df.columns else df
        if not no_doi.empty:
            dup_fallback = no_doi.duplicated(
                subset=["title_norm", "publication_year", "journal_norm"], keep=False
            )
            result["by_fallback"] = int(dup_fallback.sum())

    return result


def check_prisma_consistency(prisma_path: str | Path) -> list[str]:
    """Verifica consistência interna do arquivo PRISMA flow.

    Regras verificadas:
      screened = identified - duplicates_removed
      included_total = screened - excluded
      included_core_ex + included_adj = included_total (se ambos presentes)
    """
    path = Path(prisma_path)
    if not path.exists():
        return [f"Arquivo PRISMA não encontrado: {path}"]

    df = pd.read_csv(path, dtype=str)

    # Suporte a dois formatos de coluna
    if "etapa" in df.columns and "n" in df.columns:
        data = {str(r["etapa"]).strip(): _safe_int(r["n"]) for _, r in df.iterrows()}
    elif len(df.columns) >= 2:
        col_key, col_val = df.columns[0], df.columns[1]
        data = {str(r[col_key]).strip(): _safe_int(r[col_val]) for _, r in df.iterrows()}
    else:
        return ["Formato do arquivo PRISMA não reconhecido (esperado: etapa,n ou chave,valor)."]

    errors: list[str] = []

    def _check(label: str, expected: int | None, actual: int | None) -> None:
        if expected is None or actual is None:
            return
        if expected != actual:
            errors.append(f"PRISMA inconsistente [{label}]: esperado {expected}, encontrado {actual}")

    identified = data.get("identified")
    duplicates = data.get("duplicates_removed")
    screened = data.get("screened")
    excluded = data.get("excluded")
    included_total = data.get("included_total")
    nuclear = data.get("included_core_ex")
    extended = data.get("included_adj")

    if identified is not None and duplicates is not None and screened is not None:
        _check("screened = identified - duplicates_removed",
               identified - duplicates, screened)

    if screened is not None and excluded is not None and included_total is not None:
        _check("included_total = screened - excluded",
               screened - excluded, included_total)

    if nuclear is not None and extended is not None and included_total is not None:
        _check("nuclear + extended = included_total",
               nuclear + extended, included_total)

    return errors


def _safe_int(value) -> int | None:
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None
