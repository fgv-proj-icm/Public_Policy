# Metodologia da pesquisa

## 1. Título provisório
**Análise bibliométrica das políticas judiciárias: mapeamento do estado da arte, tendências e agenda de pesquisa**

---

## 2. Objetivo geral

Construir um corpus bibliográfico robusto sobre políticas judiciárias e temas correlatos, com foco em reforma judicial, administração judicial, governança judicial, gestão de tribunais e experiências institucionais associadas ao Poder Judiciário, para realizar análises bibliométricas e subsidiar a leitura substantiva dos trabalhos mais relevantes.

---

## 3. Objetivos específicos

1. Identificar e coletar registros bibliográficos em bases acadêmicas distintas.
2. Refinar iterativamente as estratégias de busca para reduzir ruído temático.
3. Unificar, limpar e deduplicar os registros coletados.
4. Construir diferentes camadas de corpus:
   - base mestre estrutural;
   - corpus focal temático;
   - corpus estrito;
   - corpus bibliométrico final;
   - corpus de leitura.
5. Realizar análises bibliométricas descritivas e exploratórias.
6. Selecionar um subconjunto de trabalhos para leitura substantiva aprofundada.
7. Identificar tendências, lacunas e agendas de pesquisa.

---

## 4. Delimitação temática

A pesquisa adota como núcleo temático os seguintes eixos:

- políticas judiciárias;
- administração judicial;
- governança judicial;
- gestão de tribunais;
- reforma judicial;
- desempenho judicial;
- eficiência judicial;
- gestão processual;
- transformação digital da justiça;
- Conselho Nacional de Justiça e experiências brasileiras relacionadas.

Temas de fronteira, como judicial review, acesso à justiça, política judicial e judicialização, podem aparecer no corpus, mas não constituem automaticamente o núcleo central da análise. A permanência desses registros depende da aderência efetiva ao foco do estudo.

---

## 5. Bases de dados utilizadas

A coleta foi realizada por base, de forma separada, com revisão metodológica sucessiva:

- OpenAlex
- Crossref
- Scopus
- Semantic Scholar

Cada base foi tratada como uma fonte com comportamento próprio, tanto em cobertura quanto em qualidade de metadados. Por essa razão, o projeto não partiu de uma coleta unificada, mas de uma estratégia de aprendizagem por base.

---

## 6. Estratégia metodológica geral

A pesquisa foi estruturada em camadas sucessivas:

1. coleta individual por base;
2. revisão exploratória dos resultados;
3. refino das queries e filtros;
4. unificação das bases refinadas;
5. auditoria reprodutível da base unificada;
6. limpeza final e padronização dos metadados;
7. construção da base mestre estrutural;
8. derivação de camadas progressivamente mais focalizadas do corpus;
9. definição do corpus bibliométrico final;
10. definição de uma agenda de leitura e de um corpus substantivo final.

Essa arquitetura foi adotada para evitar duas falhas:
- depender excessivamente da primeira string de busca;
- realizar análise bibliométrica em base ainda contaminada por duplicação, ruído e heterogeneidade entre fontes.

---

## 7. Estratégias de busca

As buscas iniciais foram amplas e serviram como exploração. Após as primeiras revisões, passaram a ser priorizadas expressões mais diretamente ligadas ao objeto, como:

- `judicial policy`
- `judicial policies`
- `judicial governance`
- `judicial administration`
- `court administration`
- `court governance`
- `judicial reform`
- `política judiciária`
- `políticas judiciárias`
- `governança judicial`
- `administração judiciária`
- `reforma do judiciário`
- `reforma judicial`
- `Conselho Nacional de Justiça`

A estratégia final abandonou combinações excessivamente amplas, que geravam excesso de ruído, e passou a favorecer conjuntos de queries mais específicas e auditáveis.

---

## 8. Revisão e refino por base

### 8.1. OpenAlex
O OpenAlex funcionou como principal laboratório de aprendizado metodológico. A revisão mostrou a necessidade de:
- abandonar termos muito amplos;
- excluir fontes e repositórios periféricos;
- usar âncoras temáticas mais fortes;
- deduplicar em camadas.

### 8.2. Crossref
O Crossref foi refeito com foco em:
- `journal-article`;
- DOI;
- periódico;
- autores;
- maior aderência temática.

### 8.3. Scopus
No Scopus, a estratégia se mostrou mais estável com queries curtas e executadas separadamente, com refinamento posterior em Python.

