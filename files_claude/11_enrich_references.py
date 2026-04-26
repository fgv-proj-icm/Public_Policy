"""
11_enrich_references.py
=======================
Coleta de referências bibliográficas (referenced_works) via OpenAlex API
para os artigos do anel nuclear.

Objetivo: viabilizar análise de co-citação do núcleo.

Para cada artigo nuclear com DOI ou OpenAlex ID, consulta a API
e recupera a lista de works citados + abstract (quando disponível).

Entrada : data/final/corpus_nuclear.csv
Saída   : data/interim/07_nuclear_references.csv       (artigo → referência)
          data/interim/07_nuclear_enriched.csv          (nuclear com abstract e n_refs)
          data/interim/07_cocitation_matrix_edges.csv   (pares de co-citação)
          data/interim/07_enrichment_report.txt

Uso:
    python src/pipelines/11_enrich_references.py

Nota: requer OPENALEX_API_KEY no .env (opcional, mas aumenta rate limit).
      Sem API key, funciona com rate limit reduzido (polite pool).
      Defina EMAIL_POLITE no .env para entrar no polite pool do OpenAlex.
"""

from pathlib import Path
import os
import time
import json
from itertools import combinations

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
INTERIM_DIR = BASE_DIR / "data" / "interim"
INTERIM_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = FINAL_DIR / "corpus_nuclear.csv"
OUTPUT_REFS = INTERIM_DIR / "07_nuclear_references.csv"
OUTPUT_ENRICHED = INTERIM_DIR / "07_nuclear_enriched.csv"
OUTPUT_COCITATION = INTERIM_DIR / "07_cocitation_matrix_edges.csv"
OUTPUT_REPORT = INTERIM_DIR / "07_enrichment_report.txt"

API_KEY = os.getenv("OPENALEX_API_KEY", "").strip()
EMAIL = os.getenv("EMAIL_POLITE", "").strip()

OPENALEX_BASE = "https://api.openalex.org/works"

# ── Funções auxiliares ──────────────────────────────────────────────────────

def normalize_doi(doi_str: str) -> str:
    """Normaliza DOI para formato sem prefixo URL."""
    if pd.isna(doi_str) or not doi_str:
        return ""
    doi = str(doi_str).strip().lower()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    return doi


def normalize_openalex_id(oa_id: str) -> str:
    """Extrai ID numérico do OpenAlex."""
    if pd.isna(oa_id) or not oa_id:
        return ""
    oa = str(oa_id).strip()
    # Pode vir como URL completa ou como ID
    if "openalex.org" in oa:
        return oa.split("/")[-1]
    return oa


def build_query_url(doi: str, openalex_id: str) -> str | None:
    """Constrói URL de consulta — prioriza DOI, fallback para OpenAlex ID."""
    if doi:
        return f"{OPENALEX_BASE}/https://doi.org/{doi}"
    if openalex_id and openalex_id.startswith("W"):
        return f"{OPENALEX_BASE}/{openalex_id}"
    return None


def decode_abstract(inverted_index: dict) -> str:
    """Reconstrói abstract a partir do inverted index do OpenAlex."""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


def fetch_work(doi: str, openalex_id: str) -> dict | None:
    """Consulta OpenAlex para um work específico."""
    url = build_query_url(doi, openalex_id)
    if not url:
        return None

    params = {
        "select": "id,display_name,doi,referenced_works,abstract_inverted_index,"
                  "cited_by_count,publication_year,authorships,primary_location"
    }
    if API_KEY:
        params["api_key"] = API_KEY
    elif EMAIL:
        params["mailto"] = EMAIL

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ERRO fetch: {e}")
        return None


