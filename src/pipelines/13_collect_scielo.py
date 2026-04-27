"""
13_collect_scielo.py (v3 — ArticleMeta API)
===========================================
Coleta registros do SciELO via ArticleMeta API (sem SciELO Search / sem OAI).

Estratégia:
  - Obtém ISSNs via /journal/?collection=scl
  - Para cada ISSN, obtém PIDs via /article/identifiers/?collection=scl&issn=...
  - Para cada PID, busca metadados via /article/?code=...
  - Filtra por termos (nuclear + estendido) em título/resumo
  - Exporta data/raw/scielo_results.csv no padrão do pipeline

Uso (teste rápido com 1 periódico):
  python src/pipelines/13_collect_scielo.py --issn 1676-5648 --max-articles 50

Uso (rodar em vários periódicos, com limite de journals):
  python src/pipelines/13_collect_scielo.py --max-journals 50 --max-articles 200

Saída:
  data/raw/scielo_results.csv
"""

from __future__ import annotations

from pathlib import Path
import argparse
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = RAW_DIR / "scielo_results.csv"

ARTICLEMETA_BASE = "http://articlemeta.scielo.org/api/v1"

# ── Strings de busca ────────────────────────────────────────────────────────
QUERY_PACK_NUCLEAR = [
    '"política judiciária"',
    '"políticas judiciárias"',
    '"política judicial"',
    '"políticas judiciales"',
    '"judicial policy"',
    '"judicial policies"',
]

QUERY_PACK_EXTENDED = [
    '"governança judicial"',
    '"administração judiciária"',
    '"reforma judicial"',
    '"reforma do judiciário"',
    '"gestão judicial"',
    '"gestão de tribunais"',
    '"Conselho Nacional de Justiça"',
    '"judicial governance"',
    '"judicial administration"',
    '"court administration"',
    '"judicial reform"',
]

# regex DOI (exige barra, para evitar capturar datas)
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)


def norm_query(q: str) -> str:
    return q.replace('"', "").strip().lower()


QUERY_TERMS: List[Tuple[str, str]] = [(q, norm_query(q)) for q in (QUERY_PACK_NUCLEAR + QUERY_PACK_EXTENDED)]


def _get(session: requests.Session, url: str, params: Dict[str, Any], timeout: int = 40, retries: int = 3) -> Any:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"Falha em GET {url} params={params}. Último erro: {last_err}")


def pick_lang_value(items: Any, prefer=("pt", "en", "es")) -> Tuple[str, str]:
    """
    items: lista de dicts com chaves: l (lang), _ (texto)
    Retorna (texto, lang).
    """
    if not isinstance(items, list):
        return ("", "")
    bucket = {d.get("l"): d.get("_", "") for d in items if isinstance(d, dict)}
    for lang in prefer:
        val = bucket.get(lang)
        if isinstance(val, str) and val.strip():
            return (val.strip(), lang)
    # fallback: primeiro não-vazio
    for d in items:
        if isinstance(d, dict):
            val = d.get("_")
            if isinstance(val, str) and val.strip():
                return (val.strip(), d.get("l", "") or "")
    return ("", "")


def pick_abstract(v83: Any, prefer=("pt", "en", "es")) -> Tuple[str, str]:
    """
    v83: lista de dicts com chaves: l (lang), a (texto)
    Retorna (texto, lang).
    """
    if not isinstance(v83, list):
        return ("", "")
    bucket = {d.get("l"): d.get("a", "") for d in v83 if isinstance(d, dict)}
    for lang in prefer:
        val = bucket.get(lang)
        if isinstance(val, str) and val.strip():
            return (val.strip(), lang)
    for d in v83:
        if isinstance(d, dict):
            val = d.get("a")
            if isinstance(val, str) and val.strip():
                return (val.strip(), d.get("l", "") or "")
    return ("", "")


