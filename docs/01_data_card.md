# Data Card — Corpus Bibliométrico “Política Judiciária”

## Unidade de análise
Registro bibliográfico (work/paper/article) coletado de múltiplas fontes, consolidado em um dataset unificado.

## Escopo temporal
2000–2026 (inclusive).

## População-alvo (conceitual)
Produção acadêmica que:
1) **se autodenomina explicitamente** como “política judiciária / política judicial / judicial policy” (anel nuclear), e/ou
2) aborda temas cognatos de governança/gestão/reforma judicial (anel estendido).

## Fontes (bases) e natureza do dado
- **OpenAlex** (API): metadados bibliográficos e citações.
- **Crossref** (API): metadados por DOI.
- **Semantic Scholar** (API): metadados/abstracts (cobertura variável).
- **Scopus** (API; quando disponível): metadados indexados.
- **SciELO** (ArticleMeta API): metadados de periódicos SciELO Brasil (scl), coletados via endpoints estruturados.
- **Google Scholar** (via Publish or Perish / PoP): metadados capturados por busca na interface do Scholar (sem API oficial), exportados como CSV.

## Variáveis principais (colunas padronizadas no merge)
- `source` (fonte do registro)
- `source_id` (ID na fonte; ex.: DOI/URL/PID)
- `query_term` (string/rodada que originou o registro)
- `title`
- `doi`
- `publication_year`
- `journal` (ou venue)
- `type` (article/review/etc.; quando disponível)
- `language` (quando disponível)
- `cited_by_count`
- `authors` (string)
- `abstract` (quando disponível)
- + chaves auxiliares de normalização: `doi_norm`, `title_norm`, `journal_norm`

## Chave primária e deduplicação (regra)
- **Primária:** `doi_norm` (quando existe).
- **Fallback:** `title_norm + publication_year + journal_norm` (quando DOI está ausente).
- A deduplicação é executada em etapas do pipeline (unificação/limpeza), e os efeitos devem ser registrados em logs.

## Critérios mínimos de qualidade
- Registro deve conter, idealmente: `title` e `publication_year`.
- Registros sem DOI são mantidos, mas sujeitos a maior risco de duplicidade e ambiguidade.

## Ética e conformidade
- Apenas dados publicamente acessíveis (metadados bibliográficos).
- Nenhuma informação sensível pessoal é coletada além do que já é público em registros acadêmicos (autoria).
- Google Scholar: uso via PoP com exportação manual; sem scraping em massa por HTML e sem tentativa de contornar bloqueios.

## Saídas principais
- `data/interim/01_merged_all_sources.csv` (identificação pré-dedup)
- datasets “unified/analysis-ready” conforme scripts do pipeline
- corpus nuclear/estendido conforme flags e reclassificações
- logs de execução (data/hora/commit/contagens por etapa)