def fetch_works_batch(openalex_ids: list[str]) -> dict:
    """Consulta OpenAlex em batch (até 50 IDs por chamada) para metadados de works citados."""
    results = {}
    # OpenAlex permite filtrar por ID com pipe separator
    batch_size = 50

    for i in range(0, len(openalex_ids), batch_size):
        batch = openalex_ids[i:i + batch_size]
        filter_str = "|".join(batch)

        params = {
            "filter": f"openalex_id:{filter_str}",
            "select": "id,display_name,doi,publication_year,cited_by_count,"
                      "primary_location,authorships",
            "per-page": 50,
        }
        if API_KEY:
            params["api_key"] = API_KEY
        elif EMAIL:
            params["mailto"] = EMAIL

        try:
            response = requests.get(OPENALEX_BASE, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            for work in data.get("results", []):
                oa_id = work.get("id", "").split("/")[-1]
                source = (work.get("primary_location") or {}).get("source") or {}
                authors = work.get("authorships", []) or []
                first_author = ""
                if authors:
                    ai = authors[0].get("author", {})
                    first_author = ai.get("display_name", "")

                results[oa_id] = {
                    "ref_openalex_id": oa_id,
                    "ref_title": work.get("display_name", ""),
                    "ref_doi": work.get("doi", ""),
                    "ref_year": work.get("publication_year"),
                    "ref_cited_by": work.get("cited_by_count", 0),
                    "ref_journal": source.get("display_name", ""),
                    "ref_first_author": first_author,
                }
        except Exception as e:
            print(f"  ERRO batch fetch: {e}")

        time.sleep(0.5)

    return results


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df.get("cited_by_count", 0), errors="coerce").fillna(0)

    print(f"Artigos nucleares: {len(df)}")

    # Preparar identificadores
    df["doi_clean"] = df["doi"].apply(normalize_doi)
    if "source_id" in df.columns:
        df["oa_id_clean"] = df["source_id"].apply(normalize_openalex_id)
    else:
        df["oa_id_clean"] = ""

    queryable = df[(df["doi_clean"] != "") | (df["oa_id_clean"].str.startswith("W", na=False))]
    print(f"Com DOI ou OpenAlex ID (consultáveis): {len(queryable)}")

    # ── Fase 1: Coletar referências artigo por artigo ──────────────────
    all_ref_rows = []
    enriched_rows = []
    all_cited_ids = set()

    for idx, row in queryable.iterrows():
        doi = row["doi_clean"]
        oa_id = row["oa_id_clean"]
        title = str(row.get("title", ""))[:60]

        print(f"  [{idx+1}/{len(queryable)}] {title}...", end=" ")

        work = fetch_work(doi, oa_id)

        if work is None:
            print("não encontrado")
            enriched_rows.append({
                "title": row.get("title", ""),
                "doi": row.get("doi", ""),
                "openalex_id": oa_id,
                "abstract_enriched": "",
                "n_references": 0,
                "found_in_openalex": False,
            })
            continue

        # Abstract
        abstract = decode_abstract(work.get("abstract_inverted_index"))

        # Referências
        refs = work.get("referenced_works", []) or []
        ref_ids = [r.split("/")[-1] for r in refs if r]
        all_cited_ids.update(ref_ids)

        print(f"{len(ref_ids)} refs" + (" +abstract" if abstract else ""))

        enriched_rows.append({
            "title": row.get("title", ""),
            "doi": row.get("doi", ""),
            "openalex_id": work.get("id", "").split("/")[-1],
            "abstract_enriched": abstract[:500] if abstract else "",
            "n_references": len(ref_ids),
            "found_in_openalex": True,
        })

        for ref_id in ref_ids:
            all_ref_rows.append({
                "citing_doi": doi,
                "citing_openalex_id": oa_id,
                "citing_title": row.get("title", ""),
                "cited_openalex_id": ref_id,
            })

        time.sleep(0.3)  # rate limit

    # ── Fase 2: Enriquecer metadados dos works citados ─────────────────
    print(f"\nTotal de works citados (únicos): {len(all_cited_ids)}")
    print("Buscando metadados dos works citados em batch...")

    cited_metadata = fetch_works_batch(list(all_cited_ids))
    print(f"Metadados recuperados: {len(cited_metadata)}")

    # Enriquecer ref_rows com metadados
    for row in all_ref_rows:
        ref_id = row["cited_openalex_id"]
        if ref_id in cited_metadata:
            row.update(cited_metadata[ref_id])
        else:
            row.update({
                "ref_openalex_id": ref_id,
                "ref_title": "",
                "ref_doi": "",
                "ref_year": None,
                "ref_cited_by": 0,
                "ref_journal": "",
                "ref_first_author": "",
            })

    # ── Fase 3: Construir matriz de co-citação ────────────────────────
    print("\nConstruindo pares de co-citação...")

    # Agrupar referências por artigo citante
    citing_groups = {}
    for row in all_ref_rows:
        key = row["citing_doi"] or row["citing_openalex_id"]
        if key not in citing_groups:
            citing_groups[key] = set()
        citing_groups[key].add(row["cited_openalex_id"])

    # Gerar pares
    cocitation_pairs = {}
    for citing_key, cited_set in citing_groups.items():
        cited_list = sorted(cited_set)
        for a, b in combinations(cited_list, 2):
            pair = (min(a, b), max(a, b))
            cocitation_pairs[pair] = cocitation_pairs.get(pair, 0) + 1

    cocitation_rows = [
        {"source": a, "target": b, "weight": w}
        for (a, b), w in cocitation_pairs.items()
    ]

    # ── Salvar ─────────────────────────────────────────────────────────
    df_refs = pd.DataFrame(all_ref_rows)
    df_refs.to_csv(OUTPUT_REFS, index=False, encoding="utf-8-sig")

    df_enriched = pd.DataFrame(enriched_rows)
    df_enriched.to_csv(OUTPUT_ENRICHED, index=False, encoding="utf-8-sig")

    df_cocit = pd.DataFrame(cocitation_rows)
    if len(df_cocit) > 0:
        df_cocit = df_cocit.sort_values("weight", ascending=False)
    df_cocit.to_csv(OUTPUT_COCITATION, index=False, encoding="utf-8-sig")

    # ── Relatório ──────────────────────────────────────────────────────
    n_found = sum(1 for r in enriched_rows if r["found_in_openalex"])
    n_with_refs = sum(1 for r in enriched_rows if r["n_references"] > 0)
    n_with_abstract = sum(1 for r in enriched_rows if r["abstract_enriched"])
    refs_per_article = [r["n_references"] for r in enriched_rows if r["n_references"] > 0]
    avg_refs = sum(refs_per_article) / len(refs_per_article) if refs_per_article else 0
    med_refs = sorted(refs_per_article)[len(refs_per_article)//2] if refs_per_article else 0

    report = f"""{'='*60}
ENRIQUECIMENTO DO ANEL NUCLEAR VIA OPENALEX
{'='*60}
Artigos nucleares:                  {len(df):>7,}
Com DOI ou OpenAlex ID:             {len(queryable):>7,}
Encontrados no OpenAlex:            {n_found:>7,}
Com referências (referenced_works): {n_with_refs:>7,}
Com abstract recuperado:            {n_with_abstract:>7,}

Referências por artigo (dos que têm):
  Média:                            {avg_refs:>7.1f}
  Mediana:                          {med_refs:>7,}

Total de referências (linhas):      {len(all_ref_rows):>7,}
Works citados (únicos):             {len(all_cited_ids):>7,}
Metadados de citados recuperados:   {len(cited_metadata):>7,}
Pares de co-citação:                {len(cocitation_rows):>7,}

Cobertura:
  OpenAlex:    {n_found}/{len(df)} ({n_found/len(df)*100:.1f}%)
  Referências: {n_with_refs}/{len(df)} ({n_with_refs/len(df)*100:.1f}%)
  Abstracts:   {n_with_abstract}/{len(df)} ({n_with_abstract/len(df)*100:.1f}%)

Arquivos salvos:
  Referências:     {OUTPUT_REFS}
  Enriquecido:     {OUTPUT_ENRICHED}
  Co-citação:      {OUTPUT_COCITATION}
"""

    print(report)
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    # Top co-citações
    if len(df_cocit) > 0:
        print("Top 20 pares de co-citação (por peso):")
        top_cocit = df_cocit.head(20)
        for _, row in top_cocit.iterrows():
            src = row["source"]
            tgt = row["target"]
            w = row["weight"]
            src_meta = cited_metadata.get(src, {})
            tgt_meta = cited_metadata.get(tgt, {})
            src_label = src_meta.get("ref_first_author", src)[:25]
            tgt_label = tgt_meta.get("ref_first_author", tgt)[:25]
            src_year = src_meta.get("ref_year", "")
            tgt_year = tgt_meta.get("ref_year", "")
            print(f"  [{w:>2}] {src_label} ({src_year}) <-> {tgt_label} ({tgt_year})")


if __name__ == "__main__":
    main()
