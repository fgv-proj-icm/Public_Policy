# Metodologia da Pesquisa Bibliométrica

## 1. Problema de pesquisa

Esta pesquisa tem por objetivo mapear o estado da arte do campo que se nomeia explicitamente como **política judiciária**, e não todo o universo de estudos sobre o Poder Judiciário ou sobre o sistema de justiça em sentido amplo.

A pergunta central é:

> Existe um campo que se reconhece e se apresenta explicitamente como *política judiciária*, *política judicial* ou *judicial policy*, e, se existe, qual é sua configuração bibliométrica?

Essa formulação desloca a pesquisa de uma busca temática ampla para uma busca por **identidade lexical e disciplinar**.

## 2. Delimitação do objeto

O objeto principal **não é**: todo estudo sobre reforma judicial, administração judicial, governança judicial, judicial review ou judicialização de políticas públicas. Esses temas compõem o universo mais amplo dos estudos sobre justiça, mas não correspondem automaticamente ao campo que se autodenomina como política judiciária.

A pesquisa distingue entre dois anéis:

### 2.1. Anel nuclear (CORE_EX)

Registros que utilizam explicitamente as expressões: *política judiciária*, *políticas judiciárias*, *judicial policy*, *judicial policies*, *judiciary policy*, *política judicial*, *políticas judiciales* em campos centrais do registro (título, resumo, palavras-chave).

Após reclassificação semântica, o anel nuclear foi restrito à **acepção programática** do termo (governança institucional do sistema de justiça), excluindo:

- *Judicial policy-making* (comportamento decisório dos juízes) → reclassificado para estendido
- *Criminal judicial policy* (sentenciamento penal) → reclassificado para estendido
- Tradição russa/pós-soviética (doutrina jurídica) → reclassificado para estendido
- Artigos históricos (política imperial) → reclassificado para estendido

### 2.2. Anel estendido (ADJ)

Registros que tratam de temas próximos mas não se nomeiam explicitamente, usando termos cognatos: *judicial administration*, *court administration*, *judicial governance*, *court governance*, *judicial reform*, *judicial management*, *Conselho Nacional de Justiça*, entre outros.

O anel estendido serve para contextualização, comparação núcleo/periferia e análises relacionais (co-citação).

## 3. Fontes de dados

A pesquisa utiliza **cinco** bases bibliográficas:

| Base | Tipo de acesso | Cobertura principal |
|---|---|---|
| OpenAlex | API (com chave) | Cobertura ampla, metadados do WoS, periódicos OA |
| Scopus | API (com chave) | Literatura indexada de alto impacto |
| Semantic Scholar | API (com chave) | OA, abstracts, referências |
| Crossref | API (polite pool) | DOIs, metadados de periódicos |
| SciELO | API (acesso aberto) | Periódicos latino-americanos indexados |

A inclusão do SciELO visa corrigir a subrepresentação de periódicos brasileiros de direito e administração pública nas quatro bases iniciais. A produção brasileira que mais utiliza o termo "política judiciária" no sentido programático (CNJ, resolução de conflitos, gestão judicial) publica predominantemente em periódicos indexados no SciELO.

O Web of Science não foi incluído por indisponibilidade de acesso à API. Essa limitação é parcialmente mitigada pela cobertura do OpenAlex.

## 4. Strings de busca

### Bloco nuclear (expressões exatas)

```
"judicial policy"
"judicial policies"
"judiciary policy"
"política judiciária"
"políticas judiciárias"
"política judicial"
"políticas judiciales"
```

### Bloco estendido (termos cognatos)

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

As strings são aplicadas em campos de título, resumo e palavras-chave, com adaptações sintáticas por base (ver Apêndice A do artigo e scripts no repositório).

## 5. Protocolo PRISMA adaptado

O fluxo segue o PRISMA 2020 como dispositivo de transparência, organizado em:

### 5.1. Identificação

Coleta programática via API nas cinco bases. Resultados brutos salvos em `data/raw/`.

### 5.2. Deduplicação

Consolidação cross-base com deduplicação por:

1. DOI normalizado (chave primária)
2. Título normalizado + ano + periódico (fallback para registros sem DOI)

