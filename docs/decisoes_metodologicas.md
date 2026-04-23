# Decisões metodológicas e revisão das estratégias de coleta

## Objetivo
Documentar as revisões feitas nas strings de busca, nos filtros e na forma de coleta nas bases bibliográficas, com foco em aprendizagem, transparência e reprodutibilidade.

---

## 1. Estratégia inicial

A coleta começou com scripts separados por base, priorizando:
- execução individual por API;
- salvamento em CSV por base;
- revisão exploratória antes de unir os resultados.

A primeira lógica de busca foi ampla, com termos como:
- `"judicial policy"`
- `"judicial reform"`
- `"public policy" AND (judiciary OR courts OR judicial)`
- `"Conselho Nacional de Justiça" OR CNJ`

### Problema encontrado
A estratégia inicial trouxe ruído temático e institucional excessivo, incluindo:
- documentos fora do foco principal;
- repositórios e fontes pouco adequadas para o corpus principal;
- ocorrências por ambiguidade de siglas e palavras amplas.

---

## 2. Aprendizados com a revisão do OpenAlex

A revisão exploratória do OpenAlex mostrou:

- 10.162 linhas na coleta ampla;
- 447 duplicatas por `openalex_id`;
- 304 duplicatas por DOI;
- excesso de ruído em queries amplas;
- forte presença de fontes como SSRN, Zenodo, LA Referencia e Dialnet;
- queries amplas como `"public policy" AND (judiciary OR courts OR judicial)` geraram muitos resultados pouco relevantes.

### Exemplo de ruído observado
- áreas fora do tema principal;
- resultados capturados por termos genéricos como `public policy`;
- ruído por siglas como `CNJ`.

---

## 3. Revisão metodológica adotada

A partir da análise do OpenAlex, a estratégia foi refinada com as seguintes decisões:

### 3.1. Redução do escopo sem perder cobertura
Foram priorizadas expressões mais diretamente ligadas ao tema:
- `"judicial policy"`
- `"judicial policies"`
- `"judicial governance"`
- `"judicial administration"`
- `"court administration"`
- `"court governance"`
- `"judicial reform"`
- `"política judiciária"`
- `"políticas judiciárias"`
- `"governança judicial"`
- `"administração judiciária"`
- `"reforma do judiciário"`
- `"reforma judicial"`
- `"Conselho Nacional de Justiça"`

### 3.2. Abandono de strings amplas demais
Foram removidas ou despriorizadas expressões como:
- `"public policy" AND (judiciary OR courts OR judicial)`
- `"políticas públicas" AND (judiciário OR judicial OR justiça)`
- `"CNJ"` isolado

### 3.3. Uso de âncoras temáticas
Passou-se a exigir presença de âncoras semânticas relacionadas ao sistema de justiça, por exemplo:
- `judicial`
- `judiciary`
- `court`
- `courts`
- `tribunal`
- `judiciário`
- `judiciária`
- `governança judicial`
- `administração judiciária`

### 3.4. Filtragem de fontes problemáticas
Foram marcadas como fontes de baixo interesse para o corpus principal:
- SSRN
- Zenodo
- LA Referencia
- Dialnet
- eYLS
- Choice Reviews
- repositórios institucionais genéricos

### 3.5. Deduplicação em camadas
A deduplicação passou a seguir esta ordem:
1. `openalex_id`
2. DOI normalizado
3. `title + publication_year + journal`

---

## 4. Resultado da revisão no OpenAlex

A versão refinada reduziu a base para 2.797 registros, com melhora clara de foco temático em relação à coleta inicial. Ainda restaram alguns casos de ruído, mas o corpus ficou muito mais útil para a etapa seguinte. 

---

## 5. Decisão para as próximas bases

Com base no OpenAlex, as próximas coletas devem seguir estas regras:

### Crossref
- evitar strings excessivamente amplas;
- priorizar expressões centrais do tema;
- revisar os principais periódicos encontrados;
- inspecionar resultados por query.

