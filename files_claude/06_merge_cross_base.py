"""
06_merge_cross_base.py  (v2 — inclui SciELO)
==============================================
PRISMA — Etapa "Identification"

Consolida os cinco CSVs refinados em dataset único com colunas padronizadas.
Atualização: inclui SciELO como quinta base.

Entrada : data/raw/*_refined.csv + scielo_results.csv
Saída   : data/interim/01_merged_all_sources.csv

Uso:
    python src/pipelines/06_merge_cross_base.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERIM_DIR = BASE_DIR / "data" / "interim"
INTERIM_DIR.mkdir(parents=True, exist_ok=True)

# ── Arquivos de entrada ─────────────────────────────────────────────────────
FILES = {
    "crossref": RAW_DIR / "crossref_results_refined.csv",
    "openalex": RAW_DIR / "openalex_results_refined.csv",
    "scopus": RAW_DIR / "scopus_results_refined.csv",
    "semantic_scholar": RAW_DIR / "semantic_scholar_results_core.csv",
    "scielo": RAW_DIR / "scielo_results.csv",
}

STANDARD_COLS = [
    "source", "source_id", "query_term", "title", "doi",
    "publication_year", "journal", "type", "language",
    "cited_by_count", "authors", "abstract",
]


def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[STANDARD_COLS]


def load_crossref(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)
    df["source_id"] = df.get("crossref_doi", df.get("doi", ""))
    df["source"] = "crossref"
    return _ensure_cols(df)


def load_openalex(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)
    df["source_id"] = df.get("openalex_id", "")
    df["source"] = "openalex"
    return _ensure_cols(df)


def load_scopus(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)
    df["source_id"] = df.get("scopus_id", "")
    df["source"] = "scopus"
    return _ensure_cols(df)


def load_semantic_scholar(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    if "citation_count" in df.columns and "cited_by_count" not in df.columns:
        df["cited_by_count"] = df["citation_count"]
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)
    df["source_id"] = df.get("paper_id", "")
    df["source"] = "semantic_scholar"
    return _ensure_cols(df)


def load_scielo(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)
    df["source_id"] = df.get("url", "")
    df["source"] = "scielo"
    return _ensure_cols(df)


LOADERS = {
    "crossref": load_crossref,
    "openalex": load_openalex,
    "scopus": load_scopus,
    "semantic_scholar": load_semantic_scholar,
    "scielo": load_scielo,
}


def main():
    frames = []

    for name, path in FILES.items():
        if not path.exists():
            print(f"  AVISO: {path.name} não encontrado — pulando {name}")
            continue
        loader = LOADERS[name]
        df = loader(path)
        print(f"  {name:25s} → {len(df):>6,} registros")
        frames.append(df)

    if not frames:
        print("Nenhum arquivo encontrado. Verifique data/raw/.")
        return

    merged = pd.concat(frames, ignore_index=True)

    merged["doi_norm"] = (
        merged["doi"].fillna("").astype(str).str.strip().str.lower()
        .str.replace(r"^https?://doi\.org/", "", regex=True)
    )
    merged["title_norm"] = merged["title"].fillna("").astype(str).str.strip().str.lower()
    merged["journal_norm"] = merged["journal"].fillna("").astype(str).str.strip().str.lower()
    merged["publication_year"] = merged["publication_year"].fillna("").astype(str).str.strip()

    output = INTERIM_DIR / "01_merged_all_sources.csv"
    merged.to_csv(output, index=False, encoding="utf-8-sig")

    print(f"\n{'='*60}")
    print(f"TOTAL IDENTIFICADO (antes de deduplicação): {len(merged):,}")
    print(f"Registros por fonte:")
    print(merged["source"].value_counts().to_string())
    print(f"\nSalvo em: {output}")


if __name__ == "__main__":
    main()
