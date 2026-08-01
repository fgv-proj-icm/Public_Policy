#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline de download de PDFs - Politica Judiciaria
Fontes: SciELO, Unpaywall, URLs diretas do manifesto
Uso: python download_pipeline_scielo.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import csv
import os
import re
import time
import json
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Optional

# ── Configuração ────────────────────────────────────────────────────────────
MANIFESTO  = Path(__file__).parent / "manifesto_download_politica_judiciaria.csv"
PASTA_OUT  = Path(__file__).parent          # salva PDFs na própria pasta pdfs/
RELATORIO  = Path(__file__).parent / "relatorio_download.csv"
EMAIL      = os.getenv("EMAIL_POLITE", "")  # obrigatório para Unpaywall; definir no .env
DELAY_S    = 2                              # pausa entre requisições (segundos)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,application/octet-stream,*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def is_pdf(content: bytes) -> bool:
    return content[:4] == b"%PDF"


def baixar(url: str, destino: Path, label: str = "") -> bool:
    """Tenta baixar URL como PDF. Retorna True se bem-sucedido."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=40, allow_redirects=True)
        ct = resp.headers.get("content-type", "").lower()
        if resp.status_code == 200 and (is_pdf(resp.content) or "pdf" in ct):
            destino.write_bytes(resp.content)
            print(f"    ✓ salvo: {destino.name}")
            return True
        if resp.status_code == 200:
            print(f"    ✗ resposta não é PDF ({len(resp.content)} bytes, ct={ct[:40]})")
    except Exception as e:
        print(f"    ✗ erro: {e}")
    return False


# ── Estratégias de busca de PDF ──────────────────────────────────────────────

def scielo_pdf_url(url_candidate: str) -> Optional[str]:
    """Constrói URL de PDF do SciELO a partir de URL de artigo ou DOI redirect."""
    if not url_candidate:
        return None
    for lang in ("pt", "en", "es"):
        if "scielo" in url_candidate:
            base = url_candidate.split("?")[0]
            return f"{base}?format=pdf&lang={lang}"
    return None


def tentar_scielo_doi(doi: str) -> Optional[str]:
    """Segue o DOI e verifica se redireciona para SciELO."""
    if not doi:
        return None
    try:
        resp = requests.get(
            f"https://doi.org/{doi}", headers=HEADERS,
            timeout=20, allow_redirects=True
        )
        final = resp.url
        if "scielo" in final:
            base = final.split("?")[0]
            return f"{base}?format=pdf&lang=pt"
    except Exception:
        pass
    return None


def unpaywall(doi: str) -> Optional[str]:
    """Consulta Unpaywall para PDF em acesso aberto."""
    if not doi:
        return None
    doi_clean = doi.strip().lstrip("https://doi.org/").lstrip("http://dx.doi.org/")
    url = f"https://api.unpaywall.org/v2/{doi_clean}?email={EMAIL}"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get("is_oa"):
            return None
        best = data.get("best_oa_location") or {}
        pdf_url = best.get("url_for_pdf")
        if pdf_url:
            print(f"    → Unpaywall ({best.get('host_type','?')}): {pdf_url[:70]}")
        return pdf_url
    except Exception as e:
        print(f"    ✗ Unpaywall erro: {e}")
    return None


def processar_linha(row: dict, pasta: Path) -> dict:
    """Processa uma linha do manifesto e tenta baixar o PDF."""
    status = row.get("Status_download", "")
    arquivo_sug = row.get("Arquivo_sugerido", "")
    url_pdf = row.get("URL_pdf_candidato", "").strip()
    url_acesso = row.get("URL_acesso", "").strip()
    doi = row.get("DOI_verificado", "").strip()
    autor_ano = row.get("Autor_Ano", row.get("ID", ""))
    titulo = row.get("Titulo", "")

    nome_arquivo = safe_name(arquivo_sug) if arquivo_sug else safe_name(autor_ano + ".pdf")
    if not nome_arquivo.endswith(".pdf"):
        nome_arquivo += ".pdf"
    destino = pasta / nome_arquivo

    resultado = {
        "ID": row.get("ID", ""),
        "Autor_Ano": autor_ano,
        "DOI": doi,
        "status_final": "nao_tentado",
        "arquivo": "",
        "url_usada": "",
        "notas": "",
    }

    # Se já existe na pasta, não baixar novamente
    if destino.exists() and destino.stat().st_size > 10_000:
        print(f"  ↳ JÁ EXISTE: {nome_arquivo}")
        resultado["status_final"] = "ja_existe"
        resultado["arquivo"] = str(destino)
        return resultado

    # Ignorar itens explicitamente restritos sem URL candidata
    if "restrito" in status.lower() and not url_pdf and not doi:
        print(f"  ↳ RESTRITO: {autor_ano} — baixar via CAPES/biblioteca")
        resultado["status_final"] = "restrito"
        resultado["notas"] = "acesso institucional necessário"
        return resultado

    print(f"\n{'─'*60}")
    print(f"  [{row.get('ID','')}] {autor_ano}")
    print(f"  Status manifesto: {status[:60]}")

    tentativas = []

    # 1. URL de PDF direto do manifesto
    if url_pdf and "scielo" in url_pdf:
        tentativas.append(("SciELO manifesto", scielo_pdf_url(url_pdf) or url_pdf))
    elif url_pdf:
        tentativas.append(("URL manifesto", url_pdf))

    # 2. Seguir DOI → possível SciELO
    if doi:
        scielo_via_doi = tentar_scielo_doi(doi)
        if scielo_via_doi:
            tentativas.append(("SciELO via DOI", scielo_via_doi))

    # 3. Unpaywall
    if doi:
        up_url = unpaywall(doi)
        if up_url:
            tentativas.append(("Unpaywall", up_url))
        time.sleep(DELAY_S)

    # 4. URL de acesso direto (páginas que às vezes servem PDF)
    if url_acesso and "scielo" in url_acesso and not any("scielo" in t[1] for t in tentativas):
        tentativas.append(("SciELO acesso", scielo_pdf_url(url_acesso) or url_acesso))
    elif url_acesso and url_acesso != url_pdf:
        tentativas.append(("URL acesso", url_acesso))

    for fonte, url in tentativas:
        print(f"  → tentando [{fonte}]: {url[:80]}")
        if baixar(url, destino):
            resultado["status_final"] = "baixado"
            resultado["arquivo"] = str(destino)
            resultado["url_usada"] = url
            resultado["notas"] = f"fonte: {fonte}"
            return resultado
        time.sleep(DELAY_S)

    if tentativas:
        resultado["status_final"] = "falhou"
        resultado["notas"] = f"tentativas: {'; '.join(f[0] for f in tentativas)}"
    else:
        resultado["status_final"] = "sem_url"
        resultado["notas"] = "nenhuma URL disponível no manifesto"

    print(f"  ✗ não baixado: {autor_ano}")
    return resultado


def main():
    print("=" * 60)
    print("Pipeline de Download de PDFs – Política Judiciária")
    print("=" * 60)

    if not MANIFESTO.exists():
        print(f"✗ Manifesto não encontrado: {MANIFESTO}")
        sys.exit(1)

    PASTA_OUT.mkdir(parents=True, exist_ok=True)

    # Ler manifesto
    with open(MANIFESTO, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Manifesto: {len(rows)} itens\n")

    resultados = []
    for row in rows:
        res = processar_linha(row, PASTA_OUT)
        res["Titulo"] = row.get("Titulo", "")
        resultados.append(res)

    # Relatório
    print(f"\n{'='*60}")
    print("RELATÓRIO FINAL")
    print(f"{'='*60}")
    contagem = {}
    for r in resultados:
        s = r["status_final"]
        contagem[s] = contagem.get(s, 0) + 1

    for k, v in sorted(contagem.items()):
        emoji = {"ja_existe": "✓", "baixado": "✓", "restrito": "⚠", "falhou": "✗", "sem_url": "✗"}.get(k, "?")
        print(f"  {emoji} {k}: {v}")

    # Listar não baixados
    nao_ok = [r for r in resultados if r["status_final"] not in ("ja_existe", "baixado")]
    if nao_ok:
        print("\nItens que precisam de ação manual:")
        for r in nao_ok:
            print(f"  [{r['ID']}] {r['Autor_Ano']} — {r['status_final']}: {r['notas']}")

    # Salvar relatório CSV
    with open(RELATORIO, "w", newline="", encoding="utf-8") as f:
        campos = ["ID", "Autor_Ano", "Titulo", "DOI", "status_final", "arquivo", "url_usada", "notas"]
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nRelatório salvo em: {RELATORIO}")

    # Listar PDFs existentes na pasta
    pdfs = sorted(PASTA_OUT.glob("*.pdf"))
    print(f"\nPDFs na pasta ({len(pdfs)}):")
    for p in pdfs:
        size_kb = p.stat().st_size // 1024
        print(f"  {p.name} ({size_kb} KB)")


if __name__ == "__main__":
    main()