### 8.4. Semantic Scholar
O Semantic Scholar exigiu duas rodadas de refino, culminando em uma versão `core`, mais conservadora, com redução de ruído e exigência mínima de metadados e âncoras temáticas.

---

## 9. Unificação das bases

Após o refinamento individual, os registros foram integrados em uma base unificada.

### Regras principais de deduplicação na unificação
1. DOI normalizado;
2. fallback por título + ano + periódico.

Essa etapa resultou em uma base unificada rastreável, que serviu como ponto de partida para a auditoria formal.

---

## 10. Auditoria reprodutível

A base unificada passou por auditoria reprodutível para medir:

- missingness por coluna;
- cobertura por fonte;
- duplicatas por DOI;
- duplicatas sem DOI;
- distribuição de metadados por base.

O principal problema encontrado foi a duplicação residual causada por DOI mal normalizado. Isso motivou uma etapa formal de limpeza final.

---

## 11. Limpeza final e base analysis-ready

Após a auditoria, foi implementada uma limpeza final com:

- normalização forte de DOI;
- padronização de campos textuais;
- criação de escores de completude;
- escolha do melhor registro por prioridade de metadados;
- harmonização inicial de tipo documental;
- criação de variáveis derivadas e flags analíticas.

A partir daí foi construída a base `analysis-ready`, evoluindo até uma **base mestre estrutural**, que passou a funcionar como repositório definitivo de trabalho.

---

## 12. Base mestre estrutural

A base mestre estrutural representa o repositório central do projeto.

### Funções da base mestre
- preservar todos os registros já limpos e auditados;
- manter a rastreabilidade das fontes;
- permitir a derivação de recortes específicos sem retrabalho na estrutura central;
- servir de base para futuras análises e validações.

### Decisão metodológica
A base mestre foi congelada como estrutura principal. As reduções posteriores do corpus passaram a ocorrer apenas em camadas derivadas.

---

## 13. Construção progressiva do corpus

A partir da base mestre, o projeto passou a operar com diferentes camadas:

### 13.1. Corpus amplo
Recorte inicial defensável, ainda relativamente amplo, para reduzir ruído sem apertar em excesso o foco substantivo.

### 13.2. Corpus focal
Recorte orientado ao núcleo da pesquisa: políticas judiciárias, administração judicial, governança judicial e reforma judicial.

### 13.3. Corpus estrito
Recorte mais seletivo, construído para aumentar a aderência substantiva ao objeto principal.

### 13.4. Agenda rebalanceada de leitura
Seleção reorganizada para reduzir o domínio excessivo de uma única base no topo do ranking.

### 13.5. Corpus bibliométrico final
Recorte final robusto para as análises bibliométricas.

### 13.6. Corpus de leitura curado
Recorte orientado à leitura substantiva, ainda sujeito a validação manual antes de ser considerado fechado.

---

## 14. Corpus bibliométrico final

O corpus bibliométrico final foi construído para ser:

- amplo o suficiente para análise bibliométrica;
- restrito o suficiente para preservar coerência temática;
- auditável;
- sem duplicatas residuais detectáveis nos critérios adotados.

### Critérios gerais de permanência
- tipo documental compatível (`article` ou `review`);
- periódico identificado;
- exclusão de fontes suspeitas ou periféricas;
- foco temático compatível com:
  - `policy_admin_governance`
  - `reform`
  - `cnj_brazil`
- score mínimo de elegibilidade;
- deduplicação final controlada.

### Situação metodológica
Este corpus pode ser tratado como **corpus final para análise bibliométrica**.

---

## 15. Corpus de leitura

O corpus de leitura foi derivado da agenda rebalanceada e do corpus bibliométrico final.

### Finalidade
Selecionar trabalhos com maior probabilidade de utilidade para:
- leitura aprofundada;
- identificação de achados;
- construção de agenda de pesquisa;
- redação analítica do estudo.

### Situação metodológica
Esse corpus já constitui uma agenda curada importante, mas ainda requer validação manual curta antes de ser considerado corpus substantivo definitivo.

---

## 16. Validação manual

A metodologia prevê uma etapa de validação manual amostral, com duas amostras:

1. registros incluídos no corpus final;
2. registros excluídos na última rodada de curadoria.

### Rotulagem sugerida
Cada item deverá ser classificado como:
- relevante;
- parcialmente relevante;
- irrelevante.

### Finalidade
Evitar refinamentos automáticos indefinidos e estabelecer um critério de parada metodologicamente defensável.

---

## 17. Análises bibliométricas previstas

A próxima fase do projeto consiste em realizar análises bibliométricas a partir do corpus bibliométrico final.

