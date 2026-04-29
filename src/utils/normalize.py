"""
src/utils/normalize.py
======================
Funções de normalização compartilhadas entre os scripts do pipeline.

Regras estáveis: qualquer mudança aqui afeta deduplicação e curadoria.
"""

from __future__ import annotations

import re
import pandas as pd


def normalize_doi(value: str | float | None) -> str:
    """Remove prefixo URL, converte para lowercase, strip."""
    if pd.isna(value) or value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"^https?://doi\.org/", "", text)
    return text


def normalize_title(value: str | float | None) -> str:
    """Strip + lowercase para uso como chave de fallback."""
    if pd.isna(value) or value is None:
        return ""
    return str(value).strip().lower()


def normalize_journal(value: str | float | None) -> str:
    """Strip + lowercase do nome do periódico."""
    if pd.isna(value) or value is None:
        return ""
    return str(value).strip().lower()


def extract_year(value: str | float | None) -> str:
    """Extrai o primeiro ano (19xx ou 20xx) de qualquer string."""
    if pd.isna(value) or value is None:
        return ""
    match = re.search(r"((?:19|20)\d{2})", str(value))
    return match.group(1) if match else ""


def compute_metadata_score(row: dict | pd.Series) -> int:
    """Pontua completude de metadados para decidir qual registro manter.

    DOI=3, abstract=2, authors/journal_norm/language=1 cada.
    """
    def _present(v) -> bool:
        return str(v).strip().lower() not in ("", "nan", "none", "na", "null", "n/d")

    score = 0
    if _present(row.get("doi_norm", "")):
        score += 3
    if _present(row.get("abstract", "")):
        score += 2
    if _present(row.get("authors", "")):
        score += 1
    if _present(row.get("journal_norm", "")):
        score += 1
    if _present(row.get("language", "")):
        score += 1
    return score


def dedup_key(doi: str, title: str, year: str, journal: str) -> str:
    """Retorna DOI normalizado se disponível, senão title::year::journal."""
    doi_n = normalize_doi(doi)
    if doi_n:
        return doi_n
    title_n = normalize_title(title)
    year_n = extract_year(year)
    journal_n = normalize_journal(journal)
    return f"{title_n}::{year_n}::{journal_n}"


def apply_normalizations(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas as normalizações padrão ao DataFrame in-place."""
    df["doi_norm"] = df["doi"].apply(normalize_doi)
    df["title_norm"] = df["title"].apply(normalize_title)
    df["journal_norm"] = df["journal"].apply(normalize_journal)
    df["publication_year"] = df["publication_year"].apply(extract_year)
    return df
