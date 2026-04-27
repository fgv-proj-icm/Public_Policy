# Strings de busca e rodadas (PRISMA — Identificação)

Este documento lista as strings aplicadas por fonte (bases/APIs e PoP) e define os blocos nuclear e estendido. As strings devem ser registradas com data de execução e parâmetros no runlog.

---

## 1) Bloco nuclear (expressões exatas / identidade lexical)

Expressões (usar com aspas):
- "política judiciária"
- "políticas judiciárias"
- "política judicial"
- "políticas judiciales"
- "judicial policy"
- "judicial policies"
- "judiciary policy"
- "judiciary policies"

Objetivo: identificar produção que se autodenomina explicitamente (CORE_EX).

---

## 2) Bloco estendido (termos cognatos / adjacência temática)

Expressões (usar com aspas):
- "judicial governance"
- "judicial administration"
- "court administration"
- "court governance"
- "judicial reform"
- "reforma judicial"
- "governança judicial"
- "administração judiciária"
- "Conselho Nacional de Justiça"
- "reforma do judiciário"
- "gestão judicial"
- "gestão de tribunais"

Objetivo: formar o anel adjacente (ADJ) para contextualização e comparação.

---

## 3) Implementação por fonte

### 3.1 OpenAlex (API)
- Campo: `search`
- Filtros: `publication_year:2000–2026`, `type:article|review`, `language:en|pt|es`
- Rodadas: múltiplas queries com OR/AND conforme script do pipeline.

### 3.2 Crossref (API)
- Campo: `query.bibliographic` e filtros por tipo/ano, conforme scripts.

### 3.3 Semantic Scholar (API)
- Endpoint bulk search, ano >= 2000, ordenação por citações (quando aplicável).

### 3.4 Scopus (API; quando disponível)
- Queries `TITLE-ABS-KEY(...)` com PUBYEAR > 1999 AND < 2027.

### 3.5 SciELO (ArticleMeta)
- Identificação por ISSN (collection=scl), e filtro por ocorrência das strings em:
  - `title` (article.v12)
  - `abstract` (article.v83)

### 3.6 Google Scholar (Publish or Perish)
- Execução das strings nuclear e estendido.
- Intervalo temporal: 2000–2026.
- Exportar:
  - Results CSV (item-a-item) — entra no pipeline.
  - Metrics CSV (agregado) — documentação PRISMA.

---

## 4) Registro de execução (obrigatório)
Para cada rodada, registrar em `logs/runlog.md`:
- data/hora
- fonte
- bloco (nuclear/estendido)
- string(s) executadas
- parâmetros (ano, limites)
- contagem de resultados
- arquivo exportado/gerado