### Scopus
- usar string booleana mais controlada;
- começar com busca em título, resumo e palavras-chave;
- revisar volume e qualidade antes de ampliar.

---

## 6. Regra operacional daqui em diante

Cada base deve seguir este fluxo:
1. coletar;
2. revisar;
3. refinar, se necessário;
4. salvar versão final da base da fonte;
5. só então unir com as demais.

---

## 7. Situação atual da pipeline

Concluído:
- Crossref inicial
- OpenAlex inicial
- revisão exploratória do OpenAlex
- OpenAlex refinado
- revisão do OpenAlex refinado

Próximos passos:
- refazer Crossref com estratégia refinada;
- revisar Crossref;
- coletar Scopus;
- revisar Scopus;
- criar base unificada;
- pausar para análise.

## 8. Aprendizados com a revisão do Scopus

A coleta inicial do Scopus, já em formato de queries curtas por termo, funcionou corretamente após abandonar a string única longa que gerava erro 400.

### Resultado obtido
- 687 registros após deduplicação;
- predominância das queries:
  - `judicial review`
  - `judicial reform`
  - `judicial governance`
  - `judicial administration`
  - `access to justice`

### Principais achados da revisão
- o Scopus respondeu bem a queries curtas e separadas;
- a estratégia por query individual foi mais estável que uma string grande;
- ainda houve ruído temático, especialmente em resultados ligados a “governance” de forma ampla;
- alguns periódicos relevantes apareceram com força, como:
  - *International Journal for Court Administration*
  - *German Law Journal*
  - *Access to Justice in Eastern Europe*
- também apareceram fontes menos centrais ao objeto principal, indicando necessidade de uma segunda filtragem do resultado do Scopus antes da unificação.

### Decisão metodológica
O corpus do Scopus não deve ir diretamente para a base unificada. Antes, deve passar por:
1. filtragem temática por âncoras;
2. remoção de termos e periódicos ruidosos;
3. nova revisão exploratória do CSV refinado.

### Aprendizado prático
No Scopus, a melhor abordagem até aqui foi:
- queries curtas;
- uma por vez;
- revisão por `query_term`;
- refinamento posterior em Python.

# Antes de unificar a base...

## 9. Inclusão do Semantic Scholar

Antes da unificação das bases, foi adicionada uma coleta independente via Semantic Scholar API.

### Motivo
A inclusão do Semantic Scholar amplia a cobertura bibliográfica e permite comparar:
- resultados por base;
- comportamento das strings de busca;
- presença de metadados como resumo, citações e DOI.

### Estratégia adotada
A coleta no Semantic Scholar foi implementada com:
- API key via header `x-api-key`;
- queries curtas por termo;
- uso do endpoint de busca em lote (`paper/search/bulk`);
- paginação por `token`;
- limitação de campos retornados;
- pausa entre requisições para respeitar a taxa da API.

### Regra metodológica
O Semantic Scholar entra no mesmo fluxo das demais bases:
1. coletar;
2. revisar;
3. refinar, se necessário;
4. só então unificar.

## 10. Aprendizados com a revisão do Semantic Scholar

A coleta no Semantic Scholar funcionou tecnicamente, mas retornou uma base ampla demais para entrar diretamente no corpus unificado.

### Resultado observado
- 13.368 registros após deduplicação inicial;
- forte concentração nas queries:
  - `"judicial review"`
  - `"access to justice"`
  - `"judicial reform"`
- grande volume de registros sem periódico identificado (`journal = N/D`);
- presença de obras muito amplas ou periféricas ao objeto central.

### Problemas identificados
- excesso de resultados gerais em teoria política, desenvolvimento e governança;
- ruído gerado principalmente por `"access to justice"` e por usos amplos de `"judicial review"`;
- grande número de registros sem metadados completos de periódico.

### Decisão metodológica
O Semantic Scholar passará por uma etapa adicional de refino antes da unificação, com:
1. filtros por âncoras temáticas;
2. exclusão de títulos e periódicos claramente periféricos;
3. nova revisão exploratória do CSV refinado.

