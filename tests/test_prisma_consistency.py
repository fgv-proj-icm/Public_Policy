"""Testes unitários para check_prisma_consistency."""
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from validation.schema_check import check_prisma_consistency


def _write_prisma(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "prisma_flow.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


class TestPrismaConsistency:
    def test_consistent_counts_pass(self, tmp_path):
        rows = [
            {"etapa": "identified", "n": 7161},
            {"etapa": "duplicates_removed", "n": 1193},
            {"etapa": "screened", "n": 5968},          # 7161 - 1193
            {"etapa": "excluded", "n": 1042},
            {"etapa": "included_total", "n": 4926},    # 5968 - 1042
            {"etapa": "included_core_ex", "n": 115},
            {"etapa": "included_adj", "n": 4811},      # 115 + 4811 = 4926
        ]
        path = _write_prisma(tmp_path, rows)
        errors = check_prisma_consistency(path)
        assert errors == [], f"Contagens corretas devem passar sem erros: {errors}"

    def test_wrong_screened_detected(self, tmp_path):
        rows = [
            {"etapa": "identified", "n": 7161},
            {"etapa": "duplicates_removed", "n": 1193},
            {"etapa": "screened", "n": 9999},           # ERRADO: deveria ser 5968
            {"etapa": "excluded", "n": 1042},
            {"etapa": "included_total", "n": 4926},
        ]
        path = _write_prisma(tmp_path, rows)
        errors = check_prisma_consistency(path)
        assert any("screened" in e for e in errors), f"Deveria detectar erro em screened: {errors}"

    def test_wrong_included_total_detected(self, tmp_path):
        rows = [
            {"etapa": "identified", "n": 7161},
            {"etapa": "duplicates_removed", "n": 1193},
            {"etapa": "screened", "n": 5968},
            {"etapa": "excluded", "n": 1042},
            {"etapa": "included_total", "n": 9999},     # ERRADO: deveria ser 4926
        ]
        path = _write_prisma(tmp_path, rows)
        errors = check_prisma_consistency(path)
        assert any("included_total" in e for e in errors), f"Deveria detectar erro em included_total: {errors}"

    def test_nuclear_plus_extended_mismatch_detected(self, tmp_path):
        rows = [
            {"etapa": "included_total", "n": 4926},
            {"etapa": "included_core_ex", "n": 115},
            {"etapa": "included_adj", "n": 5000},       # ERRADO: 115 + 5000 != 4926
        ]
        path = _write_prisma(tmp_path, rows)
        errors = check_prisma_consistency(path)
        assert any("nuclear" in e or "extended" in e or "included_total" in e for e in errors)

    def test_file_not_found_returns_error(self, tmp_path):
        path = tmp_path / "nao_existe.csv"
        errors = check_prisma_consistency(path)
        assert any("não encontrado" in e for e in errors)

    def test_partial_data_no_crash(self, tmp_path):
        rows = [
            {"etapa": "identified", "n": 100},
        ]
        path = _write_prisma(tmp_path, rows)
        errors = check_prisma_consistency(path)
        assert isinstance(errors, list)

    def test_real_prisma_flow(self):
        real_path = Path(__file__).resolve().parents[1] / "logs" / "prisma_flow.csv"
        if not real_path.exists():
            pytest.skip("logs/prisma_flow.csv não disponível neste ambiente")
        errors = check_prisma_consistency(real_path)
        assert errors == [], f"prisma_flow.csv real tem inconsistências: {errors}"
