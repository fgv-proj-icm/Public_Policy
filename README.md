# Public_Policy

> **Reprodução em 1 linha:**
>
> ```bash
> pip install -r requirements.txt && make pipeline
> ```

Repositório da pesquisa sobre **política judiciária como campo emergente**, com foco na **identificação, triagem e análise bibliométrica** da produção acadêmica que se nomeia explicitamente como *política judiciária*, *política judicial* ou *judicial policy*.

O projeto combina **coleta multibase**, **deduplicação cross-base**, **triagem inspirada em PRISMA**, organização do corpus em **dois anéis** (nuclear e estendido), suplemento brasileiro rastreável e produção de relatório final em **Quarto**.

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

Os números consolidados da rodada principal reproduzida em 28/04/2026 (quatro bases, modo offline, sem incorporação automática do suplemento brasileiro) são:

- **7.161** registros identificados
- **1.193** duplicatas removidas
- **5.968** registros triados
- **1.042** registros excluídos
- **4.926** registros incluídos
  - **115** no **anel nuclear**
  - **4.811** no **anel estendido**

O suplemento brasileiro é comparado separadamente em `outputs/tables/brazil_supplement_comparison.csv`. Na rodada atual, ele identifica 285 candidatos rastreáveis, 284 ainda ausentes do corpus congelado; esses itens exigem curadoria antes de alterar as estatísticas principais.

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
```

##  Arquivos e documentos importantes
Documentação
docs/01_data_card.md — definição da unidade, variáveis, chaves e ética
docs/07_search_strings.md — strings e rodadas (PRISMA / identificação)
docs/06_metodologia_fontes_complementares.md — SciELO (ArticleMeta) e PoP/Scholar
logs/runlog.md — log de execuções (data/commit/contagens/arquivos)

## Relatório
relatorio_bibliometrico_politica_judiciaria.qmd
Render:
quarto render relatorio_bibliometrico_politica_judiciaria.qmd --to docx

## Como reproduzir do zero

### Requisitos

- Python 3.11+
- Quarto 1.9+ (apenas para renderizar o relatório)
- R com `bibliometrix`, `tidyverse`, `knitr`, `ggplot2`, `igraph` (apenas para o relatório)

### Instalação

```bash
pip install -r requirements.txt
```

Configure chaves de API opcionais copiando `.env.example` → `.env`:

```env
OPENALEX_API_KEY=...        # opcional
SEMANTIC_SCHOLAR_API_KEY=... # para coleta via API
SCOPUS_API_KEY=...           # para Scopus
EMAIL_POLITE=seu@email.com  # polite pool OpenAlex
```

### Pipeline principal

```bash
make pipeline
# equivalente a: python src/pipelines/14_rebuild_full_pipeline.py --offline --skip-enrich
```

Executa os steps 06–17 em sequência (merge → dedup → PRISMA → limpeza → nuclear → freeze → export → brasil compare). Seed fixo: `42`.

### Testes e validação

```bash
make test       # 47 testes unitários (sem dados reais)
make validate   # valida schema + PRISMA do corpus congelado
```

### Render do relatório

```bash
make report
# equivalente a: quarto render relatorio_bibliometrico_politica_judiciaria.qmd --to docx
```

### Todos os alvos disponíveis

| Alvo | O que faz |
|------|-----------|
| `make setup` | `pip install -r requirements.txt` |
| `make pipeline` | pipeline offline (06–17) |
| `make brazil` | curadoria do suplemento Brasil (step 18) |
| `make enrich` | enriquece metadados via OpenAlex (requer rede) |
| `make report` | renderiza relatório Quarto |
| `make test` | pytest (47 testes) |
| `make validate` | schema + PRISMA do corpus |
| `make all` | setup + pipeline + validate + test |

---

## Outputs principais

| Arquivo | Descrição | Gerado por |
|---------|-----------|------------|
| `data/interim/06_frozen_corpus.csv` | Corpus congelado (4.926 registros) | 08d_final_nuclear_adjustment.py |
| `data/interim/07_frozen_corpus_v2.csv` | Corpus v2 com suplemento Brasil | 18_brazil_curation_merge.py |
| `data/final/corpus_nuclear.csv` | Anel nuclear (115 registros) | 10_export_bibliometrix.py |
| `data/final/corpus_complete.csv` | Corpus completo (nuclear + estendido) | 10_export_bibliometrix.py |
| `logs/prisma_flow.csv` | Contagens PRISMA | 09_prisma_flow.py |
| `logs/prisma_flow_v2.csv` | Contagens PRISMA com suplemento Brasil | 18_brazil_curation_merge.py |
| `outputs/tables/brazil_supplement_candidates.csv` | 285 candidatos Brasil | 16_brazil_supplement_compare.py |
| `outputs/tables/brazil_supplement_comparison.csv` | Comparação corpus × suplemento | 16_brazil_supplement_compare.py |
| `outputs/tables/brazil_inclusion_summary.csv` | Resumo da curadoria Brasil | 18_brazil_curation_merge.py |
| `outputs/tables/metadata_coverage_before_after.csv` | Cobertura antes/depois enrich | 19_enrich_metadata.py |
| `outputs/network/cocitation_graph.graphml` | Rede de co-citação (nuclear) | 17_export_network_snapshot.py |
| `data/manual/brazil_curation_decisions.csv` | Decisões humanas Brasil (versionado) | humano + 18_brazil_curation_merge.py |

---

## Curadoria do suplemento Brasil

O suplemento Brasil identificou **285 candidatos** (284 novos, 214 com anel nuclear sugerido) não presentes no corpus principal. Para incorporá-los:

**Passo 1 — Gerar planilha de revisão** (já gerada automaticamente pelo pipeline):

```bash
python src/pipelines/18_brazil_curation_merge.py
```

Abre/cria `data/manual/brazil_curation_decisions.csv` com colunas:
`id_local, doi, title, year, journal, source, match_status, suggested_ring, decision, reason`

**Passo 2 — Preencher decisões:**
Para cada linha com `match_status=new`, preencher:

- `decision`: `include` ou `exclude`
- `reason`: breve justificativa

**Passo 3 — Aplicar e gerar corpus v2:**

```bash
python src/pipelines/18_brazil_curation_merge.py
```

Gera `data/interim/07_frozen_corpus_v2.csv`, `logs/prisma_flow_v2.csv` e `outputs/tables/brazil_inclusion_summary.csv`.

**Passo 4 — Ativar no config** (se quiser que o pipeline principal use v2):

```yaml
# config.yml
pipeline:
  include_brazil_supplement: true
