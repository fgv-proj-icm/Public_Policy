# Public_Policy

Repositório da pesquisa sobre **política judiciária como campo emergente**, com foco na identificação, triagem e análise bibliométrica da produção acadêmica que se nomeia explicitamente como *política judiciária*, *política judicial* ou *judicial policy*.

## Objetivo

O projeto busca responder à seguinte pergunta:

> existe um campo de pesquisa que se apresenta explicitamente como política judiciária, política judicial ou *judicial policy*, e, se existe, qual é sua configuração bibliométrica?

Para isso, a pesquisa combina coleta multibase, deduplicação cross-base, triagem inspirada em PRISMA, organização do corpus em dois anéis e produção de relatório final em Quarto.

## Estratégia metodológica

A arquitetura analítica do projeto distingue dois níveis:

- **Anel nuclear**: registros que utilizam explicitamente o vocabulário do campo em título, resumo ou palavras-chave.
- **Anel estendido**: literatura cognata e adjacente sobre administração judicial, governança judicial, reforma judicial, gestão de tribunais e temas próximos.

A coleta foi realizada em quatro bases:

- OpenAlex
- Scopus
- Semantic Scholar
- Crossref

A deduplicação foi feita por DOI normalizado e, quando necessário, por título normalizado, ano e periódico.

## Resultados consolidados do corpus

O fluxo consolidado da pesquisa chegou aos seguintes números:

- **7.161** registros identificados
- **1.193** duplicatas removidas
- **5.968** registros triados
- **1.042** registros excluídos
- **4.926** registros incluídos

Corpus final:

- **115** registros no **anel nuclear**
- **4.811** registros no **anel estendido**

## Estrutura do repositório

```text
Public_Policy/
├── data/
│   ├── raw/
│   ├── interim/
│   └── final/
├── docs/
├── src/
│   └── pipelines/
├── relatorio_bibliometrico_politica_judiciaria.qmd
├── references.bib
├── abnt.csl
└── README.md
```

## Arquivos principais
Corpus final
data/final/corpus_nuclear.csv
data/final/corpus_extended.csv
data/final/corpus_complete.csv
Relatório
relatorio_bibliometrico_politica_judiciaria.qmd
Referências e estilo
references.bib
abnt.csl
Documentação
docs/01_metodologia.md
docs/03_proximos_passos.md
docs/04_prisma_flow.md
Pipeline principal

### A fase consolidada do projeto foi estruturada em torno dos seguintes scripts:

06_merge_cross_base.py
07_dedup_cross_base.py
08_screen_prisma.py
08d_final_nuclear_adjustment.py
09_prisma_flow.py
10_export_bibliometrix.py
Como reproduzir

### Na raiz do projeto:

python src/pipelines/06_merge_cross_base.py
python src/pipelines/07_dedup_cross_base.py
python src/pipelines/08_screen_prisma.py
python src/pipelines/08d_final_nuclear_adjustment.py
python src/pipelines/09_prisma_flow.py
python src/pipelines/10_export_bibliometrix.py

### Para renderizar o relatório em Word:

quarto render relatorio_bibliometrico_politica_judiciaria.qmd --to docx

## Relatório final

O relatório principal foi desenvolvido em Quarto e ajustado para renderização em DOCX, com:

leitura robusta dos dados consolidados;
tabelas compatíveis com Word;
gráficos estáticos;
referências bibliográficas em padrão ABNT.
Uso de inteligência artificial

## Ferramentas de inteligência artificial foram utilizadas como apoio técnico e metodológico em tarefas como:

organização de pipelines;
depuração de scripts;
estruturação documental;
revisão técnica do relatório.

As decisões substantivas da pesquisa — definição do problema, critérios de triagem, delimitação do corpus e interpretação dos resultados — permaneceram sob responsabilidade do pesquisador.

## Situação atual

O projeto se encontra com:

corpus final consolidado;
fluxo PRISMA estabilizado;
documentação metodológica atualizada;
relatório bibliométrico funcional em Quarto;
repositório sincronizado com o GitHub.