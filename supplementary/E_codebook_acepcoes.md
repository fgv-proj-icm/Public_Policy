# E — Codebook da classificação por acepção

Regra de codificação que sustenta a subseção *Polissemia como achado bibliométrico* do
manuscrito e a tabela "Distribuição das acepções no anel lexical e efeito da restrição
programática". Implementada em `src/utils/acepcoes.py`, executada por
`src/pipelines/10b_classify_acepcoes.py`.

A classificação é **determinística**: regra lexical aplicada por script sobre campos
estruturados, sem julgamento de codificador. Mesma entrada, mesma saída. Não há
concordância entre avaliadores a estimar; há, em contrapartida, os limites de
cobertura declarados ao final.

## Unidade de análise e populações

| População | N | Definição |
| --- | ---: | --- |
| **Anel lexical** | 170 | Registros que empregam expressamente o rótulo investigado, **antes** da restrição à acepção programática aplicada por `08c_reclassify_nuclear.py`. É a população em que a polissemia é observável, porque nela as três acepções convivem |
| **Anel nuclear final** | 115 | Resultado da restrição, usado no restante do manuscrito. Por construção quase não contém registros comportamentais |

A distinção é essencial: classificar apenas o anel final não demonstraria polissemia
alguma, porque os registros comportamentais já foram movidos para o anel estendido.
O contraste entre as duas populações é o que torna auditável a afirmação de que a
cartografia **restringe** o que o índice pode medir.

Nenhum registro muda de anel nesta etapa. A composição do corpus congelado permanece
intacta; esta é uma camada analítica sobre ela.

## Campos consultados e ordem de prioridade

| Ordem | Campo | Papel |
| --- | --- | --- |
| 1 | `title` | Evidência primária |
| 2 | `abstract` | Consultado só quando o título não carrega sinal |
| 3 | `journal` | Último recurso; tradição editorial como indício |

Cada regex é avaliada **dentro de um campo**, nunca sobre a concatenação dos três.
Vários padrões usam curinga — por exemplo `judicial policy.*administration` — e sobre
texto concatenado eles atravessam a fronteira entre título e periódico: um estudo de
*policy-making* publicado na *Public Administration Review* seria lido como
programático pelo nome do periódico. O confinamento por campo elimina essa
contaminação.

Antes da aplicação das regex, a pontuação tipográfica é normalizada (HYPHEN U+2010,
travessões, apóstrofos curvos → equivalentes ASCII). Sem isso, "Judicial
Policy‐Making" com hífen Unicode não casaria com `policy[\s-]?making`.

## Categorias

| Acepção | Definição | Tradição predominante |
| --- | --- | --- |
| **programática** | Política como programa, plano, prioridade ou portfólio institucional | Brasileira (CNJ), políticas públicas, governança judicial |
| **comportamental** | Política como indução de práticas, rotinas e decisões dos atores judiciais | Ciência política judicial anglo-saxã |
| **doutrinária** | Política como orientação normativa e interpretativa sobre o papel do Judiciário | Russa/pós-soviética, teoria geral chinesa, dogmática islâmica e constitucional |
| **indeterminado** | Rótulo empregado sem que título, resumo ou periódico permitam recuperar a acepção | — |

O **subtipo penal** (política de sentenciamento) é registrado em coluna própria
dentro de *comportamental*: induz decisão e não constitui acepção autônoma. O
manuscrito não o nomeia como quarta acepção.

## Ordem de precedência

```text
programática  →  doutrinária  →  comportamental  →  [subtipo penal]  →  indeterminado
```

Justificativa de cada posição:

1. **Programática primeiro.** É a acepção que o artigo delimita e mede, e seus sinais
   (`política judiciária nacional`, `CNJ`, `judicial governance`) são os mais
   específicos do conjunto.
2. **Doutrinária antes de comportamental.** Teoria geral da função jurisdicional é
   frequentemente enunciada a propósito de decisões concretas. A ordem inversa
   capturaria esses registros como comportamentais.
3. **Subtipo penal por último**, dentro do campo em exame, para não sequestrar
   registros programáticos ou doutrinários que apenas mencionem matéria penal.
4. **Indeterminado** é o resíduo, nunca uma atribuição ativa.

## Listas de padrões

As listas vivem em `src/utils/acepcoes.py`, em regex Python com `re.IGNORECASE`.

