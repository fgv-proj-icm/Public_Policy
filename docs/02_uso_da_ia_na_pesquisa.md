# Uso da IA na execução da pesquisa

## 1. Finalidade deste capítulo

Este documento descreve como ferramentas de inteligência artificial foram utilizadas na execução da pesquisa, com foco em apoio metodológico, programação, documentação e organização do projeto.

O objetivo é registrar de forma transparente:

- em que momentos a IA foi usada;
- para quais tarefas ela foi útil;
- quais limites foram observados;
- como foi preservado o controle intelectual da pesquisa pelo pesquisador.

---

## 2. Papel da IA no projeto

A IA foi utilizada como instrumento de apoio, e não como substituta do juízo do pesquisador.

Seu uso concentrou-se em quatro frentes:

1. apoio à programação em Python;
2. apoio à estruturação do fluxo metodológico;
3. apoio à documentação e redação técnica;
4. apoio ao diagnóstico de erros, inconsistências e oportunidades de melhoria.

---

## 3. Tipos de contribuição da IA

### 3.1. Apoio à programação
A IA foi utilizada para:

- sugerir scripts Python;
- organizar pipelines por etapas;
- estruturar rotinas de coleta;
- padronizar lógica de revisão, limpeza e deduplicação;
- ajudar na criação de relatórios automatizados;
- apoiar a geração de variáveis derivadas, flags e escores.

### 3.2. Apoio à depuração
A IA ajudou na identificação e solução de problemas como:

- erros de sintaxe;
- caminhos incorretos de arquivos;
- problemas com leitura e gravação de CSVs;
- diferenças entre ambiente local e Codespaces;
- inconsistências de nomes de colunas;
- dificuldades com `.env`, Git, `.gitignore` e sincronização.

### 3.3. Apoio à metodologia
A IA contribuiu para:

- interpretar os resultados das revisões;
- propor refinamentos de strings de busca;
- sugerir critérios de inclusão e exclusão;
- ajudar a separar base mestre, corpus focal, corpus estrito e corpus final;
- propor formas de validação manual amostral.

### 3.4. Apoio à documentação
A IA também foi usada para:

- redigir README;
- organizar o documento metodológico;
- sintetizar decisões;
- estruturar capítulos e documentos auxiliares;
- transformar a evolução prática do projeto em uma narrativa metodológica coerente.

---

## 4. Ferramentas e ambientes em que a IA foi acionada

Ao longo da pesquisa, o uso de IA esteve associado a ambientes e ferramentas como:

- VS Code;
- GitHub;
- GitHub Codespaces;
- terminal local;
- APIs acadêmicas;
- ambiente Python com scripts próprios.

A IA não executou automaticamente a pesquisa de forma autônoma. As execuções sempre dependeram de ação do pesquisador, seja localmente, seja em ambiente em nuvem.

---

## 5. Tarefas em que a IA foi especialmente útil

A experiência mostrou que a IA foi especialmente útil em tarefas como:

- transformar uma ideia de fluxo metodológico em pipelines executáveis;
- dividir um processo complexo em etapas menores;
- revisar saídas de terminal e sugerir correções;
- propor estruturas de dados e regras de deduplicação;
- sugerir caminhos para lidar com ruído temático;
- ajudar a decidir quando parar de iterar em limpeza e passar à análise.

---

## 6. Limites do uso da IA

Embora útil, a IA apresentou limites claros.

### 6.1. Dependência do material disponível
A qualidade das sugestões dependeu da clareza dos logs, arquivos e saídas fornecidos pelo pesquisador.

### 6.2. Risco de excesso de iteração
Sem critério de parada, a IA tende a continuar propondo refinamentos sucessivos. Isso exigiu do pesquisador uma decisão consciente de congelar a base mestre e encerrar a fase de preparação do corpus.

### 6.3. Necessidade de validação humana
A IA não substitui:
- a avaliação substantiva de relevância temática;
- a leitura crítica dos trabalhos;
- a decisão final sobre o que integra o corpus central da pesquisa.

### 6.4. Assimetria entre metadados e substância
A IA ajuda muito com:
- estrutura;
- organização;
- automação;
- metadados.

Mas a aderência substantiva do texto ao objeto da pesquisa continua dependendo de juízo humano.

---

## 7. Princípios adotados para uso responsável

O uso da IA no projeto seguiu quatro princípios:

### 7.1. Transparência
As decisões metodológicas foram registradas em documentos e scripts verificáveis.

### 7.2. Rastreabilidade
As mudanças relevantes foram transformadas em pipelines nomeadas e arquivos versionados no GitHub.

### 7.3. Supervisão humana
Toda decisão relevante de:
- inclusão de bases;
- mudança de estratégia;
- refinamento de corpus;
- interrupção de etapas;
- definição do corpus final

foi assumida pelo pesquisador.

### 7.4. Não delegação do juízo substantivo
A IA foi usada como apoio técnico e organizacional. A interpretação final dos achados, a validação temática e a construção argumentativa permanecem sob responsabilidade do pesquisador.

---

## 8. Contribuição metodológica da IA

Em vez de ser apenas uma ferramenta de escrita ou programação, a IA acabou funcionando como:

- assistente de engenharia de pesquisa;
- apoio à organização do workflow;
- apoio à depuração de código;
- apoio à formalização metodológica.

Nesse sentido, sua maior contribuição não foi “produzir respostas prontas”, mas ajudar a transformar um processo disperso em um projeto progressivamente mais estruturado, auditável e reproduzível.

---

## 9. Riscos reconhecidos

O projeto reconhece alguns riscos associados ao uso de IA:

- automatização excessiva de critérios temáticos;
- confiança excessiva em resultados sem validação humana;
- tentação de seguir refinando o corpus indefinidamente;
- confusão entre qualidade de metadados e qualidade substantiva da literatura.

Esses riscos foram enfrentados por meio de:
- documentação explícita das decisões;
- manutenção de uma base mestre estrutural;
- separação entre corpus bibliométrico e corpus de leitura;
- previsão de validação manual amostral.

---

## 10. Conclusão

A inteligência artificial foi um instrumento importante na execução desta pesquisa, especialmente na construção técnica do pipeline, na organização metodológica e na documentação do processo.

Sua utilização permitiu:

- acelerar a programação;
- aumentar a rastreabilidade das decisões;
- reduzir retrabalho;
- transformar erros e impasses em aprendizado metodológico.

Ao mesmo tempo, o projeto preservou a centralidade do pesquisador na definição do problema, na seleção do corpus e na interpretação final dos resultados.

Assim, a IA foi usada como apoio metodológico e operacional, sem substituição do julgamento científico humano.