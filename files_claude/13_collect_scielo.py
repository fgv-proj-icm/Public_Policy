"""
13_collect_scielo.py
====================
Coleta de registros do SciELO via interface de busca programática.

O SciELO não exige autenticação. A busca é feita em search.scielo.org
com parsing dos resultados. Aplica as mesmas strings nucleares e
estendidas usadas nas demais bases.

Entrada : Strings de busca definidas no script
Saída   : data/raw/scielo_results.csv

Uso:
    python src/pipelines/13_collect_scielo.py
"""

from pathlib import Path
import time
import re
import html as html_module

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RAW_DIR / "scielo_results.csv"

# ── Strings de busca ────────────────────────────────────────────────────────
# Mesma lógica das demais bases: bloco nuclear + bloco estendido

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

SCIELO_SEARCH_URL = "https://search.scielo.org/"

MAX_RESULTS_PER_QUERY = 200  # SciELO raramente tem centenas por query específica
RESULTS_PER_PAGE = 50


def clean_text(text: str) -> str:
    """Limpa texto extraído do HTML."""
    if not text:
        return ""
    text = html_module.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_scielo_results(html_content: str, query: str) -> list[dict]:
    """Parseia a página de resultados do SciELO Search."""
    soup = BeautifulSoup(html_content, "html.parser")
    rows = []

    # Os resultados ficam em divs com classe "item"
    items = soup.select("div.item")

    if not items:
        # Fallback: tentar outro seletor
        items = soup.select("div.results div.line")

    for item in items:
        try:
            # Título
            title_tag = item.select_one("strong a") or item.select_one(".title a") or item.select_one("a.title")
            if not title_tag:
                title_tag = item.select_one("a[href*='scielo']")
            title = clean_text(title_tag.get_text()) if title_tag else ""

            if not title:
                continue

            # URL / PID
            url = ""
            if title_tag and title_tag.get("href"):
                url = title_tag["href"]

            # DOI
            doi = ""
            doi_tag = item.select_one("a[href*='doi.org']")
            if doi_tag:
                doi = doi_tag["href"].replace("https://doi.org/", "").replace("http://doi.org/", "")
            else:
                # Tentar extrair DOI do texto
                doi_match = re.search(r'10\.\d{4,}/[^\s<"]+', str(item))
                if doi_match:
                    doi = doi_match.group(0).rstrip(".")

            # Periódico
            journal = ""
            journal_tag = item.select_one(".source") or item.select_one(".journal")
            if journal_tag:
                journal = clean_text(journal_tag.get_text())

            # Ano
            year = ""
            year_match = re.search(r"\b(19|20)\d{2}\b", str(item))
            if year_match:
                year = year_match.group(0)

            # Autores
            authors = ""
            author_tags = item.select(".authors a") or item.select(".author")
            if author_tags:
                authors = "; ".join(clean_text(a.get_text()) for a in author_tags)

            # Abstract
            abstract = ""
            abs_tag = item.select_one(".abstract") or item.select_one(".description")
            if abs_tag:
                abstract = clean_text(abs_tag.get_text())

            # Idioma
            language = ""
            lang_tags = item.select(".lang a") or item.select("[data-lang]")
            if lang_tags:
                langs = [clean_text(l.get_text()) for l in lang_tags]
                language = "; ".join(langs) if langs else ""

            rows.append({
                "query_term": query,
                "source": "scielo",
                "title": title,
                "doi": doi,
                "publication_year": year,
                "journal": journal,
                "type": "article",
                "language": language,
                "cited_by_count": 0,  # SciELO search não retorna citações
                "authors": authors,
                "abstract": abstract[:500] if abstract else "",
                "url": url,
            })
        except Exception as e:
            print(f"    Erro ao parsear item: {e}")
            continue

    return rows