| Lista | Padrões | Origem |
| --- | ---: | --- |
| `PROGRAMMATIC_PATTERNS` | 24 | Herdada de `08c_reclassify_nuclear.py`, sem alteração |
| `BEHAVIORAL_PATTERNS` | 17 | Herdada de `08c_reclassify_nuclear.py`, sem alteração |
| `PENAL_PATTERNS` | 9 | Herdada de `08c_reclassify_nuclear.py`, sem alteração |
| `DOCTRINAL_PATTERNS` | 25 | **Acréscimo desta etapa** |

As três primeiras decidem a composição do anel nuclear e por isso são congeladas:
alterá-las mudaria os números do manuscrito. `tests/test_acepcoes.py` trava seus
tamanhos para que qualquer mudança seja deliberada, e a equivalência da decisão de
anel antes e depois da extração do módulo foi verificada registro a registro contra
`data/interim/05_reclassification_log.csv` (170 registros, zero divergências).

`DOCTRINAL_PATTERNS` **não participa** da decisão de anel. Foi acrescentada apenas
para a classificação por acepção, e cobre: tradição russa/pós-soviética (`судебная
политика`, *Gosudarstvo i pravo*, *Russian justice*); teoria geral e interpretação
judicial chinesas (*basic theoretical issues*, *judicial interpretations*, *People's
Court*, *National Congress of CPC*); dogmática islâmica (`السياسة القضائية`,
*islamic law*, *fiqh*, *imam*); e dogmática constitucional (*constitutional
complaints system*, *estado constitucional*, *poderes judiciales*, *teoria geral*).

## Resultado

| Acepção | Anel lexical | % | Periódicos | Anel nuclear final |
| --- | ---: | ---: | ---: | ---: |
| programática | 38 | 22,4% | 28 | 38 |
| comportamental | 41 | 24,1% | 23 | 1 |
| doutrinária | 14 | 8,2% | 9 | 13 |
| indeterminado | 77 | 45,3% | 53 | 63 |
| **total** | **170** | **100%** | **112** | **115** |

Subtipo penal: 7 registros, todos dentro de *comportamental*.

Campo que decidiu a classificação, no anel lexical: título 87, periódico 4,
resumo 2, sem padrão 77.

## Saídas

| Arquivo | Conteúdo |
| --- | --- |
| `data/final/nuclear_acepcoes.csv` | Uma linha por registro do anel lexical: acepção, subtipo, padrão que decidiu, campo do match e marca de sobrevivência ao anel final |
| `outputs/tables/acepcoes_summary.csv` | Contagens, percentuais, mediana de citações e periódicos distintos, nas duas populações |
| `outputs/tables/acepcoes_exemplares.csv` | Três exemplares por acepção, ordenados por citações |

## Limites de inferência

1. **Cobertura de resumo.** Apenas 14,8% do anel nuclear tem *abstract* nos
   metadados. Por isso 87 das 92 decisões com padrão recaem sobre o título. Acepção
   enunciada somente no corpo do texto não é captada.
2. **Regra lexical, não semântica.** A classificação identifica vocabulário, não
   argumento. Um artigo pode discutir a acepção programática sem empregar nenhum dos
   termos da lista.
3. **Sem dupla codificação independente.** A regra é determinística, o que elimina
   variação entre codificadores, mas não valida a tipologia — apenas a aplica de modo
   reprodutível. O mesmo limite já vale para a triagem semântica do PRISMA.
4. **Resíduo alto por construção.** Os 45,3% de `indeterminado` medem o que os
   metadados permitem recuperar, não a ausência de acepção nos textos. Devem ser
   lidos como limite de observação — e, no argumento do artigo, como sintoma da
   instabilidade lexical do campo.
5. **Vazamento residual da restrição.** Um registro comportamental permanece no anel
   nuclear final, retido por `08c` via correspondência no nome do periódico. É a
   contaminação que o confinamento por campo corrige na classificação, mas que não
   foi retroagida à composição do corpus congelado.

## Reprodução

```bash
python src/pipelines/10b_classify_acepcoes.py
python -m pytest tests/test_acepcoes.py -v
```

O passo integra `make pipeline`, em `PIPELINE_STEPS` de
`src/pipelines/14_rebuild_full_pipeline.py`, imediatamente após
`10_export_bibliometrix.py`. Duas execuções consecutivas produzem arquivos
byte a byte idênticos.