### 17.1. Análises descritivas
- evolução temporal das publicações;
- distribuição por tipo documental;
- distribuição por fonte;
- distribuição por periódicos;
- distribuição por idioma, quando possível;
- distribuição por país, instituição e autoria, quando houver metadados suficientes.

### 17.2. Análises temáticas
- frequência de termos por título, resumo e palavras-chave, quando disponíveis;
- comparação entre subtemas:
  - reforma judicial;
  - administração judicial;
  - governança judicial;
  - políticas judiciárias;
  - experiências brasileiras/CNJ;
- identificação de tópicos dominantes e temas emergentes.

### 17.3. Análises de impacto
- ranking de trabalhos mais citados;
- ranking de periódicos mais recorrentes;
- comparação entre citações e centralidade temática;
- distinção entre literatura fundacional e literatura recente.

### 17.4. Análises relacionais
- coocorrência de termos;
- redes entre autores, instituições e periódicos, quando os metadados permitirem;
- relações entre clusters temáticos e anos de publicação.

### 17.5. Análises para seleção de leitura
- seleção dos artigos mais centrais por subtema;
- equilíbrio entre textos fundacionais, recentes e metodologicamente relevantes;
- construção da agenda de leitura final.

---

## 18. Limitações

As principais limitações desta metodologia são:

- cobertura desigual entre bases;
- metadados incompletos em parte dos registros;
- diferenças entre critérios de indexação das bases;
- presença de temas de fronteira que exigem leitura humana para julgamento final;
- assimetria entre qualidade de metadados e qualidade substantiva do texto.

---

## 19. Integração da curadoria assistida por IA

Após a construção do corpus bibliométrico automático (`bibliometric_corpus_final_v2.csv`), foi realizada uma etapa adicional de curadoria assistida por IA, a partir da leitura do arquivo `reading_corpus_final_curated` por um modelo externo, sem uso de PDFs e com base exclusivamente nos metadados disponíveis.

Essa curadoria gerou o arquivo:

- `data/final/corpus_curated_v3_claude.csv`

O objetivo dessa etapa foi produzir uma triagem fina dos registros, classificando-os em três grupos:
- manter;
- revisar;
- excluir.

A integração entre o corpus automático e a curadoria do Claude foi operacionalizada por meio de uma pipeline específica de integração final, resultando em uma nova camada híbrida de decisão, combinando:
- limpeza e deduplicação automáticas;
- curadoria temática assistida por IA;
- preservação da rastreabilidade metodológica.

---

## 20. Fechamento do corpus bibliométrico final

A integração da curadoria do Claude produziu o corpus bibliométrico final oficial do projeto:

- `data/final/bibliometric_corpus_final_v3.csv`

Também foram gerados os seguintes arquivos auxiliares:

- `data/final/bibliometric_corpus_review_queue.csv`
- `data/final/bibliometric_corpus_excluded.csv`
- `data/final/reading_corpus_final_v3.csv`
- `data/final/reading_corpus_final_v3_top80.csv`

### 20.1. Resultado da integração
A integração final produziu:

- `bibliometric_corpus_final_v3.csv`: 1604 registros
- `bibliometric_corpus_review_queue.csv`: 95 registros
- `bibliometric_corpus_excluded.csv`: 165 registros

A distribuição temática do corpus final v3 ficou assim:
- `policy_admin_governance`: 725
- `reform`: 637
- `cnj_brazil`: 242

A distribuição por fonte ficou assim:
- `crossref_results_refined.csv`: 700
- `openalex_results_refined.csv`: 499
- `semantic_scholar_results_core.csv`: 385
- `scopus_results_refined.csv`: 20

### 20.2. Padrões de exclusão
As exclusões ficaram concentradas principalmente em:
- `judicial_review_periférico`
- `tema_tangencial`
- `provável_ruído`
- `provável_duplicata`

Isso indica que a curadoria final conseguiu reduzir o ruído residual que ainda permanecia após a limpeza automática.

### 20.3. Decisão metodológica
A partir desta etapa, o arquivo oficial para análise bibliométrica passa a ser:

- `data/final/bibliometric_corpus_final_v3.csv`

O arquivo `v2` permanece apenas como baseline automático e referência metodológica do estágio anterior.

---

## 21. Situação da fila de revisão

Os 95 registros classificados como `revisar` foram preservados em:

- `data/final/bibliometric_corpus_review_queue.csv`

Essa fila cumpre duas funções metodológicas:

1. registrar explicitamente a zona residual de incerteza do corpus;
2. evitar que a definição do corpus final dependa de exclusões automáticas excessivamente rígidas.

