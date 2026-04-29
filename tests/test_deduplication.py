"""Testes unitários para lógica de deduplicação."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.normalize import compute_metadata_score


def _make_df(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    for col in ["doi_norm", "title_norm", "publication_year", "journal_norm",
                "abstract", "authors", "language", "cited_by_count"]:
        if col not in df.columns:
            df[col] = ""
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)
    return df


def _dedup_by_doi(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["meta_score"] = df.apply(compute_metadata_score, axis=1)
    df = df.sort_values(["cited_by_count", "meta_score"], ascending=[False, False])
    return df[df["doi_norm"] != ""].drop_duplicates(subset=["doi_norm"], keep="first")


def _dedup_by_fallback(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["meta_score"] = df.apply(compute_metadata_score, axis=1)
    df = df.sort_values(["cited_by_count", "meta_score"], ascending=[False, False])
    return df[df["doi_norm"] == ""].drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"], keep="first"
    )


class TestDedupByDoi:
    def test_keeps_higher_score_record(self):
        records = [
            {"doi_norm": "10.1234/foo", "abstract": "", "authors": "", "language": "", "cited_by_count": 10, "title": "A"},
            {"doi_norm": "10.1234/foo", "abstract": "has abstract", "authors": "Jane", "language": "en", "cited_by_count": 10, "title": "B"},
        ]
        df = _make_df(records)
        result = _dedup_by_doi(df)
        assert len(result) == 1
        assert result.iloc[0]["title"] == "B"

    def test_keeps_higher_citation_record(self):
        records = [
            {"doi_norm": "10.5678/bar", "abstract": "x", "cited_by_count": 100, "title": "High"},
            {"doi_norm": "10.5678/bar", "abstract": "x", "cited_by_count": 5, "title": "Low"},
        ]
        df = _make_df(records)
        result = _dedup_by_doi(df)
        assert len(result) == 1
        assert result.iloc[0]["title"] == "High"

    def test_two_different_dois_kept(self):
        records = [
            {"doi_norm": "10.1/a", "cited_by_count": 1, "title": "A"},
            {"doi_norm": "10.2/b", "cited_by_count": 1, "title": "B"},
        ]
        df = _make_df(records)
        result = _dedup_by_doi(df)
        assert len(result) == 2

    def test_empty_doi_not_deduplicated_here(self):
        records = [
            {"doi_norm": "", "title": "A"},
            {"doi_norm": "", "title": "A"},
        ]
        df = _make_df(records)
        result = _dedup_by_doi(df)
        assert len(result) == 0  # sem DOI → não entra neste bloco


class TestDedupByFallback:
    def test_same_title_year_journal_deduplicated(self):
        records = [
            {"doi_norm": "", "title_norm": "policy paper", "publication_year": "2020", "journal_norm": "nature", "cited_by_count": 5},
            {"doi_norm": "", "title_norm": "policy paper", "publication_year": "2020", "journal_norm": "nature", "cited_by_count": 1},
        ]
        df = _make_df(records)
        result = _dedup_by_fallback(df)
        assert len(result) == 1
        assert result.iloc[0]["cited_by_count"] == 5

    def test_different_year_not_dedup(self):
        records = [
            {"doi_norm": "", "title_norm": "policy paper", "publication_year": "2020", "journal_norm": "nature"},
            {"doi_norm": "", "title_norm": "policy paper", "publication_year": "2021", "journal_norm": "nature"},
        ]
        df = _make_df(records)
        result = _dedup_by_fallback(df)
        assert len(result) == 2

    def test_different_journal_not_dedup(self):
        records = [
            {"doi_norm": "", "title_norm": "policy paper", "publication_year": "2020", "journal_norm": "science"},
            {"doi_norm": "", "title_norm": "policy paper", "publication_year": "2020", "journal_norm": "nature"},
        ]
        df = _make_df(records)
        result = _dedup_by_fallback(df)
        assert len(result) == 2


class TestSchemaValidation:
    def test_validate_valid_corpus(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from validation.schema_check import validate_schema

        df = pd.DataFrame([{
            "source": "openalex",
            "source_id": "W1",
            "title": "Test Article",
            "doi": "10.1234/test",
            "doi_norm": "10.1234/test",
            "title_norm": "test article",
            "journal_norm": "test journal",
            "publication_year": "2020",
            "journal": "Test Journal",
            "type": "article",
            "language": "en",
            "cited_by_count": "5",
            "authors": "Jane Doe",
            "abstract": "Some abstract",
            "ring": "nuclear",
        }])
        errors = validate_schema(df)
        assert errors == [], f"Esperado sem erros, encontrado: {errors}"

    def test_invalid_ring_detected(self):
        from validation.schema_check import validate_schema

        df = pd.DataFrame([{
            "source": "openalex", "title": "A", "doi": "", "doi_norm": "",
            "title_norm": "a", "journal_norm": "j", "publication_year": "2020",
            "journal": "J", "type": "article", "language": "en",
            "cited_by_count": "0", "authors": "", "abstract": "", "ring": "invalid_ring",
        }])
        errors = validate_schema(df)
        assert any("ring" in e for e in errors), f"Esperava erro de ring, encontrado: {errors}"

    def test_missing_columns_detected(self):
        from validation.schema_check import validate_schema

        df = pd.DataFrame([{"title": "A"}])
        errors = validate_schema(df)
        assert any("ausentes" in e or "Colunas" in e for e in errors)
