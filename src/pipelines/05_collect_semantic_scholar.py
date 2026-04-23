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

API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()

QUERY_PACK = [
    '"judicial policy"',
    '"judicial policies"',
    '"judicial governance"',
    '"judicial administration"',
    '"court administration"',
    '"court governance"',
    '"judicial reform"',
    '"judicial review"',
    '"access to justice"',
]

FIELDS = ",".join([
    "title",
    "year",
    "abstract",
    "citationCount",
    "url",
    "venue",
    "publicationTypes",
    "publicationDate",
    "externalIds",
    "authors",
])

YEAR_FILTER = "2000-"
SORT = "citationCount:desc"
MAX_PAGES_PER_QUERY = 4


def fetch_semantic_scholar(query: str) -> list[dict]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    headers = {"x-api-key": API_KEY}
    rows = []

    token = None
    pages = 0

    while pages < MAX_PAGES_PER_QUERY:
        params = {
            "query": query,
            "fields": FIELDS,
            "year": YEAR_FILTER,
            "sort": SORT,
        }
        if token:
            params["token"] = token

        response = requests.get(url, params=params, headers=headers, timeout=60)

        print(f"Status: {response.status_code} | token={'SIM' if token else 'NAO'}")

        if response.status_code != 200:
            print("Resposta de erro:")
            print(response.text[:2000])
            response.raise_for_status()

        payload = response.json()
        data = payload.get("data", [])

        if not data:
            break

        for item in data:
            external_ids = item.get("externalIds") or {}
            authors = item.get("authors") or []
            author_names = []
            for author in authors:
                name = author.get("name", "")
                if name:
                    author_names.append(name)

            publication_types = item.get("publicationTypes") or []

            rows.append(
                {
                    "source": "semantic_scholar",
                    "query_term": query,
                    "paper_id": item.get("paperId", ""),
                    "title": item.get("title", ""),
                    "doi": external_ids.get("DOI", ""),
                    "publication_year": item.get("year", ""),
                    "journal": item.get("venue", ""),
                    "type": "; ".join(publication_types),
                    "citation_count": item.get("citationCount", 0),
                    "authors": "; ".join(author_names),
                    "url": item.get("url", ""),
                    "abstract": item.get("abstract", ""),
                    "publication_date": item.get("publicationDate", ""),
                }
            )

        token = payload.get("token")
        pages += 1

        if not token:
            break

        time.sleep(1.1)  # respeita 1 RPS

    return rows


def main():
    if not API_KEY:
        raise RuntimeError("SEMANTIC_SCHOLAR_API_KEY não encontrada no .env")

    all_rows = []

    for query in QUERY_PACK:
        print(f"\nBuscando Semantic Scholar | query={query}")
        try:
            rows = fetch_semantic_scholar(query)
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
    df["citation_count"] = pd.to_numeric(df["citation_count"], errors="coerce").fillna(0)

    df = df.sort_values("citation_count", ascending=False)

    if "paper_id" in df.columns:
        df = df.drop_duplicates(subset=["paper_id"], keep="first")

    df_with_doi = df[df["doi_norm"] != ""].copy()
    df_without_doi = df[df["doi_norm"] == ""].copy()

    df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
    df_without_doi = df_without_doi.drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"],
        keep="first",
    )

    df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)

    output_csv = RAW_DIR / "semantic_scholar_results.csv"
    df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\nArquivo salvo em: {output_csv}")
    print(f"Total final após deduplicação: {len(df_final)}")


if __name__ == "__main__":
    main()