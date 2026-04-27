from __future__ import annotations

from pathlib import Path
import argparse
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)

STANDARD_COLS = [
    "source","source_id","query_term","title","doi",
    "publication_year","journal","type","language",
    "cited_by_count","authors","abstract","url",
]

def norm_year(x) -> str:
    s = "" if pd.isna(x) else str(x)
    m = re.search(r"(19|20)\d{2}", s)
    return m.group(0) if m else ""

def extract_doi(val: str) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    if not s:
        return ""
    m = DOI_RE.search(s)
    if m:
        return m.group(0).rstrip(").,;")
    return s if s.lower().startswith("10.") else ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV de Results exportado do Publish or Perish")
    ap.add_argument("--query-term", required=True, help="Label da rodada (ex: pop_nuclear / pop_extended)")
    ap.add_argument("--output", required=True, help="Nome do CSV de saída em data/raw/")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {inp}")

    df = pd.read_csv(inp)

    # Cabeçalhos típicos do PoP (se algum mudar, ajustamos depois)
    col_map = {
        "title": "Title",
        "authors": "Authors",
        "year": "Year",
        "source": "Source",
        "cites": "Cites",
        "url": "ArticleURL",
        "doi": "DOI",
        "abstract": "Abstract",
        "type": "Type",
    }

    for need in ["Title", "Authors", "Year"]:
        if need not in df.columns:
            raise RuntimeError(f"Coluna obrigatória ausente: {need}. Colunas disponíveis: {df.columns.tolist()}")

    out = pd.DataFrame(columns=STANDARD_COLS)
    out["source"] = "google_scholar_pop"
    out["query_term"] = args.query_term
    out["title"] = df[col_map["title"]].fillna("").astype(str)
    out["authors"] = df[col_map["authors"]].fillna("").astype(str)
    out["publication_year"] = df[col_map["year"]].apply(norm_year)

    out["journal"] = df[col_map["source"]].fillna("").astype(str) if col_map["source"] in df.columns else ""
    out["cited_by_count"] = pd.to_numeric(df[col_map["cites"]], errors="coerce").fillna(0) if col_map["cites"] in df.columns else 0
    out["url"] = df[col_map["url"]].fillna("").astype(str) if col_map["url"] in df.columns else ""
    out["doi"] = df[col_map["doi"]].apply(extract_doi) if col_map["doi"] in df.columns else ""
    out["abstract"] = df[col_map["abstract"]].fillna("").astype(str).str.slice(0, 500) if col_map["abstract"] in df.columns else ""

    out["type"] = df[col_map["type"]].fillna("").astype(str) if col_map["type"] in df.columns else "unknown"
    out["language"] = ""

    # source_id: DOI > URL > title+year
    out["source_id"] = out["doi"].where(out["doi"] != "", "")
    out.loc[out["source_id"] == "", "source_id"] = out["url"].where(out["url"] != "", "")
    out.loc[out["source_id"] == "", "source_id"] = out["title"].str.lower().str.strip() + "::" + out["publication_year"]

    # dedup interno (para não inflar antes do merge)
    out["doi_norm"] = out["doi"].fillna("").astype(str).str.strip().str.lower()
    out["title_norm"] = out["title"].fillna("").astype(str).str.strip().str.lower()

    with_doi = out[out["doi_norm"] != ""].drop_duplicates(subset=["doi_norm"], keep="first")
    without_doi = out[out["doi_norm"] == ""].drop_duplicates(subset=["title_norm","publication_year","journal"], keep="first")
    out_final = pd.concat([with_doi, without_doi], ignore_index=True)

    # volta para esquema padrão
    out_final = out_final[STANDARD_COLS]

    out_path = RAW_DIR / args.output
    out_final.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("=" * 60)
    print("IMPORT PoP → OK")
    print("=" * 60)
    print("In:", inp)
    print("Out:", out_path)
    print("Rows:", len(out_final))
    print("Has DOI:", (out_final["doi"].fillna("") != "").sum())

if __name__ == "__main__":
    main()