def extract_authors(v10: Any) -> str:
    """
    v10: lista de dicts com 'n' (nome) e 's' (sobrenome)
    """
    if not isinstance(v10, list):
        return ""
    names = []
    for a in v10:
        if not isinstance(a, dict):
            continue
        given = a.get("n", "") or ""
        sur = a.get("s", "") or ""
        full = f"{given} {sur}".strip()
        if full:
            names.append(full)
    return "; ".join(names)


def extract_journal(v30: Any) -> str:
    """
    v30: lista de dicts com '_' (título abreviado do periódico)
    """
    if not isinstance(v30, list) or not v30:
        return ""
    for d in v30:
        if isinstance(d, dict):
            val = d.get("_")
            if isinstance(val, str) and val.strip():
                return val.strip()
    return ""


def extract_url(fulltexts: Any) -> str:
    """
    fulltexts: dict como {'html': {'pt': 'http://...'}, 'pdf': {...}}
    Vamos preferir html pt/en/es; fallback primeiro link encontrado.
    """
    if not isinstance(fulltexts, dict):
        return ""
    html = fulltexts.get("html")
    if isinstance(html, dict):
        for lang in ("pt", "en", "es"):
            u = html.get(lang)
            if isinstance(u, str) and u.strip():
                return u.strip()
        # fallback: qualquer html
        for _, u in html.items():
            if isinstance(u, str) and u.strip():
                return u.strip()

    # fallback geral: primeiro string em qualquer nível
    def walk(x):
        if isinstance(x, str) and x.strip():
            return x.strip()
        if isinstance(x, dict):
            for v in x.values():
                out = walk(v)
                if out:
                    return out
        return ""
    return walk(fulltexts)


def extract_doi(data: Dict[str, Any]) -> str:
    doi = data.get("doi")
    if isinstance(doi, str) and doi.strip():
        return doi.strip()

    # fallback: varrer strings no payload por DOI_RE
    def walk(x):
        if isinstance(x, str):
            m = DOI_RE.search(x)
            if m:
                return m.group(0).rstrip(").,;")
        elif isinstance(x, list):
            for v in x:
                out = walk(v)
                if out:
                    return out
        elif isinstance(x, dict):
            for v in x.values():
                out = walk(v)
                if out:
                    return out
        return ""
    return walk(data) or ""


def matches_queries(title: str, abstract: str) -> Optional[str]:
    hay = f"{title} {abstract}".lower()
    for original, qnorm in QUERY_TERMS:
        if qnorm and qnorm in hay:
            return original
    return None


def list_journals(session: requests.Session, collection: str) -> List[str]:
    url = f"{ARTICLEMETA_BASE}/journal/"
    data = _get(session, url, {"collection": collection, "format": "json"})
    issns = []
    if isinstance(data, list):
        for j in data:
            if isinstance(j, dict):
                for i in j.get("issns", []) or []:
                    if isinstance(i, str) and i.strip():
                        issns.append(i.strip())
    # dedup preservando ordem
    seen = set()
    out = []
    for i in issns:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def list_article_codes(session: requests.Session, collection: str, issn: str, limit: int = 1000, max_articles: int = 0) -> List[str]:
    url = f"{ARTICLEMETA_BASE}/article/identifiers/"
    codes: List[str] = []
    offset = 0
    while True:
        payload = _get(session, url, {"collection": collection, "issn": issn, "limit": limit, "offset": offset})
        objs = payload.get("objects", []) if isinstance(payload, dict) else []
        if not objs:
            break
        for o in objs:
            if isinstance(o, dict):
                c = o.get("code")
                if isinstance(c, str) and c.strip():
                    codes.append(c.strip())
                    if max_articles and len(codes) >= max_articles:
                        return codes
        offset += limit
        # segurança: se total existir e já passou
        meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
        total = (meta.get("total") if isinstance(meta, dict) else None)
        if isinstance(total, int) and offset >= total:
            break
    return codes


