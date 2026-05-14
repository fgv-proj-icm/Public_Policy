#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai texto dos PDFs disponiveis e gera resumos estruturados
para subsidiar a revisao bibliografica do artigo.
Saida: pdfs/textos_extraidos/ (TXTs) + pdfs/resumo_corpus_pdf.json
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import json
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Instale PyMuPDF: pip install pymupdf")
    sys.exit(1)

# ── Metadados curados de cada PDF ───────────────────────────────────────────
META = {
    "santiso2003.pdf": {
        "chave": "santiso2003",
        "ref": "Santiso (2003)",
        "titulo": "Economic reform and judicial governance in Brazil: balancing independence with accountability",
        "revista": "Democratization",
        "doi": "10.1080/13510340312331294077",
        "anel": "nuclear",
        "temas": ["governança judicial", "independência judicial", "accountability", "reforma judicial", "Brasil"],
    },
    "rios-figueroa2006.pdf": {
        "chave": "riosfigueroa2006",
        "ref": "Ríos-Figueroa & Taylor (2006)",
        "titulo": "Institutional Determinants of the Judicialisation of Policy in Brazil and Mexico",
        "revista": "Journal of Latin American Studies",
        "doi": "10.1017/S0022216X06001593",
        "anel": "estendido",
        "temas": ["judicialização", "instituições judiciais", "Brasil", "México", "políticas públicas"],
    },
    "garoupa2009.pdf": {
        "chave": "garoupa2009",
        "ref": "Garoupa & Ginsburg (2009)",
        "titulo": "Guarding the Guardians: Judicial Councils and Judicial Independence",
        "revista": "American Journal of Comparative Law",
        "doi": "10.5131/ajcl.2008.0004",
        "anel": "nuclear",
        "temas": ["conselhos judiciais", "independência judicial", "governança judicial", "direito comparado"],
    },
    "armony2005.pdf": {
        "chave": "armony2005",
        "ref": "Armony & Schamis (2005)",
        "titulo": "Babel in Democratization Studies",
        "revista": "Journal of Democracy",
        "doi": "",
        "anel": "estendido",
        "temas": ["democratização", "estudos comparativos", "América Latina", "governança"],
    },
    "visser2019.pdf": {
        "chave": "visser2019",
        "ref": "Visser, Schouteten & Dikkers (2019)",
        "titulo": "Controlling the Courts: New Public Management and the Dutch Judiciary",
        "revista": "Justice System Journal",
        "doi": "10.1080/0098261X.2018.1539645",
        "anel": "nuclear",
        "temas": ["Nova Gestão Pública", "NPM", "administração judicial", "Países Baixos", "desempenho judicial"],
    },
    "10.1017@S2071832200023178.pdf": {
        "chave": "kosar2018_orig",
        "ref": "Kosař (2018) [original]",
        "titulo": "Beyond Judicial Councils: Forms, Rationales and Impact of Judicial Self-Governance in Europe",
        "revista": "German Law Journal",
        "doi": "10.1017/S2071832200023178",
        "anel": "nuclear",
        "temas": ["autogovernança judicial", "conselhos judiciais", "Europa", "governança judicial comparada"],
    },
    "KOSAR_2018_beyond_judicial_councils.pdf": {
        "chave": "kosar2018",
        "ref": "Kosař (2018)",
        "titulo": "Beyond Judicial Councils: Forms, Rationales and Impact of Judicial Self-Governance in Europe",
        "revista": "German Law Journal",
        "doi": "10.1017/S2071832200023178",
        "anel": "nuclear",
        "temas": ["autogovernança judicial", "conselhos judiciais", "Europa", "governança judicial comparada"],
    },
    "AKUTSU_GUIMARAES_2012_dimensoes_governanca_judicial.pdf": {
        "chave": "akutsu2012",
        "ref": "Akutsu & Guimarães (2012)",
        "titulo": "Dimensões da governança judicial e sua aplicação ao sistema judicial brasileiro",
        "revista": "Revista Direito GV",
        "doi": "10.1590/S1808-24322012000100008",
        "anel": "nuclear",
        "temas": ["governança judicial", "sistema judicial brasileiro", "independência", "accountability", "acesso à justiça"],
    },
    "KOERNER_INATOMI_BARREIRA_2015_racionalizacao_gestao_judicial.pdf": {
        "chave": "koerner2015",
        "ref": "Koerner, Inatomi & Barreira (2015)",
        "titulo": "Dez anos de racionalização da gestão judicial no Brasil: efeitos e perspectivas",
        "revista": "Revista Direito e Práxis",
        "doi": "10.12957/dep.2015.18009",
        "anel": "nuclear",
        "temas": ["CNJ", "reforma gerencial", "Nova Gestão Pública", "metas judiciárias", "racionalização"],
    },
}


