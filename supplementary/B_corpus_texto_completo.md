# B — Corpus de texto completo (PDFs curados)

Reproduz o Apêndice B do manuscrito.

Para a revisão bibliográfica narrativa, foram obtidos textos completos de **9 obras**
por acesso aberto, repositórios institucionais e arquivos de pesquisa, a partir de
12 obras de alta prioridade no manifesto de download.

Extração de texto com **PyMuPDF 1.27**, a partir dos PDFs em `pdfs/`.

## Manifesto

| Obra | Revista | Ano | Palavras (est.) | Acesso |
| --- | --- | ---: | ---: | --- |
| Garoupa & Ginsburg (2009) | Am. J. Comparative Law | 2009 | ~13.200 | Arquivo de pesquisa |
| Kosař (2018) | German Law Journal | 2018 | ~19.600 | Acesso aberto (Cambridge) |
| Visser et al. (2019) | Justice System Journal | 2019 | ~9.000 | Acesso aberto (T&F) |
| Koerner et al. (2015) | Revista Direito e Práxis | 2015 | ~13.000 | Acesso aberto (UERJ) |
| Santiso (2003) | Democratization | 2003 | ~10.900 | Arquivo de pesquisa |
| Akutsu & Guimarães (2012) | Revista Direito GV | 2012 | ~9.300 | Repositório UnB / SciELO |
| Ríos-Figueroa & Taylor (2006) | J. Latin American Studies | 2006 | ~12.800 | Arquivo de pesquisa |

## Obras revisadas sem texto integral

| Obra | Situação |
| --- | --- |
| Ng (2011) | Utrecht Law Review — discutida a partir de resumo e citações secundárias |
| Staats, Bowler & Hiskey (2005) | Latin American Politics and Society — discutida como referência metodológica, sem texto integral |
| Taylor (2007) | Dados — texto consultado, sem extração automatizada |

Essa distinção está declarada no manuscrito: a revisão informa que, das 12 obras de
alta prioridade, 9 tiveram texto completo obtido.

## Scripts

| Script | Função |
| --- | --- |
| `pdfs/download_pipeline_scielo.py` | Download dos PDFs disponíveis |
| `pdfs/extrair_texto_pdfs.py` | Extração de texto com PyMuPDF |

Os PDFs em si **não** são redistribuídos, por restrição de direitos autorais. O
manifesto permite localizar cada obra na fonte original.
