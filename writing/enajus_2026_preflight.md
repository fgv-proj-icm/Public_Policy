# EnAJUS 2026 — Preflight da Submissão Bibliométrica

**Data da verificação:** 4 de junho de 2026  
**Tipo de trabalho:** Trabalho empírico concluído  
**Tema de interesse:** 9) Políticas Públicas de Justiça. Formulação, Implementação e Avaliação  
**Título comum às duas etapas:** Política Judiciária como Campo Emergente: Uma Análise Bibliométrica Multibase

## Artefatos

| Artefato | Finalidade |
|---|---|
| `enajus_2026_resumo_expandido_blind.pdf` | Arquivo anônimo para a primeira etapa |
| `enajus_2026_resumo_expandido_blind.docx` | Revisão e conferência do resumo expandido |
| `enajus_2026_trabalho_completo.pdf` | PDF sem senha para a segunda etapa, caso selecionado |
| `enajus_2026_trabalho_completo_revisao.docx` | Revisão editorial do trabalho completo |
| `enajus_2026_resumo_expandido_blind.qmd` | Fonte reproduzível do resumo |
| `enajus_2026_trabalho_completo.qmd` | Fonte reproduzível baseada na versão `v2` |
| `build_enajus.ps1` | Regenera DOCX, PDF e documento de referência |

## Verificações

| Critério | Resultado | Status |
|---|---:|---|
| Título | 9 palavras; idêntico nas duas etapas | OK |
| Resumo expandido | 938 palavras na extração DOCX; 950 na extração PDF | OK: 900–1.100 |
| Corpo do resumo expandido | 1 parágrafo | OK |
| Referências científicas do resumo | 5 obras citadas e listadas | OK: 2–5 |
| Anonimização do resumo | 0 menções a autor ou afiliação no DOCX/PDF | OK |
| Trabalho completo | 8.638 palavras na extração DOCX | OK: 4.000–9.000 |
| Resumo do trabalho completo | 169 palavras | OK: até 250 |
| Palavras-chave | 5, separadas por ponto-e-vírgula | OK |
| Estrutura empírica | Introdução; Quadro Teórico-Conceitual; Métodos e Técnicas; Resultados; Discussão; Conclusões e Recomendações | OK |
| Notas | Sem notas de rodapé ou de fim | OK |
| Sumário | Ausente | OK |
| Referências e citações | APA por `apa.csl` | OK |
| Tabelas e figuras | Legendas presentes e interpretação incorporada ao texto | OK |
| Fonte dos PDFs | Somente variantes incorporadas de Times New Roman | OK |
| Layout | A4; Times New Roman 12; espaço simples; margens 3 cm superior/esquerda e 2 cm inferior/direita | OK |
| Resumo expandido PDF | 2 páginas; sem senha | OK |
| Trabalho completo PDF | 27 páginas; sem senha | OK |

## Integridade

| Arquivo | SHA-256 |
|---|---|
| `enajus_2026_resumo_expandido_blind.pdf` | `BEB48E970650D62846B818901D85CB94B2D17C264D37F89381B33ABAF6A6FDEA` |
| `enajus_2026_trabalho_completo.pdf` | `A4CEA3905088B4C43DC021ED92F269AE43954517F208F2AF4C4A09A582008285` |
| `enajus_2026_resumo_expandido_blind.docx` | `0994CF94B81B5061C821FB96A13FC5035D5DD1EF155F62F6A53A7BBEB1DC7FF3` |
| `enajus_2026_trabalho_completo_revisao.docx` | `E567588A9D6D4ACEB3463FC43D2BB9731FE48F78EAE29AD41C94C888752B4C96` |

## Reprodução

Executar na raiz de `Public_Policy`:

```powershell
.\writing\build_enajus.ps1
```

## Fontes Oficiais

- https://enajus.org.br/submissao-de-trabalhos/
- https://enajus.org.br/temas-de-interesse/
- https://enajus.org.br/datas-importantes/
