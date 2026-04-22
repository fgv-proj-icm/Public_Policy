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

API_KEY = os.getenv("OPENALEX_API_KEY", "").strip()

YEAR_START = 2000
YEAR_END = 2026
PER_PAGE = 25
MAX_PAGES_PER_QUERY_YEAR = 2

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
    "administração judiciária",
    "governança judicial",
    "conselho nacional de justiça",
]

BAD_SOURCES = [
    "ssrn",
    "zenodo",
    "la referencia",
    "dialnet",
    "choice reviews",
    "eyls",
    "institutional digital library",
]

def build_params(query: str, year: int, page: int) -> dict:
    params = {
        "search": query,
        "filter": f"publication_year:{year},type:article|review,language:en|pt|es",
        "per-page": PER_PAGE,
        "page": page,
        "select": ",".join(
            [
                "id",
                "display_name",
                "doi",
                "publication_year",
                "type",
                "language",
                "cited_by_count",
                "primary_location",
                "authorships",
                "concepts",
            ]
        ),
    }

    if API_KEY:
        params["api_key"] = API_KEY

    return params


def normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def is_relevant(title: str, journal: str, concepts: list[str]) -> bool:
    text = " ".join(
        [
            normalize_text(title),
            normalize_text(journal),
            normalize_text(" ".join(concepts)),
        ]
    )

    has_anchor = any(anchor in text for anchor in ANCHORS)
    bad_source = any(bad in normalize_text(journal) for bad in BAD_SOURCES)

    return has_anchor and not bad_source


def fetch_openalex(query: str, year: int) -> list[dict]:
    url = "https://api.openalex.org/works"
    rows = []

    for page in range(1, MAX_PAGES_PER_QUERY_YEAR + 1):
        params = build_params(query, year, page)
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 401:
            raise RuntimeError("OpenAlex retornou 401. Verifique OPENALEX_API_KEY no .env.")

        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            break

        for item in results:
            source = (item.get("primary_location") or {}).get("source") or {}

            institutions = []
            for auth in item.get("authorships", []) or []:
                for inst in auth.get("institutions", []) or []:
                    name = inst.get("display_name")
                    if name and name not in institutions:
                        institutions.append(name)

            concepts = []
            for concept in item.get("concepts", []) or []:
                name = concept.get("display_name")
                if name:
                    concepts.append(name)

            title = item.get("display_name", "")
            journal = source.get("display_name", "")

            if not is_relevant(title, journal, concepts):
                continue

            rows.append(
                {
                    "query_term": query,
                    "year_query": year,
                    "source": "openalex",
                    "openalex_id": item.get("id", ""),
                    "title": title,
                    "doi": item.get("doi", ""),
                    "publication_year": item.get("publication_year"),
                    "journal": journal,
                    "type": item.get("type", ""),
                    "language": item.get("language", ""),
                    "cited_by_count": item.get("cited_by_count", 0),
                    "institutions": "; ".join(institutions),
                    "concepts": "; ".join(concepts),
                }
            )

        time.sleep(1)

    return rows


def main() -> None:
    if not API_KEY:
        raise RuntimeError("OPENALEX_API_KEY não encontrada no .env")

    all_rows = []

    for query in QUERY_PACK:
        for year in range(YEAR_START, YEAR_END + 1):
            print(f"Buscando | ano={year} | query={query}")
            try:
                rows = fetch_openalex(query, year)
                print(f"  -> {len(rows)} registros mantidos")
                all_rows.extend(rows)
            except Exception as e:
                print(f"  ERRO | ano={year} | query={query} | {e}")

    if not all_rows:
        print("Nenhum registro coletado.")
        return

    df = pd.DataFrame(all_rows)

    df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
    df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()

    df = df.sort_values("cited_by_count", ascending=False)

    df = df.drop_duplicates(subset=["openalex_id"], keep="first")

    df_with_doi = df[df["doi_norm"] != ""].copy()
    df_without_doi = df[df["doi_norm"] == ""].copy()

    df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
    df_without_doi = df_without_doi.drop_duplicates(subset=["title_norm", "publication_year", "journal"], keep="first")

    df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)

    output_csv = RAW_DIR / "openalex_results_refined.csv"
    df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\nArquivo salvo em: {output_csv}")
    print(f"Total final após filtro e deduplicação: {len(df_final)}")


if __name__ == "__main__":
    main()