### 5.3. Triagem (Screening)

Cada registro é classificado em: `nuclear`, `extended` ou `excluded`, com motivo explícito. Critérios de exclusão:

- Sem relação com o sistema de justiça
- Judicial review em sentido constitucionalista
- Judicialização de políticas públicas (sem foco no Judiciário como instituição)
- Periódico ou título fora do escopo (ciências naturais, medicina, engenharia)
- Metadados insuficientes

### 5.4. Reclassificação semântica

O anel nuclear é submetido a reclassificação para restringir à acepção programática:

- Rodada 1: judicial policy-making → estendido (n = 33)
- Rodada 2: criminal judicial policy → estendido (n = 7)
- Rodada 3: tradição russa/históricos → estendido (n = 15)

### 5.5. Enriquecimento

Coleta de referências bibliográficas (referenced_works) e abstracts via OpenAlex para o anel nuclear, visando análise exploratória de co-citação.

## 6. Pipeline de processamento

| Script | Função | Entrada | Saída |
|---|---|---|---|
| 01–05 | Coleta por base (Crossref, OpenAlex, Scopus, Semantic Scholar) | APIs | `data/raw/*_refined.csv` |
| 13 | Coleta SciELO | API SciELO | `data/raw/scielo_results.csv` |
| 13b | Review SciELO | `data/raw/scielo_results.csv` | Console |
| 06 | Merge cross-base | `data/raw/*_refined.csv` + SciELO | `data/interim/01_merged_all_sources.csv` |
| 07 | Deduplicação inter-bases | 01_merged | `data/interim/02_deduplicated.csv` + `logs/dedup_impact.csv` |
| 08 | Triagem PRISMA | 02_deduplicated | `data/interim/03_screened.csv` + `03_excluded.csv` |
| 08b | Limpeza pós-triagem | 03_screened | `data/interim/04_cleaned.csv` |
| 08c | Reclassificação nuclear | 04_cleaned | `data/interim/05_reclassified.csv` |
| 08d | Ajuste final | 05_reclassified | `data/interim/06_frozen_corpus.csv` |
| 09 | PRISMA flow diagram | Todos os interim | `docs/04_prisma_flow.md` + `logs/prisma_flow.csv` |
| 10 | Exportação bibliometrix | 06_frozen | `data/final/corpus_*.csv` |
| 11 | Enriquecimento de referências | corpus_nuclear | `data/interim/07_nuclear_*.csv` |
| 12 | Completude de metadados | 06_frozen + 07_enriched | `data/interim/08_metadata_*.csv` |
| 14 | Orquestrador (pipeline completo) | `data/raw/` | Executa 06→07→08→08b→08c→08d→09→10→16→12 |
| 16 | Comparação suplemento brasileiro | `data/brazil_supplement.csv` + corpus | `outputs/tables/brazil_supplement_comparison.csv` |
| 17 | Exportação snapshot de rede | corpus_nuclear | `outputs/network/` |

## 7. Situação atual

Rodada principal executada em 28/04/2026 (quatro bases globais, modo offline):

| Etapa | Status |
|---|---|
| Coleta OpenAlex, Scopus, Crossref, Semantic Scholar | Concluída |
| Coleta SciELO | Suplemento opcional — não integrado ao corpus principal |
| Merge e deduplicação | Concluída — 7.161 identificados → 5.968 após dedup |
| Triagem e reclassificação | Concluída — 115 nuclear / 4.811 estendido / 1.042 excluídos |
| Enriquecimento (referências/abstracts) | Concluída — 31/115 registros nucleares com referências OpenAlex |
| Suplemento brasileiro | Comparação externa — 285 candidatos, 284 ausentes do corpus congelado |
| Completude de metadados | Concluída |
| Análise bibliométrica (QMD) | Relatório renderizado (DOCX) — corpus congelado em `06_frozen_corpus.csv` |

## 8. Repositório

Todo o código, dados e decisões metodológicas estão em:

**GitHub:** [github.com/cairesmachado-svg/Public_Policy](https://github.com/cairesmachado-svg/Public_Policy)