def extrair_texto(caminho: Path) -> str:
    doc = fitz.open(str(caminho))
    partes = []
    for pg in doc:
        partes.append(pg.get_text("text"))
    doc.close()
    texto = "\n".join(partes)
    # Limpeza básica
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    return texto.strip()


def resumir_estrutura(texto: str, max_chars: int = 8000) -> dict:
    """Extrai seções estruturais do texto."""
    linhas = texto.split("\n")
    n_palavras = len(texto.split())
    n_paginas_est = max(1, n_palavras // 300)

    # Tenta identificar seções
    secoes = []
    for i, linha in enumerate(linhas[:200]):
        s = linha.strip()
        if len(s) > 5 and len(s) < 120 and s.isupper():
            secoes.append(s)
        elif re.match(r"^(\d+\.?\s+[A-Z]|[IVX]+\.\s+[A-Z])", s):
            secoes.append(s)

    # Extrai os primeiros ~3000 chars (intro) e últimos 2000 (conclusão)
    intro = texto[:3000].strip()
    conclusao = texto[-2000:].strip() if len(texto) > 5000 else ""

    return {
        "n_palavras": n_palavras,
        "n_paginas_estimadas": n_paginas_est,
        "secoes_detectadas": secoes[:15],
        "trecho_inicial": intro[:2000],
        "trecho_final": conclusao[:1500],
    }


def main():
    pasta_pdfs = Path(__file__).parent
    pasta_out = pasta_pdfs / "textos_extraidos"
    pasta_out.mkdir(exist_ok=True)

    corpus = []

    # Processar todos os PDFs da pasta (não apenas os listados em META)
    pdfs = sorted(pasta_pdfs.glob("*.pdf"))
    print(f"PDFs encontrados: {len(pdfs)}\n")

    for pdf_path in pdfs:
        nome = pdf_path.name
        meta = META.get(nome, {
            "chave": nome.replace(".pdf", ""),
            "ref": nome.replace(".pdf", ""),
            "titulo": "(sem metadado curado)",
            "revista": "",
            "doi": "",
            "anel": "desconhecido",
            "temas": [],
        })

        print(f"Extraindo: {nome} ...", end=" ")
        try:
            texto = extrair_texto(pdf_path)
            struct = resumir_estrutura(texto)

            # Salvar texto completo
            txt_path = pasta_out / (meta["chave"] + ".txt")
            txt_path.write_text(texto, encoding="utf-8")

            entrada = {**meta, **struct, "pdf": nome}
            corpus.append(entrada)
            print(f"OK ({struct['n_palavras']} palavras, ~{struct['n_paginas_estimadas']}p)")

        except Exception as e:
            print(f"ERRO: {e}")
            corpus.append({**meta, "pdf": nome, "erro": str(e)})

    # Salvar resumo JSON
    resumo_path = pasta_pdfs / "resumo_corpus_pdf.json"
    with open(resumo_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print(f"\nTextos salvos em: {pasta_out}")
    print(f"Resumo JSON: {resumo_path}")
    print(f"\nCorpus PDF processado: {len(corpus)} obras")
    for e in corpus:
        ok = "n_palavras" in e
        print(f"  {'OK' if ok else 'ERR'} {e['ref']} - {e['titulo'][:60]}")


if __name__ == "__main__":
    main()