Esses registros não integram o corpus bibliométrico final oficial, mas permanecem disponíveis para eventual reavaliação posterior.

---

## 22. Situação do corpus de leitura

A integração final também produziu:

- `data/final/reading_corpus_final_v3.csv`
- `data/final/reading_corpus_final_v3_top80.csv`

### 22.1. Natureza do corpus de leitura
O `reading_corpus_final_v3.csv` representa o universo curado de leitura derivado do corpus final.

Já o `reading_corpus_final_v3_top80.csv` representa uma agenda priorizada de leitura, construída para orientar a etapa substantiva da pesquisa.

### 22.2. Limite metodológico do top80
Embora o `top80` tenha sido útil para organizar a leitura prioritária, ele não deve ser tratado automaticamente como corpus substantivo final fechado.

Isso se deve ao fato de que:
- sua composição por fonte ainda é assimétrica;
- alguns itens de fronteira temática permanecem entre os primeiros colocados;
- a definição do corpus de leitura ainda depende de uma triagem humana curta.

### 22.3. Decisão metodológica
Assim, o `reading_corpus_final_v3_top80.csv` deve ser tratado como:

- agenda priorizada de leitura;
- não como corpus substantivo final definitivo.

---

## 23. Situação consolidada do projeto

Neste ponto, o projeto passa a operar com a seguinte arquitetura final:

### 23.1. Base mestre estrutural
- `data/final/unified_base_analysis_ready_v3.csv`

### 23.2. Corpus bibliométrico final oficial
- `data/final/bibliometric_corpus_final_v3.csv`

### 23.3. Zona de incerteza documentada
- `data/final/bibliometric_corpus_review_queue.csv`

### 23.4. Excluídos rastreados
- `data/final/bibliometric_corpus_excluded.csv`

### 23.5. Corpus de leitura curado
- `data/final/reading_corpus_final_v3.csv`

### 23.6. Agenda priorizada de leitura
- `data/final/reading_corpus_final_v3_top80.csv`

Essa estrutura encerra a fase de preparação do corpus bibliográfico e estabelece, de forma metodologicamente defensável, os arquivos oficiais a serem usados na fase analítica.

---

## 24. Decisão metodológica final desta fase

A fase de definição do corpus pode ser considerada encerrada.

A decisão metodológica consolidada é:

1. congelar a base mestre estrutural;
2. adotar `bibliometric_corpus_final_v3.csv` como corpus bibliométrico oficial;
3. preservar a fila de revisão e os excluídos como documentação metodológica;
4. tratar o `reading_corpus_final_v3_top80.csv` como agenda provisória de leitura;
5. iniciar a fase bibliométrica a partir do corpus final v3.

---

## 25. Próximos passos

A próxima fase da pesquisa deixa de ser uma fase de coleta e curadoria ampla e passa a ser uma fase analítica.

Os próximos passos são:

1. realizar as análises bibliométricas sobre `bibliometric_corpus_final_v3.csv`;
2. fazer uma triagem humana curta do `reading_corpus_final_v3_top80.csv`;
3. derivar, a partir dessa triagem, o corpus substantivo final de leitura;
4. iniciar a redação dos resultados bibliométricos e da síntese analítica da literatura.

---

## 26. Análises bibliométricas previstas a partir do corpus final v3

As análises bibliométricas a serem realizadas a partir de `bibliometric_corpus_final_v3.csv` incluem:

### 26.1. Estatísticas descritivas
- publicações por ano;
- distribuição por tipo documental;
- distribuição por fonte;
- distribuição por periódicos;
- distribuição por idioma, quando houver metadados suficientes.

### 26.2. Análises temáticas
- frequência de termos;
- distribuição por subtemas;
- comparação entre:
  - reforma judicial;
  - administração judicial;
  - governança judicial;
  - políticas judiciárias;
  - experiências brasileiras/CNJ.

### 26.3. Análises de impacto
- artigos mais citados;
- periódicos mais recorrentes;
- literatura fundacional;
- produção recente.

### 26.4. Análises relacionais
- coocorrência de termos;
- relações entre periódicos;
- relações entre temas e anos;
- redes de autores e instituições, quando os metadados permitirem.

### 26.5. Função da bibliometria nesta pesquisa
A bibliometria será utilizada para:
- mapear o estado da arte;
- identificar núcleos temáticos e editoriais;
- apoiar a seleção dos trabalhos centrais para leitura aprofundada;
- subsidiar a construção da agenda de pesquisa final.