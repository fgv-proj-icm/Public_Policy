# baixar_abertos.py
# Uso: python baixar_abertos.py
# O script tenta baixar apenas URLs marcadas como abertas ou candidatas no manifesto.
# Se algum site bloquear automação, baixe manualmente pelo URL_acesso.

import csv
import os
import re
import requests

MANIFESTO = "manifesto_download_politica_judiciaria.csv"
PASTA = "pdfs_politica_judiciaria"
os.makedirs(PASTA, exist_ok=True)

def safe_name(name):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', name).strip('_')

with open(MANIFESTO, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        status = row.get("Status_download", "")
        url = row.get("URL_pdf_candidato", "")
        if not url:
            continue
        if "restrito" in status.lower():
            continue
        filename = safe_name(row.get("Arquivo_sugerido") or row.get("Titulo") + ".pdf")
        path = os.path.join(PASTA, filename)
        try:
            print(f"Baixando: {filename}")
            r = requests.get(url, timeout=45, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            content_type = r.headers.get("content-type", "").lower()
            if r.status_code == 200 and ("pdf" in content_type or r.content[:4] == b"%PDF"):
                with open(path, "wb") as out:
                    out.write(r.content)
                print(f"OK: {path}")
            else:
                print(f"NÃO BAIXADO: {filename} | status={r.status_code} | content-type={content_type} | use URL_acesso manualmente")
        except Exception as e:
            print(f"ERRO: {filename} | {e}")
