# Metodologia da pesquisa

## 1. Problema de pesquisa

Esta pesquisa tem por objetivo mapear o **estado da arte do campo que se nomeia explicitamente como política judiciária**, e não todo o universo de estudos sobre o Poder Judiciário ou sobre o sistema de justiça em sentido amplo.

A pergunta central passa a ser:

**existe um campo que se reconhece e se apresenta explicitamente como política judiciária, política judicial ou judicial policy, e, se existe, qual é sua estrutura intelectual?**

Essa formulação desloca a pesquisa de uma busca temática ampla para uma busca por **identidade lexical e disciplinar**.

---

## 2. Delimitação do objeto

O objeto principal da pesquisa não é:

- todo estudo sobre reforma judicial;
- todo estudo sobre administração judicial;
- todo estudo sobre governança judicial;
- toda literatura sobre judicial review;
- toda literatura sobre judicialização de políticas públicas.

Esses temas compõem o universo mais amplo dos estudos sobre justiça, tribunais e Judiciário, mas não correspondem automaticamente ao campo que se **autodenomina** como política judiciária.

Assim, a pesquisa distingue entre:

### 2.1. Núcleo explícito
Registros que utilizam explicitamente expressões como:

- `política judiciária`
- `políticas judiciárias`
- `judicial policy`
- `judicial policies`
- `judiciary policy`
- `judiciary policies`
- `política judicial`
- `políticas judiciales`

em campos centrais do registro, especialmente:
- título;
- resumo;
- palavras-chave / concepts.

### 2.2. Literatura adjacente
Registros que tratam de temas próximos, mas não se nomeiam explicitamente dessa forma, como:
- `judicial administration`
- `court administration`
- `judicial governance`
- `court governance`
- `judicial reform`
- `court reform`
- `judicial management`
- `case management`
- `judicial performance`

Essa literatura não compõe o núcleo da pergunta principal, mas será preservada como **anel adjacente** para contextualização e comparação.

---

## 3. Justificativa da escolha

A escolha por um corpus mais restrito e lexicalmente explícito decorre de três razões.

### 3.1. Coerência com a pergunta
Se a pergunta é sobre o campo que se reconhece explicitamente como política judiciária, o corpus deve ser formado por registros que expressem esse enquadramento de forma visível.

### 3.2. Precisão metodológica
Uma busca temática ampla gera um corpus maior, mas dilui o objeto e aumenta o ruído por sobreposição com tradições distintas, como judicial review, judicial politics, reforma judicial e governança judicial.

### 3.3. Valor analítico do corpus pequeno
Se o campo for realmente emergente, um corpus pequeno não é defeito, mas resultado substantivo: ele permite mostrar o grau de dispersão, a baixa densidade de rede, a ausência de periódico nuclear ou a concentração em poucos autores e instituições.

---

## 4. Fontes de dados

A pesquisa utiliza quatro bases bibliográficas:

- OpenAlex
- Crossref
- Scopus
- Semantic Scholar

As bases já haviam sido coletadas em fases anteriores do projeto, com queries mais amplas. Nesta etapa, esses materiais passam a ser tratados como **universo de identificação**, e não como corpus final automático.

---

## 5. Estratégia geral de construção do corpus

A estratégia adotada passa a seguir lógica inspirada em PRISMA e organizada em duas camadas analíticas.

### 5.1. Universo identificado
Todos os registros coletados nas bases e posteriormente consolidados em um dataset unificado e deduplicado entre bases.

### 5.2. Dois anéis de inclusão

#### CORE_EX
O anel nuclear reúne os registros que mencionam explicitamente o campo em:
- título;
- resumo;
- palavras-chave / concepts.

Esse é o corpus principal da pesquisa.

#### ADJ
O anel adjacente reúne registros sobre termos cognatos e tradições próximas, úteis para:
- contextualizar o núcleo;
- comparar periferia e centro;
- analisar de quais tradições o núcleo se alimenta.

---

## 6. Protocolo de identificação e triagem

### 6.1. Identificação
Os registros são identificados a partir das bases bibliográficas já coletadas.

### 6.2. Filtro documental
São mantidos apenas documentos com perfil acadêmico compatível com a análise bibliométrica:
- `article`
- `review`
- `paper`

### 6.3. Deduplicação
A deduplicação cross-base segue a seguinte ordem:

1. DOI normalizado;
2. para registros sem DOI, combinação de:
   - título normalizado;
   - ano;
   - periódico.

### 6.4. Screening
Após a deduplicação, cada registro é classificado em:

- `include_core`
- `include_adjacent`
- `exclude`

com motivo explícito registrado em log de triagem.

---

## 7. Critérios de inclusão

### 7.1. Inclusão no CORE_EX
O registro entra no núcleo quando:

- contém termo explícito do campo em título, resumo ou concepts; ou
- contém `judicial policy` no singular em campo central, desde que acompanhado de suporte institucional suficiente.

### 7.2. Inclusão no ADJ
O registro entra no anel adjacente quando:

- não integra o núcleo explícito;
- mas contém termos cognatos relevantes para o ecossistema do campo.

---

## 8. Critérios de exclusão

São excluídos do corpus principal registros que:

- tratem predominantemente de `judicial review` em sentido constitucionalista;
- tratem de judicialização de políticas públicas sem foco no Judiciário como objeto institucional;
- estejam fora dos tipos documentais definidos;
- não apresentem sinais textuais suficientes de pertencimento ao núcleo ou ao anel adjacente;
- sejam duplicatas após consolidação cross-base.

---

## 9. Situação empírica atual da triagem

Na rodada consolidada de 28/04/2026 (quatro bases globais, modo offline, sem integração do suplemento brasileiro):

- foram identificados **7.161** registros;
- **1.193** duplicatas removidas (DOI normalizado; fallback título + ano + periódico);
- após deduplicação, restaram **5.968** registros triados;
- desses, **115** foram incluídos no `CORE_EX`;
- **4.811** foram classificados como `ADJ`;
- **1.042** foram excluídos.

Esses resultados reforçam a hipótese de que o núcleo explícito do campo é pequeno e distinto do universo mais amplo da literatura sobre justiça e Judiciário.

---

## 10. Uso analítico dos dois anéis

### 10.1. CORE_EX
O núcleo explícito será usado para:
- estatísticas descritivas do campo;
- evolução temporal;
- periódicos;
- autores;
- instituições;
- termos centrais;
- construção do estado da arte principal.

### 10.2. ADJ
O anel adjacente será usado para:
- contextualização;
- comparação entre núcleo e periferia;
- análises relacionais, como co-citação e acoplamento bibliográfico, quando pertinentes.

---

## 11. Consequência epistemológica da escolha

A pesquisa não pretende afirmar que toda a literatura adjacente seja irrelevante, mas apenas que ela não responde diretamente à pergunta principal.

Assim, a contribuição central do estudo será mostrar:

- se existe um campo explícito de políticas judiciárias;
- como esse campo se distribui no tempo, nas bases, nos periódicos e nos idiomas;
- e como ele se relaciona com tradições vizinhas.

---

## 12. Próxima fase

Com o corpus congelado em 28/04/2026, a próxima fase consiste em:

1. curadoria do suplemento brasileiro (285 candidatos identificados, 284 ainda ausentes do corpus);
2. análise bibliométrica do `CORE_EX` (evolução temporal, periódicos, autores, instituições);
3. análise relacional do `ADJ` (co-citação, acoplamento bibliográfico);
4. integração dos resultados no relatório Quarto.