def fetch_scielo(query: str) -> list[dict]:
    """Busca no SciELO Search e retorna registros parseados."""
    all_rows = []

    for offset in range(0, MAX_RESULTS_PER_QUERY, RESULTS_PER_PAGE):
        params = {
            "q": query,
            "lang": "pt",
            "count": RESULTS_PER_PAGE,
            "from": offset + 1,
            "page": (offset // RESULTS_PER_PAGE) + 1,
            "filter[type][]": "research-article",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (research bibliometric study; contact via GitHub)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }

        try:
            response = requests.get(
                SCIELO_SEARCH_URL,
                params=params,
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:
                print(f"    Status {response.status_code} em offset={offset}")
                break

            rows = parse_scielo_results(response.text, query)

            if not rows:
                break

            all_rows.extend(rows)
            print(f"    offset={offset} -> {len(rows)} registros")

            # Se retornou menos que o page size, não há mais páginas
            if len(rows) < RESULTS_PER_PAGE:
                break

        except Exception as e:
            print(f"    ERRO em offset={offset}: {e}")
            break

        time.sleep(2)  # Respeitar rate limit (sem API key)

    return all_rows


def main():
    all_rows = []

    print("=" * 60)
    print("COLETA SCIELO — BLOCO NUCLEAR")
    print("=" * 60)

    for query in QUERY_PACK_NUCLEAR:
        print(f"\nQuery: {query}")
        rows = fetch_scielo(query)
        print(f"  Total: {len(rows)} registros")
        all_rows.extend(rows)

    print(f"\n{'=' * 60}")
    print("COLETA SCIELO — BLOCO ESTENDIDO")
    print("=" * 60)

    for query in QUERY_PACK_EXTENDED:
        print(f"\nQuery: {query}")
        rows = fetch_scielo(query)
        print(f"  Total: {len(rows)} registros")
        all_rows.extend(rows)

    if not all_rows:
        print("\nNenhum registro coletado. Verifique a conectividade e o formato do SciELO.")
        print("Se o parsing falhou, pode ser necessário ajustar os seletores CSS.")
        print("Verifique manualmente: https://search.scielo.org/?q=%22pol%C3%ADtica+judici%C3%A1ria%22")
        return

    df = pd.DataFrame(all_rows)

    # Normalização e deduplicação interna
    df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()
    df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()
    df["journal_norm"] = df["journal"].fillna("").astype(str).str.strip().str.lower()

    total_bruto = len(df)

    # Deduplicar
    df_with_doi = df[df["doi_norm"] != ""].copy()
    df_without_doi = df[df["doi_norm"] == ""].copy()

    df_with_doi = df_with_doi.drop_duplicates(subset=["doi_norm"], keep="first")
    df_without_doi = df_without_doi.drop_duplicates(
        subset=["title_norm", "publication_year", "journal_norm"], keep="first"
    )

    df_final = pd.concat([df_with_doi, df_without_doi], ignore_index=True)

    df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n{'=' * 60}")
    print("RESULTADO DA COLETA SCIELO")
    print(f"{'=' * 60}")
    print(f"Total bruto coletado:      {total_bruto:>6}")
    print(f"Após deduplicação interna: {len(df_final):>6}")
    print(f"Arquivo salvo em: {OUTPUT_FILE}")

    if len(df_final) > 0:
        print(f"\nTop queries:")
        print(df_final["query_term"].value_counts().head(10).to_string())
        print(f"\nTop periódicos:")
        print(df_final["journal"].fillna("N/D").value_counts().head(10).to_string())
        print(f"\nRegistros com DOI: {(df_final['doi_norm'] != '').sum()}")
        print(f"Registros com abstract: {(df_final['abstract'].fillna('') != '').sum()}")
    else:
        print("\n⚠ Nenhum resultado após deduplicação.")
        print("  Isso pode indicar que o parsing do HTML do SciELO precisa de ajuste.")
        print("  Verifique se a estrutura HTML mudou em search.scielo.org")


if __name__ == "__main__":
    main()
