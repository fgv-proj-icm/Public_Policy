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
### 0) Instalação
pip install -r requirements.txt

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

### 3) Merge multibase (Identification)
python src/pipelines/06_merge_cross_base.py

### 4) Pipeline principal (unified → clean → analysis-ready → corpora)
python src/pipelines/06_build_unified_base.py
python src/pipelines/06b_review_unified_base.py

python src/pipelines/08_clean_unified_base.py
python src/pipelines/08b_review_unified_base_clean.py

python src/pipelines/09_build_analysis_ready_base.py
python src/pipelines/09b_review_analysis_ready_base.py

python src/pipelines/10a_finalize_no_doi_dedup.py
python src/pipelines/10b_normalize_query_and_type.py
python src/pipelines/10c_build_relevance_flags.py
python src/pipelines/10d_review_analysis_ready_v2.py

python src/pipelines/11a_build_core_corpus.py
python src/pipelines/11b_review_core_corpus.py

python src/pipelines/12a_build_focus_corpus.py
python src/pipelines/12b_review_focus_corpus.py

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
Integração SciELO via ArticleMeta concluída (com ISSNs selecionados).
Integração Google Scholar via PoP em andamento (nuclear concluído; estendido em execução).
Merge multibase (06_merge_cross_base.py) atualizado para incluir SciELO e PoP.
Próximo passo após concluir PoP (extended): consolidar google_scholar_pop_results.csv, rodar merge e reconstruir corpora/relatório.
