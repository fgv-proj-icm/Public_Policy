from pathlib import Path
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

EMAIL = os.getenv("EMAIL_POLITE", "").strip()

query = "judicial policy"

params = {
    "query.title": query,
    "rows": 20,
}

if EMAIL:
    params["mailto"] = EMAIL

response = requests.get(
    "https://api.crossref.org/works",
    params=params,
    timeout=30,
)
response.raise_for_status()

items = response.json()["message"]["items"]

rows = []
for item in items:
    title = item.get("title", [""])
    journal = item.get("container-title", [""])
    published = item.get("published-print") or item.get("published-online") or {}

    year = None
    if published.get("date-parts"):
        year = published["date-parts"][0][0]

    rows.append(
        {
            "source": "crossref",
            "title": title[0] if title else "",
            "doi": item.get("DOI", ""),
            "year": year,
            "journal": journal[0] if journal else "",
            "type": item.get("type", ""),
            "citation_count": item.get("is-referenced-by-count", 0),
            "url": item.get("URL", ""),
        }
    )

df = pd.DataFrame(rows)
output_file = RAW_DIR / "crossref_results.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(df.head(10).to_string(index=False))
print(f"\nArquivo salvo em: {output_file}")