### Regra operacional
O arquivo `semantic_scholar_results.csv` não entra diretamente na base unificada.
A unificação deve usar apenas `semantic_scholar_results_refined.csv`.

### Revisão final do Semantic Scholar (core)
Após o segundo refino conservador, o Semantic Scholar foi reduzido para 2754 registros.

Características observadas:
- predominância de `judicial review` e `judicial reform`;
- presença de periódicos mais aderentes ao tema;
- permanência de registros sem periódico identificado (`N/D`), mas em volume aceitável para entrada controlada na base unificada.

Decisão:
- usar `semantic_scholar_results_core.csv` na unificação;
- não usar `semantic_scholar_results.csv` bruto nem a versão apenas `refined`.

## 11. Unificação final das bases

Foram unificadas as bases refinadas de:
- OpenAlex
- Crossref
- Scopus
- Semantic Scholar (versão core)

### Resultado da unificação
- total bruto unificado: 7161
- total final deduplicado: 6893

### Regra de deduplicação usada
1. DOI normalizado
2. título + ano + periódico

### Situação da pesquisa
A pipeline foi interrompida nesta etapa para permitir:
- inspeção qualitativa da base consolidada;
- avaliação dos registros mais citados;
- definição da próxima fase de triagem e análise.

## 12. Base final pronta para análise (v1)

Após auditoria, normalização forte de DOI, deduplicação e construção da camada analítica, foi gerada a base:

`data/final/unified_base_analysis_ready.csv`

### Resultado final da v1
- linhas: 5968
- colunas: 43

### Transformações aplicadas
- normalização forte de DOI;
- deduplicação por DOI limpo;
- fallback por título + ano + periódico para registros sem DOI;
- harmonização inicial de `type`;
- criação de campos analíticos:
  - `record_id`
  - `doi_clean`
  - `title_clean`
  - `journal_clean`
  - `type_clean`
  - `language_clean`
  - `citation_count_log1p`
  - flags de completude

### Situação da v1
A base `analysis_ready` passou a funcionar como versão analítica inicial, adequada para:
- auditoria reprodutível;
- inspeção de cobertura por fonte;
- cálculo de duplicatas;
- preparação da etapa seguinte de curadoria.

### Ressalvas registradas
Mesmo após a limpeza principal, permaneceram pontos que justificaram nova rodada de melhoria:
- `journal = N/D` ainda elevado;
- `language_clean = nd` predominante;
- `type_clean` ainda com categorias compostas;
- necessidade de uma camada explícita de relevância temática.

## 13. Auditoria reprodutível e limpeza documentada

Após a geração da base `unified_base.csv`, foi implementada uma etapa formal de auditoria reprodutível e limpeza final.

### 13.1. Auditoria da base unificada
Foram criados relatórios automáticos para:
- missingness por coluna;
- distribuição por fonte;
- duplicatas por DOI limpo;
- duplicatas sem DOI;
- cobertura de metadados por fonte.

Arquivos gerados:
- `data/final/audit/overview.csv`
- `data/final/audit/missingness_by_column.csv`
- `data/final/audit/rows_by_source_file.csv`
- `data/final/audit/duplicate_doi_candidates.csv`
- `data/final/audit/duplicate_no_doi_candidates.csv`
- `data/final/audit/duplicates_summary.csv`
- `data/final/audit/coverage_by_source.csv`

### 13.2. Resultado da auditoria
A auditoria confirmou que o principal problema residual da base unificada estava na duplicação por DOI mal normalizado.

Resultado observado:
- base unificada antes da limpeza final: 6893 linhas;
- registros com DOI: 5819;
- DOIs limpos únicos: 4894;
- registros em grupos duplicados por DOI: 1850;
- registros em grupos duplicados sem DOI no fallback `title + year + journal`: 0.

### 13.3. Limpeza final documentada
A limpeza final foi implementada com a seguinte regra:

1. normalização forte de DOI;
2. escolha do “melhor registro” por DOI, usando:
   - maior `completeness_score`;
   - maior `source_priority`;
   - maior `citation_count_unified`;
