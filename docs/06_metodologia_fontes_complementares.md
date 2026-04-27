# Fontes complementares — SciELO (ArticleMeta) e Google Scholar (PoP)

Este documento descreve duas fontes adicionadas para reduzir viés de cobertura em bases globais: SciELO (periódicos brasileiros) e Google Scholar (cobertura ampla, incluindo literatura cinzenta). O uso dessas fontes é compatível com PRISMA como “fontes adicionais de identificação”, desde que protocolos e decisões sejam documentados.

---

## 1) SciELO via ArticleMeta API (coleta programática)

### 1.1 Motivação
Bases globais (OpenAlex/Scopus/Crossref/Semantic Scholar) apresentam cobertura limitada de parte relevante da produção brasileira em direito, administração pública e publicações institucionais, especialmente quando:
- não há DOI,
- o periódico não está indexado internacionalmente,
- ou os metadados são incompletos.

SciELO é o principal indexador de periódicos latino-americanos com revisão por pares e, portanto, fonte complementar defensável para ampliar cobertura brasileira.

### 1.2 Por que não usar SciELO Search / OAI-PMH no Codespace
Durante a execução em ambiente Codespace, endpoints web do SciELO (ex.: `scielo.br` e `search.scielo.org`) retornaram bloqueios anti-bot (403/challenge). Para manter reprodutibilidade e evitar scraping de HTML, adotou-se o **ArticleMeta API**, que permaneceu acessível no ambiente.

### 1.3 Estratégia de coleta (reprodutível)
A coleta usa endpoints estruturados do ArticleMeta:

1) Seleção de periódicos (ISSN)
- via lista de journals (`/api/v1/journal/?collection=scl&format=json`) ou lista manual de ISSNs-alvo.

2) Listagem de artigos por periódico
- via `/api/v1/article/identifiers/?collection=scl&issn=<ISSN>&limit=<n>&offset=<n>` para obter `code` (PID SciELO).

3) Recuperação de metadados por artigo
- via `/api/v1/article/?code=<PID>&format=json`.

4) Extração de campos (mapeamento operacional)
- **Título:** `article.v12` (prioridade pt → en → es).
- **Resumo:** `article.v83` (texto em `a`, prioridade pt → en → es).
- **Autores:** `article.v10` (concatenação `n + s`).
- **Periódico:** `article.v30`.
- **Ano:** `publication_year` (top-level).
- **URL:** `fulltexts.html.*` (preferência pt/en/es).
- **DOI:** `doi` (top-level) quando existir; caso ausente, vazio.

5) Filtragem por strings
- Aplicada por substring no conjunto `title + abstract`, usando os mesmos blocos nuclear/estendido descritos em `docs/07_search_strings.md`.

### 1.4 Limitações
- A filtragem ocorre por título/resumo (metadados). Artigos cujo termo aparece apenas no texto completo podem não ser capturados.
- Registros antigos podem não conter DOI.
- A cobertura depende da lista de ISSNs selecionada e dos limites de paginação.

---

## 2) Google Scholar via Publish or Perish (PoP)

### 2.1 Motivação
Google Scholar tem alta cobertura, incluindo:
- periódicos fora das bases globais,
- literatura institucional,
- working papers e preprints,
- capítulos e outras formas (com maior ruído).

Ele é útil para reduzir subrepresentação brasileira, especialmente para termos institucionalizados (ex.: CNJ, programas, resoluções) e para localizar itens não indexados em bases tradicionais.

### 2.2 Restrições metodológicas
- Não há API pública oficial do Google Scholar.
- Resultados podem variar no tempo e por localização.
- Metadados podem conter duplicatas e inconsistências (fonte, ano, DOI ausente).

### 2.3 Protocolo adotado (reprodutível)
1) Execução das mesmas strings (blocos nuclear e estendido) no PoP.
2) Definição do intervalo temporal (2000–2026).
3) Exportação manual do **Results CSV** (lista item-a-item), e exportação do **Metrics CSV** (agregado por rodada).
4) Importação para o pipeline via script `04_import_pop_scholar.py`, padronizando colunas para o mesmo esquema do merge.

### 2.4 Integração e deduplicação
- Os registros PoP entram com `source = google_scholar_pop`.
- Deduplicação ocorre por DOI quando existente; quando ausente, por título+ano+veículo (com normalização).
- Recomenda-se manter `query_term` como `pop_nuclear` e `pop_extended` para rastreabilidade.

### 2.5 Uso analítico e mitigação de ruído
- PoP/Scholar deve ser tratado como **fonte complementar**.
- Recomenda-se separar, na discussão, resultados “peer-reviewed/indexados” vs “cinzenta/institucional”, quando necessário.
- Itens com metadados insuficientes ou evidente não-academicidade podem ser excluídos na triagem.

---

## 3) Registro de execução e rastreabilidade
Para cada rodada (SciELO/PoP), registrar:
- data/hora e commit hash,
- strings executadas,
- limites (max results / paginação),
- contagens (identificado / após dedup interno),
- arquivo gerado e caminho.

Esses registros devem ser mantidos em `logs/runlog.md`.