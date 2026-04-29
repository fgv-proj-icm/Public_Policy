"""
19_enrich_metadata.py
=====================
Enriquecimento de metadados via OpenAlex para o corpus final.

Preenche campos faltantes (abstract, language, authors) buscando cada DOI
no OpenAlex. Usa cache local em data/cache/openalex_metadata.jsonl para
evitar requisições repetidas. Não altera o corpus congelado — aplica o
enriquecimento em data/final/corpus_complete.csv.

Saídas:
  - data/final/corpus_complete_enriched.csv
  - outputs/tables/metadata_coverage_before_after.csv
  - logs/enrichment.log

Uso:
    python src/pipelines/19_enrich_metadata.py --force-online
    python src/pipelines/19_enrich_metadata.py --limit 50  (teste rápido)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src"))
from utils.normalize import normalize_doi

# ── Paths ────────────────────────────────────────────────────────────────────
CACHE_DIR = BASE_DIR / "data" / "cache"
CACHE_FILE = CACHE_DIR / "openalex_metadata.jsonl"
FINAL_DIR = BASE_DIR / "data" / "final"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_TABLES = BASE_DIR / "outputs" / "tables"

INPUT_CORPUS = FINAL_DIR / "corpus_complete.csv"
OUTPUT_CORPUS = FINAL_DIR / "corpus_complete_enriched.csv"
OUTPUT_COVERAGE = OUTPUT_TABLES / "metadata_coverage_before_after.csv"
LOG_FILE = LOGS_DIR / "enrichment.log"

OPENALEX_API = "https://api.openalex.org/works"
RATE_LIMIT_DELAY = 0.12   # ~8 req/s (generoso p/ modo cortês)
REQUEST_TIMEOUT = 20

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ── Cache ─────────────────────────────────────────────────────────────────────

def _load_cache() -> dict[str, dict]:
    if not CACHE_FILE.exists():
        return {}
    cache: dict[str, dict] = {}
    with CACHE_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    cache[obj["_doi"]] = obj
                except (json.JSONDecodeError, KeyError):
                    pass
    return cache


def _save_to_cache(doi: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    record = {"_doi": doi, "_cached_at": datetime.now(timezone.utc).isoformat(), **data}
    with CACHE_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── OpenAlex fetch ─────────────────────────────────────────────────────────────

def _decode_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return ""
    try:
        pairs = [(word, pos) for word, positions in inverted_index.items() for pos in positions]
        pairs.sort(key=lambda x: x[1])
        return " ".join(word for word, _ in pairs)
    except Exception:
        return ""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
    before_sleep=before_sleep_log(log, logging.WARNING),
    reraise=False,
)
def _fetch_openalex(doi: str, email: str) -> dict | None:
    url = f"{OPENALEX_API}/doi:{doi}"
    params: dict = {}
    if email:
        params["mailto"] = email
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        log.warning("HTTP %s para DOI %s", e.response.status_code, doi)
        return None


def fetch_with_cache(doi: str, cache: dict, email: str) -> dict | None:
    doi_n = normalize_doi(doi)
    if not doi_n:
        return None
    if doi_n in cache:
        return cache[doi_n]
    data = _fetch_openalex(doi_n, email)
    payload = data if data is not None else {"_not_found": True}
    _save_to_cache(doi_n, payload)
    cache[doi_n] = payload
    time.sleep(RATE_LIMIT_DELAY)
    return data


# ── Metadata extraction ────────────────────────────────────────────────────────

def extract_fields(data: dict) -> dict:
    if not data or data.get("_not_found"):
        return {}

    abstract = _decode_abstract(data.get("abstract_inverted_index"))
    language = data.get("language", "")

    raw_authors = data.get("authorships", [])
    authors_list = [
        a.get("author", {}).get("display_name", "")
        for a in raw_authors
        if a.get("author", {}).get("display_name")
    ]
    authors = "; ".join(authors_list)

    return {
        "abstract": abstract or "",
        "language": language or "",
        "authors": authors or "",
    }


# ── Coverage ───────────────────────────────────────────────────────────────────

def _coverage(df: pd.DataFrame, label: str) -> list[dict]:
    rows = []
    for field in ["abstract", "language", "authors", "doi"]:
        if field not in df.columns:
            present = 0
        else:
            present = df[field].apply(
                lambda v: str(v).strip().lower() not in ("", "nan", "none", "na", "null", "n/d")
            ).sum()
        rows.append({
            "corpus": label,
            "campo": field,
            "total": len(df),
            "preenchidos": int(present),
            "faltantes": len(df) - int(present),
            "pct": round(present / len(df) * 100, 1) if len(df) else 0.0,
        })
    return rows


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-online", action="store_true",
                        help="Executa mesmo com offline=true no config.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limitar a N registros (útil para teste).")
    args = parser.parse_args()

    # Verificar modo offline
    try:
        import yaml
        cfg = yaml.safe_load((BASE_DIR / "config.yml").read_text(encoding="utf-8")) or {}
        offline = cfg.get("offline", True)
        email = cfg.get("email_polite", "")
    except Exception:
        offline = True
        email = ""

    if offline and not args.force_online:
        print("Modo offline ativo. Use --force-online para executar o enriquecimento.")
        print("Exemplo: python src/pipelines/19_enrich_metadata.py --force-online")
        sys.exit(0)

    # Tentar obter email do .env
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv(BASE_DIR / ".env")
        email = os.getenv("EMAIL_POLITE", email)
    except ImportError:
        pass

    if not INPUT_CORPUS.exists():
        print(f"ERRO: corpus não encontrado em {INPUT_CORPUS}")
        print("Execute primeiro: make pipeline")
        sys.exit(1)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    log.info("Carregando corpus: %s", INPUT_CORPUS)
    df = pd.read_csv(INPUT_CORPUS, dtype=str)
    if args.limit > 0:
        df = df.head(args.limit)
        log.info("Modo teste: limitado a %d registros", args.limit)

    log.info("Total de registros: %d", len(df))

    # Cobertura ANTES
    coverage_before = _coverage(df, "antes_enrichment")

    # Carregar cache
    cache = _load_cache()
    log.info("Cache carregado: %d entradas", len(cache))

    # Enriquecer
    enriched_count = 0
    skipped_no_doi = 0
    skipped_cached_not_found = 0

    def _is_empty(val: str) -> bool:
        return str(val).strip().lower() in ("", "nan", "none", "na", "null", "n/d")

    for idx, row in df.iterrows():
        doi = str(row.get("doi", "")).strip()
        if not doi or _is_empty(doi):
            skipped_no_doi += 1
            continue

        # Só busca se algum campo alvo está faltando
        needs_enrichment = any(
            _is_empty(row.get(f, ""))
            for f in ["abstract", "language", "authors"]
        )
        if not needs_enrichment:
            continue

        data = fetch_with_cache(doi, cache, email)
        if data is None or data.get("_not_found"):
            skipped_cached_not_found += 1
            continue

        fields = extract_fields(data)
        changed = False
        for field, value in fields.items():
            if value and _is_empty(row.get(field, "")):
                df.at[idx, field] = value
                changed = True

        if changed:
            enriched_count += 1
            log.info("Enriquecido: %s", doi[:60])

    log.info(
        "Enriquecimento concluído: %d registros atualizados, %d sem DOI, %d não encontrados",
        enriched_count, skipped_no_doi, skipped_cached_not_found,
    )

    # Salvar corpus enriquecido
    df.to_csv(OUTPUT_CORPUS, index=False, encoding="utf-8-sig")
    log.info("Corpus enriquecido salvo: %s", OUTPUT_CORPUS)

    # Cobertura DEPOIS
    coverage_after = _coverage(df, "depois_enrichment")

    # Relatório de cobertura
    cov_rows = []
    before_map = {(r["corpus"], r["campo"]): r for r in coverage_before}
    for r in coverage_after:
        key = ("antes_enrichment", r["campo"])
        before = before_map.get(key, {})
        cov_rows.append({
            "campo": r["campo"],
            "total": r["total"],
            "antes_preenchidos": before.get("preenchidos", 0),
            "antes_pct": before.get("pct", 0.0),
            "depois_preenchidos": r["preenchidos"],
            "depois_pct": r["pct"],
            "ganho_registros": r["preenchidos"] - before.get("preenchidos", 0),
        })

    pd.DataFrame(cov_rows).to_csv(OUTPUT_COVERAGE, index=False, encoding="utf-8-sig")
    log.info("Cobertura before/after: %s", OUTPUT_COVERAGE)

    print(f"\n{'='*60}")
    print("ENRIQUECIMENTO DE METADADOS — RESUMO")
    print(f"{'='*60}")
    print(pd.DataFrame(cov_rows).to_string(index=False))
    print(f"\nLog: {LOG_FILE}")
    print(f"Corpus enriquecido: {OUTPUT_CORPUS}")
    print(f"Cobertura: {OUTPUT_COVERAGE}")


if __name__ == "__main__":
    main()