3. fallback por `title + year + journal` apenas para registros sem DOI.

### 13.4. Resultado da limpeza final
A base caiu de 6893 para 5968 registros.

Resumo:
- total inicial: 6893
- removidos por DOI limpo: 925
- removidos por fallback sem DOI: 0
- total final: 5968

### 13.5. Leitura metodológica
A limpeza confirmou que a deduplicação principal do projeto deveria ser ancorada em DOI limpo, e não apenas em identificadores internos de cada base.

## 14. Segunda camada de curadoria da base analítica

Após a geração da `unified_base_analysis_ready.csv`, foi implementada uma nova camada de melhoria para tornar a base mais estável para análise substantiva.

### 14.1. Deduplicação final de registros sem DOI
Foi criada uma regra adicional para registros sem DOI:
- agrupamento por `title_clean + year_clean`;
- manutenção da linha mais informativa, usando:
  - `completeness_score`
  - presença de `journal`
  - presença de `url`
  - `source_priority`
  - `citation_count_unified`

### 14.2. Normalização editorial de `query_term`
Foi criada a coluna `query_term_clean`, com padronização das queries oriundas de diferentes bases.

Objetivo:
- eliminar diferenças meramente editoriais;
- estabilizar tabelas e gráficos por termo de busca;
- reduzir a heterogeneidade entre strings como `TITLE-ABS-KEY(...)` e termos simples entre aspas.

### 14.3. Harmonização de tipo documental
Foi criada a coluna `primary_type`, derivada de `type_clean`, além de flags auxiliares:
- `is_article`
- `is_review`
- `is_book_chapter`
- `is_conference`

A regra adotada foi determinística e priorizou categorias centrais:
- `review` quando presente;
- `article` para variantes de journal article;
- `book_chapter`, `conference`, `editorial`, `book`, `note`, `erratum` quando aplicável.

### 14.4. Motivação metodológica
Essa etapa foi necessária porque a base ainda apresentava:
- queries heterogêneas;
- tipos compostos;
- ruído editorial remanescente;
- necessidade de uma camada mais adequada para estatística descritiva.

## 15. Camada de relevância temática rastreável

A etapa final desta rodada consistiu na criação de uma camada explícita de relevância temática, sem exclusão automática dos registros.

### 15.1. Regra adotada
Foram criadas as colunas:
- `relevance_flag`
- `relevance_reason`

A lógica foi:

- `relevance_flag = 1` quando o registro apresentava âncoras temáticas em `title` ou `journal`;
- `relevance_flag = 1` também quando os `concepts` continham termos core do campo jurídico-judicial;
- `relevance_flag = 0` quando não havia âncora suficiente ou quando havia sinal claro de periódico irrelevante.

### 15.2. Motivo da escolha
A estratégia adotada foi de marcação, e não de exclusão automática, por três razões:

1. parte do ruído pode representar interseções legítimas com temas vizinhos;
2. a decisão final de inclusão substantiva ainda depende de leitura analítica;
3. a rastreabilidade da decisão é mais importante do que uma filtragem excessivamente agressiva nesta fase.

### 15.3. Resultado metodológico
Com isso, a base passou a ter duas camadas:
- uma camada estrutural, voltada à identidade e limpeza dos registros;
- uma camada temática, voltada à relevância analítica.

### 15.4. Situação atual da pesquisa
A base resultante desta etapa passa a ser:

`data/final/unified_base_analysis_ready_v2.csv`

Ela representa a versão mais avançada do corpus até o momento, pronta para:
- triagem temática fina;
- estatísticas descritivas;
- preparação de corpus final de leitura;
- construção do funil analítico final.

## 16. Próxima etapa planejada

A próxima fase do projeto não é mais de coleta, mas de redução analítica do corpus.

Os passos previstos são:
1. revisão da distribuição de `primary_type`;
2. uso combinado de `relevance_flag` e `query_term_clean`;
3. eventual exclusão ou reclassificação de periódicos claramente periféricos;
4. construção de um corpus final reduzido e defendável para leitura substantiva.