# CLAUDE.md — Bibliometria "Política Judiciária"

Guia para o agente de IA sobre este repositório.

## Reprodução rápida (1 linha)

```bash
pip install -r requirements.txt && make pipeline
```

Ou equivalente:

```bash
python src/pipelines/14_rebuild_full_pipeline.py --offline --skip-enrich
```

## Estrutura

```
src/
  pipelines/   # Scripts numerados (01–19); orquestrador: 14_rebuild_full_pipeline.py
  utils/       # Módulos compartilhados: normalize.py (DOI, título, periódico, score)
  validation/  # schema_check.py (guardrails metodológicos)
data/
  raw/         # Snapshots das APIs (ignorados no git)
  interim/     # Pipeline intermediários (ignorados no git)
  final/       # Corpus final (ignorado no git)
  manual/      # Decisões humanas (VERSIONADAS): brazil_curation_decisions.csv
  brazil_supplement_candidates.csv  # Candidatos Brasil (versionado)
logs/          # prisma_flow.csv, dedup_impact.csv (versionados)
outputs/
  tables/      # Tabelas de resultados (comparação Brasil, cobertura de metadados)
  network/     # Co-citação (GraphML, edges)
tests/         # pytest — 47 testes unitários (sem dependência de dados)
```

## Configuração

`config.yml` controla:
- `seed: 42` — semente fixa para reprodutibilidade
- `offline: true` — bloqueia chamadas de API (padrão seguro)
- `pipeline.include_brazil_supplement: false` — ativa o step 18 quando true

## Pipeline principal (steps 06–17)

| Script | Entrada | Saída |
|--------|---------|-------|
| 06_merge_cross_base | raw/\*.csv | 01_merged_all_sources.csv |
| 07_dedup_cross_base | 01_merged | 02_deduplicated.csv |
| 08_screen_prisma | 02_dedup | 03_screened.csv |
| 08b–08d | 03_screened | 06_frozen_corpus.csv |
| 09_prisma_flow | 06_frozen | logs/prisma_flow.csv |
| 10_export_bibliometrix | 06_frozen | data/final/corpus_\*.csv |
| 16_brazil_supplement | 06_frozen | outputs/tables/brazil_\*.csv + data/brazil_supplement_candidates.csv |

## Curadoria do suplemento Brasil (step 18)

Passo a passo:

1. Rodar step 16 (incluído no pipeline) para gerar `data/brazil_supplement_candidates.csv` (285 candidatos).
2. Rodar `python src/pipelines/18_brazil_curation_merge.py` → gera `data/manual/brazil_curation_decisions.csv` com 284 linhas para revisar.
3. Abrir o CSV, preencher colunas `decision` (include/exclude) e `reason` para cada linha.
4. Rodar novamente `python src/pipelines/18_brazil_curation_merge.py` → incorpora os aprovados e gera:
   - `data/interim/07_frozen_corpus_v2.csv`
   - `logs/prisma_flow_v2.csv`
   - `outputs/tables/brazil_inclusion_summary.csv`
5. Ativar no config: `pipeline.include_brazil_supplement: true`

## Enriquecimento de metadados (step 19)

Requer rede. Preenche abstract/language/authors faltantes via OpenAlex API:

```bash
make enrich
# ou: python src/pipelines/19_enrich_metadata.py --force-online
```

Cache local: `data/cache/openalex_metadata.jsonl` (ignorado no git).
Saídas: `data/final/corpus_complete_enriched.csv` + `outputs/tables/metadata_coverage_before_after.csv`.

## Testes e validação

```bash
make test       # 47 testes unitários (sem dados reais necessários)
make validate   # valida schema do corpus + consistência PRISMA
```

## Normalização

Todas as funções de normalização estão em `src/utils/normalize.py`.
Nunca reimplementar inline — importar de lá para manter consistência.

Funções: `normalize_doi`, `normalize_title`, `normalize_journal`,
`extract_year`, `compute_metadata_score`, `dedup_key`, `apply_normalizations`.

## Commits

Mensagens em português, imperativo, prefixo convencional:
`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
