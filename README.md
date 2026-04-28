# Public_Policy

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

## Como reproduzir

### Requisitos verificados

- Python 3.14.4
- Quarto 1.9.37
- R com pacotes usados no QMD (`bibliometrix`, `tidyverse`, `knitr`, `scales`, `patchwork`, `ggrepel`, `igraph`, `RColorBrewer`)

### 0) Instalação

```powershell
pip install -r requirements.txt
```

Se usar .env (opcional), configure chaves conforme scripts:

OPENALEX_API_KEY (opcional)
SEMANTIC_SCHOLAR_API_KEY (necessário para coleta via API)
SCOPUS_API_KEY (necessário para Scopus)

### 1) Coleta SciELO (ArticleMeta)

Exemplo com ISSNs selecionados:

python src/pipelines/13_collect_scielo.py --issn 0034-7612 --max-articles 500 --sleep 0.05
python src/pipelines/13b_review_scielo.py

### 2) Google Scholar via PoP (importação)

Após rodar PoP e exportar o Results CSV:

### Nuclear

python src/pipelines/04_import_pop_scholar.py \
  --input data/raw/google_scholar_pop_nuclear_results.csv \
  --query-term pop_nuclear \
  --output google_scholar_pop_nuclear.csv

### Extended

python src/pipelines/04_import_pop_scholar.py \
  --input data/raw/google_scholar_pop_extended_results.csv \
  --query-term pop_extended \
  --output google_scholar_pop_extended.csv

Opcional (recomendado): consolidar em um único arquivo:

python - <<'PY'
import pandas as pd
a=pd.read_csv("data/raw/google_scholar_pop_nuclear.csv")
b=pd.read_csv("data/raw/google_scholar_pop_extended.csv")
out=pd.concat([a,b], ignore_index=True)
out.to_csv("data/raw/google_scholar_pop_results.csv", index=False, encoding="utf-8-sig")
print("OK total:", len(out), "nuclear:", len(a), "extended:", len(b))
PY

### 3) Pipeline principal em comando único

```powershell
$env:PYTHONIOENCODING='utf-8'
python src\pipelines\14_rebuild_full_pipeline.py --offline --skip-enrich
```

Esse comando executa:

`06_merge_cross_base.py` → `07_dedup_cross_base.py` → `08_screen_prisma.py` → `08b_clean_and_enrich.py` → `08c_reclassify_nuclear.py` → `08d_final_nuclear_adjustment.py` → `09_prisma_flow.py` → `10_export_bibliometrix.py` → `16_brazil_supplement_compare.py` → `12_metadata_completeness.py`.

Seed documentada: `42`.

Logs principais:

- `logs/prisma_flow.csv`
- `logs/dedup_impact.csv`
- `data/interim/06_frozen_corpus.csv`
- `outputs/tables/brazil_supplement_comparison.csv`

### 4) Render do relatório

```powershell
quarto render relatorio_bibliometrico_politica_judiciaria.qmd --to docx
```

Para incluir Google Scholar/PoP no corpus principal, rode explicitamente:

```powershell
python src\pipelines\14_rebuild_full_pipeline.py --offline --with-pop --skip-enrich
```

Use essa opção apenas após curadoria dos candidatos, pois PoP/Scholar é snapshot manual e pode conter literatura cinzenta ou duplicatas bibliográficas imperfeitas.

### Dados e versionamento
Não versionar data/raw, data/interim, data/final (apenas .gitkeep).
Versionar:
scripts (src/pipelines)
documentação (docs/)
logs/runlog.md
relatório (.qmd), referências (.bib) e estilo (.csl)

### Uso de inteligência artificial

Ferramentas de IA foram utilizadas como apoio técnico/metodológico em tarefas como:

depuração e organização de pipelines,
estruturação documental,
revisão técnica e padronização.

Decisões substantivas (problema de pesquisa, critérios de triagem, delimitação do corpus e interpretação) permanecem sob responsabilidade do pesquisador.

### Situação atual

Pipeline principal reproduzido com snapshots locais das quatro bases globais. SciELO/PoP/Scholar permanecem como suplemento brasileiro rastreável e comparação externa, documentada no método e em `docs/REPRO_AUDIT.md`.
