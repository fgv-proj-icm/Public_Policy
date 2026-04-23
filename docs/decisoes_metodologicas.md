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