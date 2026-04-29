"""Testes unitários para src/utils/normalize.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.normalize import (
    normalize_doi,
    normalize_title,
    normalize_journal,
    extract_year,
    compute_metadata_score,
    dedup_key,
)


class TestNormalizeDoi:
    def test_removes_https_prefix(self):
        assert normalize_doi("https://doi.org/10.1234/foo") == "10.1234/foo"

    def test_removes_http_prefix(self):
        assert normalize_doi("http://doi.org/10.1234/foo") == "10.1234/foo"

    def test_lowercase(self):
        assert normalize_doi("10.1234/FOO") == "10.1234/foo"

    def test_empty_string(self):
        assert normalize_doi("") == ""

    def test_none(self):
        assert normalize_doi(None) == ""

    def test_nan(self):
        import math
        assert normalize_doi(float("nan")) == ""

    def test_already_normalized(self):
        assert normalize_doi("10.1234/foo-bar") == "10.1234/foo-bar"

    def test_strips_whitespace(self):
        assert normalize_doi("  10.1234/foo  ") == "10.1234/foo"


class TestNormalizeTitle:
    def test_lowercase(self):
        assert normalize_title("A Great Article") == "a great article"

    def test_strips(self):
        assert normalize_title("  title  ") == "title"

    def test_empty(self):
        assert normalize_title("") == ""

    def test_none(self):
        assert normalize_title(None) == ""


class TestNormalizeJournal:
    def test_lowercase(self):
        assert normalize_journal("Nature Reviews") == "nature reviews"

    def test_none(self):
        assert normalize_journal(None) == ""


class TestExtractYear:
    def test_iso_date(self):
        assert extract_year("2024-01-15") == "2024"

    def test_year_only(self):
        assert extract_year("2024") == "2024"

    def test_year_in_text(self):
        assert extract_year("Published in 2019 online") == "2019"

    def test_19xx(self):
        assert extract_year("1985") == "1985"

    def test_empty(self):
        assert extract_year("") == ""

    def test_none(self):
        assert extract_year(None) == ""

    def test_no_year(self):
        assert extract_year("no year here") == ""


class TestComputeMetadataScore:
    def test_full_record(self):
        row = {
            "doi_norm": "10.1234/foo",
            "abstract": "Some abstract text",
            "authors": "Jane Doe",
            "journal_norm": "nature",
            "language": "en",
        }
        assert compute_metadata_score(row) == 8  # 3+2+1+1+1

    def test_only_doi(self):
        row = {
            "doi_norm": "10.1234/foo",
            "abstract": "",
            "authors": "",
            "journal_norm": "",
            "language": "",
        }
        assert compute_metadata_score(row) == 3

    def test_empty_record(self):
        row = {"doi_norm": "", "abstract": "", "authors": "", "journal_norm": "", "language": ""}
        assert compute_metadata_score(row) == 0

    def test_nan_values(self):
        row = {"doi_norm": "nan", "abstract": "nan", "authors": "nan"}
        assert compute_metadata_score(row) == 0


class TestDedupKey:
    def test_with_doi(self):
        key = dedup_key("10.1234/foo", "Some Title", "2024", "Nature")
        assert key == "10.1234/foo"

    def test_with_doi_url(self):
        key = dedup_key("https://doi.org/10.1234/foo", "Some Title", "2024", "Nature")
        assert key == "10.1234/foo"

    def test_without_doi_uses_fallback(self):
        key = dedup_key("", "A Title", "2024", "Nature Reviews")
        assert key == "a title::2024::nature reviews"

    def test_none_doi_uses_fallback(self):
        key = dedup_key(None, "A Title", "2024", "Nature")
        assert key == "a title::2024::nature"

    def test_fallback_year_extraction(self):
        key = dedup_key("", "A Title", "2024-01-15", "Nature")
        assert key == "a title::2024::nature"
