from pathlib import Path
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("SCOPUS_API_KEY", "").strip()

QUERY_PACK = [
    'TITLE-ABS-KEY("judicial policy") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("judicial policies") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("judicial governance") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("judicial administration") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("court administration") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("court governance") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("judicial reform") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("judicial review") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
    'TITLE-ABS-KEY("access to justice") AND PUBYEAR > 1999 AND PUBYEAR < 2027',
]

COUNT_PER_PAGE = 25
MAX_PAGES_PER_QUERY = 4


def fetch_scopus(query: str) -> list[dict]:
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json",
    }

    url = "https://api.elsevier.com/content/search/scopus"
    rows = []

    for page in range(MAX_PAGES_PER_QUERY):
        start = page * COUNT_PER_PAGE
        params = {
            "query": query,
            "count": COUNT_PER_PAGE,
            "start": start,
        }

        response = requests.get(url, headers=headers, params=params, timeout=60)
        print(f"Status: {response.status_code} | start={start}")

        if response.status_code != 200:
            print("Resposta de erro:")
            print(response.text[:2000])
            response.raise_for_status()

        payload = response.json()
        entries = payload.get("search-results", {}).get("entry", [])

        if not entries:
            break

        for item in entries:
            rows.append(
                {
                    "source": "scopus",
                    "query_term": query,
                    "title": item.get("dc:title", ""),
                    "doi": item.get("prism:doi", ""),
                    "publication_year": item.get("prism:coverDate", "")[:4],
                    "journal": item.get("prism:publicationName", ""),
                    "type": item.get("subtypeDescription", ""),
                    "language": item.get("language", ""),
                    "cited_by_count": item.get("citedby-count", 0),
                    "scopus_id": item.get("dc:identifier", ""),
                }
            )

        time.sleep(1)

    return rows


def main():
    if not API_KEY:
        raise RuntimeError("SCOPUS_API_KEY não encontrada no .env")

    all_rows = []

    for query in QUERY_PACK:
        print(f"\nBuscando Scopus | query={query}")
        try:
            rows = fetch_scopus(query)
            print(f"  -> {len(rows)} registros coletados")
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
    df["publication_year"] = df["publication_year"].fillna("").astype(str).str.strip()
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)

    df = df.sort_values("cited_by_count", ascending=False)

    if "scopus_id" in df.columns:
        df = df.drop_duplicates(subset=["scopus_id"], keep="first")

    df_with_doi = df[df["doi_norm"] != ""].copy()
    df_without_doi = df[df["doi_norm"] == ""].copy()

    df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
    df_without_doi = df_without_doi.drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"],
        keep="first",
    )

    df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)

    output_csv = RAW_DIR / "scopus_results.csv"
    df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\nArquivo salvo em: {output_csv}")
    print(f"Total final após deduplicação: {len(df_final)}")


if __name__ == "__main__":
    main()