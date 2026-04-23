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

QUERY = """
TITLE-ABS-KEY(
    "judicial policy"
    OR "judicial policies"
    OR "judicial governance"
    OR "judicial administration"
    OR "court administration"
    OR "court governance"
    OR "judicial reform"
    OR "política judiciária"
    OR "políticas judiciárias"
    OR "governança judicial"
    OR "administração judiciária"
    OR "reforma do judiciário"
    OR "reforma judicial"
    OR "Conselho Nacional de Justiça"
)
AND PUBYEAR > 1999
AND PUBYEAR < 2027
"""

def main():
    if not API_KEY:
        raise RuntimeError("SCOPUS_API_KEY não encontrada no .env")

    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json",
    }

    params = {
        "query": QUERY,
        "count": 200,
        "start": 0,
    }

    url = "https://api.elsevier.com/content/search/scopus"
    response = requests.get(url, headers=headers, params=params, timeout=60)
    response.raise_for_status()

    entries = response.json().get("search-results", {}).get("entry", [])
    rows = []

    for item in entries:
        rows.append(
            {
                "source": "scopus",
                "title": item.get("dc:title", ""),
                "doi": item.get("prism:doi", ""),
                "publication_year": item.get("prism:coverDate", "")[:4],
                "journal": item.get("prism:publicationName", ""),
                "type": item.get("subtypeDescription", ""),
                "language": item.get("language", ""),
                "cited_by_count": item.get("citedby-count", 0),
                "scopus_id": item.get("dc:identifier", ""),
                "query_term": "SCOPUS_MAIN_QUERY",
            }
        )

    df = pd.DataFrame(rows)

    output_csv = RAW_DIR / "scopus_results.csv"
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"Arquivo salvo em: {output_csv}")
    print(f"Total bruto coletado: {len(df)}")

    time.sleep(1)

if __name__ == "__main__":
    main()