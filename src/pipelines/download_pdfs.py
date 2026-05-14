#!/usr/bin/env python3
"""
DOWNLOAD AUTOMATIZADO DE PDFs - Fontes Abertas
Política Judiciária / Judicial Policy / Judicial Governance
Usa: SciELO, Unpaywall, DOAJ, CORE, Crossref
"""

import csv
import os
import re
import time
import json
import requests
from urllib.parse import urlparse
from typing import List, Dict, Optional

# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO_ENTRADA = "corpus_nuclear.csv"  # Substitua pelo nome do seu arquivo
PASTA_SAIDA = "pdfs_baixados"
UNPAYWALL_EMAIL = "seu@email.com"  # Obrigatório para usar Unpaywall

# ============================================================
# FUNÇÕES PRINCIPAIS
# ============================================================

def carregar_dois(arquivo_csv: str) -> List[Dict]:
    """Carrega DOIs do CSV de entrada."""
    dois = []
    with open(arquivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get('doi', row.get('DOI', '')).strip()
            if doi:
                dois.append({
                    'doi': doi,
                    'titulo': row.get('titulo', row.get('title', '')),
                    'autores': row.get('autores', row.get('authors', ''))
                })
    return dois

def normalizar_doi(doi: str) -> str:
    """Limpa e normaliza DOI."""
    doi = doi.strip().lower()
    if doi.startswith('https://doi.org/'):
        doi = doi.replace('https://doi.org/', '')
    if doi.startswith('http://dx.doi.org/'):
        doi = doi.replace('http://dx.doi.org/', '')
    if doi.startswith('doi:'):
        doi = doi.replace('doi:', '')
    # Remove trailing punctuation
    doi = doi.rstrip('.')
    return doi

def buscar_unpaywall(doi: str) -> Optional[Dict]:
    """Consulta Unpaywall para obter link de PDF em acesso aberto."""
    url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('is_oa') and data.get('best_oa_location'):
                return {
                    'pdf_url': data['best_oa_location'].get('url_for_pdf'),
                    'host_type': data['best_oa_location'].get('host_type'),
                    'repository': data['best_oa_location'].get('repository_institution', '')
                }
    except Exception as e:
        print(f"  ⚠ Erro Unpaywall para {doi}: {e}")
    return None

def buscar_scielo(doi: str) -> Optional[str]:
    """Verifica se o artigo está no SciELO e obtém link do PDF."""
    url = f"https://doi.org/{doi}"
    try:
        resp = requests.get(url, allow_redirects=True, timeout=15)
        final_url = resp.url
        # Se for SciELO, constrói URL do PDF
        if 'scielo.br' in final_url or 'scielo.org' in final_url:
            # SciELO geralmente tem PDF no padrão: ...?format=pdf&lang=pt
            if '?' in final_url:
                base = final_url.split('?')[0]
            else:
                base = final_url
            pdf_url = base + "?format=pdf&lang=pt"
            return pdf_url
    except:
        pass
    return None

def buscar_crossref(doi: str) -> Optional[str]:
    """Consulta Crossref para obter URL do artigo."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            urls = data.get('message', {}).get('URL', '')
            if urls:
                return urls
    except:
        pass
    return None

def baixar_pdf(url: str, caminho_arquivo: str) -> bool:
    """Baixa o PDF de uma URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if resp.status_code == 200 and 'application/pdf' in resp.headers.get('Content-Type', ''):
            with open(caminho_arquivo, 'wb') as f:
                f.write(resp.content)
            return True
        # Se não foi PDF, verifica se houve redirecionamento
        if resp.status_code == 200 and len(resp.content) > 1000:
            # Pode ser PDF mesmo sem Content-Type correto
            if resp.content[:4] == b'%PDF':
                with open(caminho_arquivo, 'wb') as f:
                    f.write(resp.content)
                return True
            print(f"    ⚠ Resposta não é PDF ({len(resp.content)} bytes)")
            return False
    except Exception as e:
        print(f"    ⚠ Erro no download: {e}")
    return False

def processar_doi(doi: str, pasta: str) -> Dict:
    """Processa um DOI: busca PDF em múltiplas fontes e tenta baixar."""
    resultado = {
        'doi': doi,
        'status': 'não encontrado',
[],
'arquivo': None,
'pdf_url': None
}

print(f"\n🔍 Processando: {doi}")

# 1. Tenta SciELO primeiro (fonte mais confiável para Brasil)
pdf_url = buscar_scielo(doi)
if pdf_url:
append(f"SciELO: {pdf_url}")
resultado['pdf_url'] = pdf_url
print(f" ✅ Encontrado no SciELO")

    nome_arquivo = doi.replace('/', '_').replace('.', '_') + '.pdf'
    caminho = os.path.join(pasta, nome_arquivo)
    
    if baixar_pdf(pdf_url, caminho):
        resultado['status'] = 'baixado'
        resultado['arquivo'] = caminho
        print(f"   ✅ PDF baixado: {caminho}")
        return resultado
    else:
        print(f"   ⚠ Falha no download do SciELO")

# 2. Tenta Unpaywall  
unpaywall_data = buscar_unpaywall(doi)
if unpaywall_data and unpaywall_data['pdf_url']:
append(f"Unpaywall ({unpaywall_data['repository']}): {unpaywall_data['pdf_url']}")
resultado['pdf_url'] = unpaywall_data['pdf_url']
print(f" ✅ Encontrado via Unpaywall")

    nome_arquivo = doi.replace('/', '_').replace('.', '_') + '.pdf'
    caminho = os.path.join(pasta, nome_arquivo)
    
    if baixar_pdf(unpaywall_data['pdf_url'], caminho):
        resultado['status'] = 'baixado'
        resultado['arquivo'] = caminho
        print(f"   ✅ PDF baixado: {caminho}")
        return resultado
    else:
        print(f"   ⚠ Falha no download via Unpaywall")

# 3. Tenta Crossref para obter URL do periódico
crossref_url = buscar_crossref(doi)
if crossref_url:
append(f"Crossref: {crossref_url}")
resultado['pdf_url'] = crossref_url
print(f" ⚠ URL do artigo: {crossref_url}")

    # Tenta baixar diretamente da página (menos confiável)
    nome_arquivo = doi.replace('/', '_').replace('.', '_') + '.pdf'
    caminho = os.path.join(pasta, nome_arquivo)
    
    if baixar_pdf(crossref_url, caminho):
        resultado['status'] = 'baixado'
        resultado['arquivo'] = caminho
        print(f"   ✅ PDF baixado de URL"
              f"")
        return resultado
    else:
        resultado['status'] = 'não baixado'
        print(f"   ❌ Apenas URL registrada")

resultado['status'] = 'não encontrado em fonte aberta'
print(f"   ❌ PDF não localizado em fonte aberta")

return resultado
def main():
"""Função principal."""
# Cria pasta de saída
os.makedirs(PASTA_SAIDA, exist_ok=True)

# Carrega DOIs
print(f"📂 Carregando DOIs de: {ARQUIVO_ENTRADA}")
if not os.path.exists(ARQUIVO_ENTRADA):
    print(f"❌ Arquivo {ARQUIVO_ENTRADA} não encontrado!")
    print("   Por favor, faça upload do arquivo corpus_nuclear.csv")
    return

registros = carregar_dois(ARQUIVO_ENTRADA)
print(f"   Total de DOIs carregados: {len(registros)}")

# Processa cada DOI
resultados = []
for i, reg in enumerate(registros, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/{len(registros)}]")
    doi = normalizar_doi(reg['doi'])
    resultado = processar_doi(doi, PASTA_SAIDA)
    resultado['titulo'] = reg['titulo']
    resultado['autores'] = reg['autores']
    resultados.append(resultado)
    time.sleep(1)  # Pausa para respeitar limites de API

# Gera relatório final
print(f"\n{'='*60}")
print("📊 RELATÓRIO FINAL")
print(f"{'='*60}")

baixados = [r for r in resultados if r['status'] == 'baixado']
nao_encontrados = [r for r in resultados if r['status'] == 'não encontrado em fonte aberta']
url_only = [r for r in resultados if r['status'] == 'não baixado']

print(f"✅ PDFs baixados: {len(baixados)}")
print(f"❌ Não encontrados em fonte aberta: {len(nao_encontrados)}")
print(f"⚠️  Apenas URL registrada (acesso restrito): {len(url_only)}")

for r in nao_encontrados:
    print(f"   - {r['doi']} | {r.get('titulo', '')}")

# Exporta relatório CSV
relatorio_path = os.path.join(PASTA_SAIDA, 'relatorio_download.csv')
with open(relatorio_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['doi', 'titulo', 'autores', 'status', 'arquivo', 'pdf_url', 'fontes'])
    writer.writeheader()
    writer.writerows(resultados)

print(f"\n📄 Relatório salvo em: {relatorio_path}")
print(f"📁 PDFs salvos em: {PASTA_SAIDA}/")
if name == "main":
main()