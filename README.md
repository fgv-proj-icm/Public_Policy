# Public_Policy

Repositório da pesquisa sobre **política judiciária como campo emergente**, com foco na **identificação, triagem e análise bibliométrica** da produção acadêmica que se nomeia explicitamente como *política judiciária*, *política judicial* ou *judicial policy*.

O projeto combina **coleta multibase**, **deduplicação cross-base**, **triagem inspirada em PRISMA**, organização do corpus em **dois anéis** (nuclear e estendido) e produção de relatório final em **Quarto**.

---

## Pergunta de pesquisa

> Existe um campo de pesquisa que se reconhece e se apresenta explicitamente como política judiciária, política judicial ou *judicial policy* e, se existe, qual é sua configuração bibliométrica?

---

## Estratégia metodológica

A arquitetura analítica distingue dois níveis:

- **Anel nuclear (CORE_EX)**: registros que utilizam explicitamente o vocabulário do campo em **título e/ou resumo** (e, quando disponível, campos equivalentes).
- **Anel estendido (ADJ)**: literatura cognata sobre **administração/governança judicial**, **reforma judicial**, **gestão de tribunais**, **desempenho**, **acesso à justiça** e temas próximos.

A deduplicação segue hierarquia:

1. **DOI normalizado** (`doi_norm`)
2. **Fallback**: `title_norm + publication_year + journal_norm` (quando DOI ausente)

---

## Fontes de dados

### Bases com API (coleta programática)
- **OpenAlex**
- **Crossref**
- **Semantic Scholar**
- **Scopus** *(quando há chave/credencial disponível)*

### SciELO (Brasil) — via ArticleMeta API
Para reduzir sub-representação de periódicos brasileiros, o projeto integra SciELO por meio do **ArticleMeta API** (collection `scl`), utilizando:
- listagem de artigos por ISSN via `article/identifiers`
- recuperação por PID via `article/?code=...`
- extração de título (v12), resumo (v83), autores (v10), periódico (v30), ano (publication_year)

> Observação: em ambiente Codespace, endpoints web do SciELO (ex.: Search/OAI) podem retornar bloqueios anti-bot; o ArticleMeta se mostrou a alternativa mais estável e reprodutível.

### Google Scholar — via Publish or Perish (PoP)
Como **fonte complementar**, para capturar produção não indexada nas bases globais (incluindo literatura institucional/“cinzenta”), o projeto utiliza Google Scholar via **Publish or Perish**:
- execução das mesmas strings (nuclear e estendido)
- exportação manual do **Results CSV** (lista item-a-item)
- importação e padronização via `04_import_pop_scholar.py`

> Importante: o arquivo `*_metrics.csv` do PoP é apenas agregado e serve para documentação; o pipeline usa o `*_results.csv`.

---

## Status dos resultados

Os totais variam por rodada (dependem de credenciais para Scopus, ISSNs selecionados no SciELO e resultados do PoP).  
Os números consolidados do relatório anterior (quatro bases) foram:

- **7.161** registros identificados
- **1.193** duplicatas removidas
- **5.968** registros triados
- **1.042** registros excluídos
- **4.926** registros incluídos
  - **115** no **anel nuclear**
  - **4.811** no **anel estendido**

Com a inclusão de SciELO e PoP/Scholar, a etapa de **identificação** tende a aumentar e deve ser recalculada no PRISMA.

---

## Estrutura do repositório

```text
Public_Policy/
├── data/
│   ├── raw/        # entradas (não versionar)
│   ├── interim/    # intermediários (não versionar)
│   └── final/      # saídas (não versionar)
├── docs/           # documentação metodológica
├── logs/           # run logs (template versionado)
├── src/
│   └── pipelines/  # scripts do pipeline
├── relatorio_bibliometrico_politica_judiciaria.qmd
├── references.bib
├── abnt.csl
└── README.md
