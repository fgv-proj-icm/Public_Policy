# A — Strings de busca por base

Reproduz o Apêndice A do manuscrito. Strings copiadas exatamente como executadas,
conforme recomendação PRISMA-S.

Período de referência: **2000–2026**. Coleta programática via API.

## Desenho em dois anéis

| Anel | Critério |
| --- | --- |
| **Nuclear** | A expressão exata "política judiciária" / "judicial policy" / "política judicial" (e flexões) aparece no título ou resumo |
| **Estendido** | Registros sobre governança, administração e reforma do sistema de justiça, por termos cognatos |

## OpenAlex

**Bloco nuclear**

```
"judicial policy"
"judicial policies"
"política judiciária"
"políticas judiciárias"
"política judicial"
```

**Bloco estendido**

```
"judicial governance"
"judicial administration"
"court administration"
"court governance"
"judicial reform"
"reforma judicial"
"governança judicial"
"administração judiciária"
"Conselho Nacional de Justiça"
```

**Filtros**

```
publication_year:2000-2026
type:article|review
language:en|pt|es          (quando disponível)
```

## Scopus

```
TITLE-ABS-KEY( <bloco> ) AND PUBYEAR > 1999 AND PUBYEAR < 2027
```

## Semantic Scholar

```
endpoint:  /graph/v1/paper/search/bulk
fields:    title, year, abstract, citationCount, venue, externalIds, authors
filtro:    year:2000-
ordenação: citationCount:desc
```

## Crossref

```
endpoint: /works
campo:    query.bibliographic
filtros:  from-pub-date:2000-01-01, type:journal-article
paginação: 100 por página
```

## Google Scholar / Publish or Perish

Buscas dirigidas para o suplemento Brasil, com curadoria manual. Ver
`data/brazil_supplement_candidates.csv` no repositório de origem.

## Rastreabilidade

| Etapa | Registros | Arquivo |
| --- | ---: | --- |
| Coleta bruta (4 bases) | 7.161 | `data/raw/` |
| Após merge | — | `data/interim/01_merged_all_sources.csv` |
| Após deduplicação | — | `data/interim/02_deduplicated.csv` |
| Após triagem PRISMA | 4.926 | `data/interim/03_screened.csv` |
| Contagens PRISMA | — | `data/interim/03_prisma_counts.csv` |
| Anel nuclear | 115 | `data/final/corpus_nuclear.csv` |
| Anel estendido | 4.811 | `data/final/corpus_extended.csv` |
| Corpus completo | 4.926 | `data/final/corpus_complete.csv` |

Documentação metodológica complementar: `docs/01_data_card.md`,
`docs/01_metodologia.md`, `docs/04_prisma_flow.md`, `docs/07_search_strings.md`,
`docs/REPRO_AUDIT.md`.