```

---

### Coleta SciELO (ArticleMeta)

```bash
python src/pipelines/13_collect_scielo.py --issn 0034-7612 --max-articles 500 --sleep 0.05
python src/pipelines/13b_review_scielo.py
```

### Google Scholar via Publish or Perish

Após exportar o Results CSV do PoP:

```bash
python src/pipelines/04_import_pop_scholar.py \
  --input data/raw/google_scholar_pop_nuclear_results.csv \
  --query-term pop_nuclear \
  --output google_scholar_pop_nuclear.csv
```

Para incluir PoP no corpus principal:

```bash
python src/pipelines/14_rebuild_full_pipeline.py --offline --with-pop --skip-enrich
```

---

### Dados e versionamento

Não versionados: `data/raw/`, `data/interim/`, `data/final/`, `data/cache/`

Versionados: `src/`, `docs/`, `tests/`, `logs/prisma_flow.csv`, `logs/dedup_impact.csv`,
`data/manual/`, `data/brazil_supplement_candidates.csv`, `config.yml`, `requirements.txt`

---

### Uso de inteligência artificial

Ferramentas de IA foram utilizadas como apoio técnico/metodológico (depuração e organização de pipelines, estruturação documental, revisão técnica). Decisões substantivas (problema de pesquisa, critérios de triagem, delimitação do corpus e interpretação) permanecem sob responsabilidade do pesquisador.

### Situação atual

Pipeline principal reproduzido com snapshots locais das quatro bases globais. SciELO/PoP/Scholar permanecem como suplemento brasileiro rastreável e comparação externa, documentada no método e em `docs/REPRO_AUDIT.md`.
