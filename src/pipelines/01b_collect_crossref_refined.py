from pathlib import Path
import os
import time
import html
import re

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

EMAIL = os.getenv("EMAIL_POLITE", "").strip()

YEAR_START = 2000
YEAR_END = 2026
ROWS_PER_QUERY = 100

QUERY_PACK = [
    '"judicial policy"',
    '"judicial policies"',
    '"judicial governance"',
    '"judicial administration"',
    '"court administration"',
    '"court governance"',
    '"judicial reform"',
    '"política judiciária"',
    '"políticas judiciárias"',
    '"governança judicial"',
    '"administração judiciária"',
    '"reforma do judiciário"',
    '"reforma judicial"',
    '"Conselho Nacional de Justiça"',
]

ANCHORS = [
    "judicial",
    "judiciary",
    "court",
    "courts",
    "tribunal",
    "tribunais",
    "judiciário",
    "judiciária",
    "judiciarias",
    "governança judicial",
    "administração judiciária",
    "conselho nacional de justiça",
]

BAD_SOURCES = [
    "ssrn",
    "zenodo",
    "dialnet",
    "la referencia",
    "choice reviews",
]

BAD_TITLE_HINTS = [
    "nursing",
    "chemistry",
    "lepidopter",
    "polymer",
]

def clean_text(value) -> str:
    if value is None:
        return ""
    text = str(value)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_text(value) -> str:
    return clean_text(value).lower()

def extract_year(item: dict):
    published = item.get("published-print") or item.get("published-online") or item.get("created") or {}
    parts = published.get("date-parts", [])
    if parts and parts[0]:
        return parts[0][0]
    return None

def is_relevant(title: str, journal: str) -> bool:
    text = f"{normalize_text(title)} {normalize_text(journal)}"
    has_anchor = any(anchor in text for anchor in ANCHORS)
    bad_source = any(bad in normalize_text(journal) for bad in BAD_SOURCES)
    bad_title = any(bad in normalize_text(title) for bad in BAD_TITLE_HINTS)
    return has_anchor and not bad_source and not bad_title

def fetch_crossref(query: str) -> list[dict]:
    url = "https://api.crossref.org/works"

    params = {
        "query.bibliographic": query,
        "rows": ROWS_PER_QUERY,
        "filter": f"from-pub-date:{YEAR_START}-01-01,until-pub-date:{YEAR_END}-12-31,type:journal-article",
    }

    if EMAIL:
        params["mailto"] = EMAIL

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    items = response.json().get("message", {}).get("items", [])
    rows = []

    for item in items:
        title_list = item.get("title", [])
        journal_list = item.get("container-title", [])

        title = clean_text(title_list[0] if title_list else "")
        journal = clean_text(journal_list[0] if journal_list else "")

        if not is_relevant(title, journal):
            continue

        year = extract_year(item)
        authors = item.get("author", []) or []
        author_names = []
        for a in authors:
            given = clean_text(a.get("given", ""))
            family = clean_text(a.get("family", ""))
            full = f"{given} {family}".strip()
            if full:
                author_names.append(full)

        rows.append(
            {
                "query_term": query,
                "source": "crossref",
                "crossref_doi": item.get("DOI", ""),
                "title": title,
                "doi": item.get("DOI", ""),
                "publication_year": year,
                "journal": journal,
                "type": item.get("type", ""),
                "language": item.get("language", ""),
                "cited_by_count": item.get("is-referenced-by-count", 0),
                "authors": "; ".join(author_names),
                "url": item.get("URL", ""),
            }
        )

    time.sleep(1)
    return rows

def main():
    all_rows = []

    for query in QUERY_PACK:
        print(f"Buscando Crossref | query={query}")
        try:
            rows = fetch_crossref(query)
            print(f"  -> {len(rows)} registros mantidos")
            all_rows.extend(rows)
        except Exception as e:
            print(f"  ERRO | {query} | {e}")

    if not all_rows:
        print("Nenhum registro coletado.")
        return

    df = pd.DataFrame(all_rows)

    df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
    df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()
    df["journal_norm"] = df["journal"].fillna("").astype(str).str.strip().str.lower()

    df = df.sort_values("cited_by_count", ascending=False)

    df_with_doi = df[df["doi_norm"] != ""].copy()
    df_without_doi = df[df["doi_norm"] == ""].copy()

    df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
    df_without_doi = df_without_doi.drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"],
        keep="first",
    )

    df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)

    output_csv = RAW_DIR / "crossref_results_refined.csv"
    df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\nArquivo salvo em: {output_csv}")
    print(f"Total final após filtro e deduplicação: {len(df_final)}")

if __name__ == "__main__":
    main()