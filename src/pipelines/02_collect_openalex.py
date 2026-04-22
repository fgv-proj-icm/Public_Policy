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

# Use 2000-2026 se quiser seguir o funil metodológico mais estrito das orientações
YEAR_START = 2000
YEAR_END = 2026

QUERY_PACK = [
    '"política judiciária" OR "políticas judiciárias"',
    '"governança judicial" OR "administração judicial"',
    '"reforma do judiciário" OR "reforma judicial"',
    '"Conselho Nacional de Justiça" OR CNJ',
    '"políticas públicas" AND (judiciário OR judicial OR justiça)',
    '"judicial policy" OR "judicial policies"',
    '"judicial governance" OR "judicial administration"',
    '"court administration" OR "court governance"',
    '"judicial reform"',
    '"public policy" AND (judiciary OR courts OR judicial)',
]

# Rode depois, como reforço de Brasil
QUERY_PACK_BR = [
    '(Brasil OR Brazil OR brasileiro* OR brasileira*) AND ("política judiciária" OR "judicial policy")',
    '(STF OR "Supremo Tribunal Federal" OR "Justiça Federal" OR "Justiça Estadual") AND (política* OR governança OR gestão)',
]

USE_BR_SUBPACK = False
PER_PAGE = 25
MAX_PAGES_PER_QUERY_YEAR = 2


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


def fetch_openalex(query: str, year: int) -> list[dict]:
    url = "https://api.openalex.org/works"
    rows = []

    for page in range(1, MAX_PAGES_PER_QUERY_YEAR + 1):
        params = build_params(query, year, page)
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 401:
            raise RuntimeError(
                "OpenAlex retornou 401. Verifique se OPENALEX_API_KEY no .env está correta."
            )

        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            break

        for item in results:
            source = (item.get("primary_location") or {}).get("source") or {}

            authorships = item.get("authorships", []) or []
            institutions = []
            for auth in authorships:
                for inst in auth.get("institutions", []) or []:
                    name = inst.get("display_name")
                    if name and name not in institutions:
                        institutions.append(name)

            concepts = []
            for concept in item.get("concepts", []) or []:
                name = concept.get("display_name")
                if name:
                    concepts.append(name)

            rows.append(
                {
                    "query_term": query,
                    "year_query": year,
                    "source": "openalex",
                    "openalex_id": item.get("id", ""),
                    "title": item.get("display_name", ""),
                    "doi": item.get("doi", ""),
                    "publication_year": item.get("publication_year"),
                    "journal": source.get("display_name", ""),
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

    query_pack = QUERY_PACK + (QUERY_PACK_BR if USE_BR_SUBPACK else [])

    all_rows = []

    for query in query_pack:
        for year in range(YEAR_START, YEAR_END + 1):
            print(f"Buscando | ano={year} | query={query}")
            try:
                rows = fetch_openalex(query, year)
                print(f"  -> {len(rows)} registros")
                all_rows.extend(rows)
            except Exception as e:
                print(f"  ERRO | ano={year} | query={query} | {e}")

    if not all_rows:
        print("Nenhum registro coletado.")
        return

    df = pd.DataFrame(all_rows)

    output_csv = RAW_DIR / "openalex_results.csv"
    output_parquet = RAW_DIR / "openalex_results.parquet"

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    df.to_parquet(output_parquet, index=False)

    print(f"\nArquivo salvo em: {output_csv}")
    print(f"Arquivo salvo em: {output_parquet}")
    print(f"Total bruto coletado: {len(df)}")


if __name__ == "__main__":
    main()