def fetch_article(session: requests.Session, code: str) -> Dict[str, Any]:
    url = f"{ARTICLEMETA_BASE}/article/"
    data = _get(session, url, {"code": code, "format": "json"})
    if not isinstance(data, dict):
        return {}
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", default="scl")
    ap.add_argument("--issn", action="append", default=[], help="Pode repetir: --issn 1676-5648 --issn 0102-311X")
    ap.add_argument("--max-journals", type=int, default=0, help="Limite de periódicos quando não usar --issn")
    ap.add_argument("--max-articles", type=int, default=0, help="Limite de artigos por ISSN (0 = sem limite)")
    ap.add_argument("--sleep", type=float, default=0.3, help="Sleep entre requisições (segundos)")
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Public_Policy bibliometric study (ArticleMeta client)",
        "Accept": "application/json",
    })

    if args.issn:
        issns = args.issn
    else:
        print("Listando periódicos via /journal/ ...")
        issns = list_journals(session, args.collection)
        if args.max_journals:
            issns = issns[:args.max_journals]

    print(f"ISSNs selecionados: {len(issns)}")

    rows = []
    for idx, issn in enumerate(issns, 1):
        print(f"\n[{idx}/{len(issns)}] ISSN {issn}: listando article codes ...")
        codes = list_article_codes(session, args.collection, issn, limit=1000, max_articles=args.max_articles)
        print(f"  codes encontrados: {len(codes)}")

        for j, code in enumerate(codes, 1):
            data = fetch_article(session, code)
            if not data:
                continue

            article = data.get("article", {}) or {}
            title, title_lang = pick_lang_value(article.get("v12", []))
            abstract, abs_lang = pick_abstract(article.get("v83", []))

            # filtrar por queries
            qmatch = matches_queries(title, abstract)
            if not qmatch:
                time.sleep(args.sleep)
                continue

            journal = extract_journal(article.get("v30", []))
            authors = extract_authors(article.get("v10", []))
            year = data.get("publication_year")
            year = str(year).strip() if year is not None else ""

            doi = extract_doi(data)
            url = extract_url(data.get("fulltexts"))

            language = title_lang or abs_lang or ""

            rows.append({
                "query_term": qmatch,
                "source": "scielo",
                "source_id": code,
                "title": title,
                "doi": doi,
                "publication_year": year,
                "journal": journal,
                "type": data.get("document_type", "article") or "article",
                "language": language,
                "cited_by_count": 0,
                "authors": authors,
                "abstract": (abstract or "")[:500],
                "url": url,
            })

            if j % 50 == 0:
                print(f"    processados {j}/{len(codes)}; matches acumulados={len(rows)}")

            time.sleep(args.sleep)

    df = pd.DataFrame(rows)
    
    if df.empty:
        print("\nNenhum match encontrado para as queries definidas.")
        out_cols = [
            "query_term","source","source_id","title","doi","publication_year","journal",
            "type","language","cited_by_count","authors","abstract","url"
        ]
        pd.DataFrame(columns=out_cols).to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"Arquivo vazio (com cabeçalho) salvo em: {OUTPUT_FILE}")
        return

    # dedup interno básico
    df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
    df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()
    df["journal_norm"] = df["journal"].fillna("").astype(str).str.strip().str.lower()

    with_doi = df[df["doi_norm"] != ""].drop_duplicates(subset=["doi_norm"], keep="first")
    without_doi = df[df["doi_norm"] == ""].drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"], keep="first"
    )
    out = pd.concat([with_doi, without_doi], ignore_index=True)

    out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print("RESULTADO — SCIELO (ArticleMeta)")
    print("=" * 60)
    print(f"Matches brutos: {len(df)}")
    print(f"Após dedup:     {len(out)}")
    print(f"Salvo em:       {OUTPUT_FILE}")
    print("\nTop queries:")
    print(out["query_term"].value_counts().head(10).to_string())
    print("\nTop periódicos:")
    print(out["journal"].fillna("N/D").value_counts().head(10).to_string())


if __name__ == "__main__":
    main()