# Proposta de execução detalhada — Raspagens, triagem e consolidação do corpus (v7)

**Projeto:** Public_Policy — Políticas Judiciárias  
**Objetivo desta etapa:** Revisar a estratégia de raspagem (strings/rodadas), consolidar a base unificada e conduzir uma triagem metodologicamente defensável para produzir **um corpus bibliométrico “CORE”** (e um corpus “ADJACENTE” controlado), que sustentará a revisão bibliométrica e a seleção final de leitura.

> Este documento registra a estratégia “v7” **à luz do aprendizado das rodadas anteriores** (multi-base, unificação e deduplicação) e do **mapeamento preliminar do campo** realizado no deepresearch (ênfases: CNJ, governança/gestão, eixos temáticos e natureza transdisciplinar).

---

## 1. Contexto e decisão epistemológica do recorte

### 1.1. Dois objetos possíveis (e por que isso importa)

A literatura do “sistema de justiça” é ampla e altamente adjacente. Por isso, antes de expandir raspagens, o projeto deve escolher explicitamente **qual objeto pretende mapear**:

**Opção A — Campo autodeclarado (“política judiciária” como rótulo explícito)**  
Mapear o **estado da arte do campo emergente** que se nomeia como “política judiciária” (e variações léxicas próximas), priorizando precisão conceitual.  
- **Pró:** reduz ruído; “defensável” como mapeamento de um campo emergente com autoidentificação.
- **Contra:** pode excluir literatura relevante que trata do mesmo objeto com outros rótulos (administração/governança/reforma), mesmo quando substantivamente próxima.

**Opção B — Campo ampliado (fenômeno)**  
Mapear a literatura sobre fenômenos ligados a políticas judiciárias, incluindo judicial administration / court management / judicial governance / judicial reform.  
- **Pró:** maior cobertura internacional e histórica.
- **Contra:** adjacências dominam (p.ex., “judicial review” constitucional) e o campo pode “dissolver” em vizinhos.

**Recomendação operacional (v7):** adotar **arquitetura em camadas**, com **CORE explícito** como eixo principal (Opção A) e uma camada “ADJACENTE” (Opção B restrita) apenas para robustez/nota metodológica.

---

## 2. Aprendizados das rodadas anteriores (o que manter e o que corrigir)

### 2.1. Unificação e deduplicação já resolvem 80% do risco de erro

O pipeline atual de unificação (script `06_build_unified_base.py`) faz:
- unificação de múltiplas bases (OpenAlex, Crossref, Scopus, Semantic Scholar);
- normalização de DOI/título/periódico/ano;
- ordenação por contagem de citações unificada;
- deduplicação por DOI (quando existe) e por chave composta (title+year+journal) quando não há DOI;
- exportação final em `data/final/unified_base.csv`.

Isso é um ponto forte e deve ser **preservado como backbone** do projeto.

### 2.2. Limitação importante: perda de rastreabilidade “multi-hit”

Ao deduplicar, um registro final pode ter sido capturado por **múltiplas strings e múltiplas bases**. Se o registro final guarda apenas uma referência (ex.: um `query_term` ou uma fonte), existe risco de:
- inferir incorretamente “de onde veio” ou “por qual string foi capturado”;
- usar `query_term` como filtro de inclusão/exclusão (o que é metodologicamente frágil).

**Correção v7 (obrigatória):** manter uma tabela de mapeamento *muitos-para-muitos*:
- `record_id` × `query_id` × `source`  
para recuperar a rastreabilidade completa sem distorcer o deduplicado final.

### 2.3. Adjacent noise: “judicial review” e vizinhanças constitucionais

Rodadas amplas tendem a capturar clusters grandes de:
- judicial review / constitutional review
- judicialization (macropolítica) sem instrumentos de política judiciária
- criminal justice/policing/prisons (quando não focam o Judiciário)

**Correção v7 (obrigatória):** evitar “judicial review” *sozinho* em novas raspagens. Se usado, será **sempre condicionado** (ver Seção 5).

---

## 3. Arquitetura de corpus (camadas) e entregáveis

A partir da base unificada, a v7 propõe **4 camadas**:

1. **UNIFIED (base ampla):** `data/final/unified_base_v7.csv`  
   - deduplicada, multi-base, com audit/log.

2. **EXPLÍCITO (CORE-EX):** `data/final/corpus_core_explicit_v1.csv`  
   - subconjunto da UNIFIED com regra principal: **ocorrência explícita** do rótulo do campo (“política judiciária” e variações) em campos textuais (título/abstract/keywords/query/journal), com regras e logs.

3. **AMPLIADO CONTROLADO (ADJ):** `data/final/corpus_adjacent_controlled_v1.csv`  
   - literatura próxima (admin/governance/reform) **sem rótulo explícito**, usada apenas para:
     - análise de robustez
     - nota metodológica (“o que ficou de fora e por quê”)

4. **LISTA FINAL DE LEITURA (READING):** `data/final/reading_list_final_v1.csv`  
   - seleção estratificada a partir do CORE-EX (e, opcionalmente, poucos “ponte” do ADJ), com justificativa por métricas bibliométricas.

**Entregáveis mínimos (para fechar a fase de raspagem/triagem):**
- `docs/05_raspagem_e_triagem_v7.md` (este doc)
- `data/audit/query_registry_v1.csv` (catálogo de strings/rodadas)
- `data/audit/run_log_v7.csv` (execuções: data, base, query_id, n)
- `data/interim/unified_base_v7_rawconcat.csv` (antes de deduplicar)
- `data/final/unified_base_v7.csv` (deduplicado)
- `data/final/corpus_core_explicit_v1.csv`
- `data/final/corpus_adjacent_controlled_v1.csv`
- `docs/audit_report_v7.md` (+ tabelas)

---

## 4. Governança da execução (reprodutibilidade)

### 4.1. Convenções de versão e “freeze”

- Toda rodada gera uma `run_id` (ex.: `v7_r01_2026-04-24_scopus`).
- O arquivo final de cada etapa recebe:
  - hash SHA256
  - data/hora
  - commit hash do Git
- Nenhuma etapa sobrescreve outputs “final”; sempre cria nova versão.

### 4.2. Registro de parâmetros

Guardar em `data/audit/`:
- `query_registry_v1.csv` (strings, idiomas, filtros, objetivo, rodada)
- `screening_rules_v1.yml` (dicionários e regras de triagem)
- `normalization_rules_v1.yml` (sinônimos, stopwords, normalizações)

### 4.3. Ética e conformidade
- Respeitar limites e termos de uso das bases (preferir APIs oficiais quando existirem).
- Armazenar apenas metadados necessários para bibliometria e rastreio dos textos.

---

## 5. Plano de raspagem (rodadas de strings) — v7

> Lógica: **rodadas curtas e “cirúrgicas”**, orientadas por lacunas do CORE e por controle de adjacência.

### 5.1. Rodada 0 (R0) — “Sem nova raspagem”: construir o CORE-EX a partir da base unificada

**Entrada:** `unified_base.csv`  
**Saída:** `corpus_core_explicit_v1.csv` e `corpus_adjacent_controlled_v1.csv`

**Regra CORE-EX (mínima e auditável):**
- incluir se houver match em `(title OR abstract OR keywords OR query_term OR journal)` para pelo menos um item de:
  - `política judiciária`
  - `políticas judiciárias`
  - `politica judiciaria` (sem acento)
  - `judicial policy`
  - `judicial policies`
  - `política judicial` / `políticas judiciais` (PT/ES) **(com validação manual curta porque tem ambiguidade)**

**Regra DOI (para bibliometria “clean”):**
- manter `doi != ""` como padrão;
- permitir exceções apenas se:
  - `document_type == review` **ou**
  - registro for “chave” (alto impacto) e recuperável por link estável.
- Tudo que ficar sem DOI deve ser marcado `doi_missing_flag=True`.

**Validação curta (obrigatória):**
- 100 itens CORE-EX aleatórios + 50 “casos de borda” (baixa confiança) para rotular:
  - relevante / parcialmente / irrelevante
- salvar `validation_pack_coreex_v1.xlsx` e `validation_metrics_v1.json`.

**Critério de parada:** se CORE-EX atingir precisão aceitável (ex.: ≥85% relevante+parcial na amostra), seguir para bibliometria sem reabrir coleta.

---

### 5.2. Rodada 1 (R1) — Expansão linguística controlada (PT/ES/EN)

Rodar somente se a Rodada 0 revelar:
- CORE-EX pequeno demais; ou
- subtemas centrais faltando (p.ex. “multiportas”, “Justiça 4.0”, “Justiça restaurativa” dentro de política judiciária).

**Strings PT (Brasil):**
- `"política judiciária" OR "políticas judiciárias" OR "politica judiciaria"`
- `"Conselho Nacional de Justiça" OR CNJ` **AND** (`"política judiciária"` OR `"politica judiciaria"`)
- `"gestão de política judiciária" OR "política judiciária nacional"` (alta precisão)

**Strings ES (LatAm):**
- `"política judicial" OR "políticas judiciales"` (com filtro de contexto)
- `"consejo de la judicatura" OR "consejo del poder judicial"` **AND** (`política*`)

**Strings EN (internacional):**
- `"judicial policy" OR "judicial policies"` **AND** pelo menos um termo de ancoragem:
  - `court administration OR judicial administration OR governance OR management OR performance OR council`
  - (isso evita capturar a literatura comportamental de “policy preferences” em judicial review)

**Guard rails (R1):**
- Proibir `judicial review` como termo isolado.
- Se `judicial review` aparecer, só permitir em conjunto:
  - `"judicial review" AND (judicial policy OR court administration OR governance OR management)`.

---

### 5.3. Rodada 2 (R2) — Âncoras institucionais do campo (CNJ e políticas nomeadas)

Rodar se a Rodada 0/1 mostrar que os eixos empíricos centrais do campo (no Brasil) não aparecem bem.

**Strings por eixo (alta precisão):**

**(A) Multiportas / mediação / CEJUSC**
- `"Resolução 125" OR "Resolução CNJ 125" OR CEJUSC OR "tratamento adequado dos conflitos" OR "Justiça multiportas"`
- combinar com `CNJ` quando a base for muito ampla.

**(B) Justiça Restaurativa**
- `"Resolução 225" OR "Justiça Restaurativa" AND CNJ`

**(C) Transformação digital / Justiça 4.0**
- `"Justiça 4.0" OR "Juízo 100% Digital" OR "Balcão Virtual" OR "PDPJ-Br" OR "PDPJ" OR "Núcleo de Justiça 4.0"`
- opcional: `("inteligência artificial" OR IA OR "algorithm*") AND (CNJ OR tribunal*)` (para mapear subtema emergente)

**Nota:** essas strings podem capturar documentos normativos e relatórios; por isso:
- separar outputs em `academic_candidates` vs `institutional_docs`;
- institucional entra como **corpus de contexto**, não como bibliometria (a menos que o objetivo inclua literatura cinzenta).

---

### 5.4. Rodada 3 (R3) — Lacunas de gestão e avaliação (somente se o CORE ficar “normativo demais”)

Se o CORE-EX ficar muito centrado em “norma e descrição institucional” e faltar avaliação empírica/gestão:

**Strings (somente em conjunto com policy/anchor):**
- `("avaliação" OR "impacto" OR "indicadores" OR "desempenho" OR "eficiência") AND ("política judiciária" OR CNJ)`
- `("court performance" OR "performance measurement" OR "caseflow" OR backlog) AND ("judicial policy" OR "court administration")`

---

## 6. Triagem e classificação (CORE / ADJ / OUT)

### 6.1. Variáveis de triagem (campos e features)

Criar `text_for_screening` concatenando (quando existir):
- title
- abstract
- keywords/concepts
- journal
- query_term(s)
- (opcional) venue/subject areas

Gerar colunas:
- `scope_label_suggested` ∈ {CORE_EX, ADJ, OUT, REVIEW}
- `scope_confidence` ∈ [0, 1]
- `scope_reason_terms` (termos que dispararam a regra)
- `policy_axis` (multiportas / JR / digital / governança / gestão-avaliação / outros)

### 6.2. Codebook curto (para validação humana)

**CORE_EX**: usa rótulo explícito do campo OU está claramente ancorado em políticas judiciárias do CNJ (com linguagem de política/programa, não só “caso”).  
**ADJ**: trata de administração/governança/reforma do Judiciário sem o rótulo explícito; entra apenas como robustez.  
**OUT**: constitucional/judicial review sem instrumento de política judiciária; áreas substantivas sem foco institucional; criminal justice sem Judiciário como objeto.

### 6.3. Validação curta (mínimo viável)

- 100 CORE_EX aleatórios
- 50 ADJ aleatórios
- todos REVIEW (casos de borda)

Reportar:
- precisão CORE_EX (relevante+parcial)
- taxa de falsos negativos (ADJ que deveria ser CORE_EX)
- ajustes no dicionário

---

## 7. Integração com o pipeline existente (scripts e pastas)

### 7.1. Pastas sugeridas (repo)

```
data/
  raw/
    v7_r01_scopus_raw.csv
    v7_r01_openalex_raw.csv
  interim/
    v7_concat_raw.csv
    v7_unified_pre_dedupe.csv
  final/
    unified_base_v7.csv
    corpus_core_explicit_v1.csv
    corpus_adjacent_controlled_v1.csv
  audit/
    query_registry_v1.csv
    run_log_v7.csv
    screening_rules_v1.yml
    unified_base_v7_meta.json
docs/
  05_raspagem_e_triagem_v7.md
  audit_report_v7.md
src/
  pipelines/
    06_build_unified_base.py
    07_build_record_query_map.py
    08_screen_core_explicit.py
```

### 7.2. Ajustes recomendados no `06_build_unified_base.py`

Sem mudar a lógica de deduplicação, adicionar:
- preservação de `source` e `query_id` quando existirem;
- exportar um `record_query_map.csv` antes do drop_duplicates, com:
  - `doi_norm`, `title_norm`, `source_file`, `query_id`, `query_term`, `retrieval_date`.

---

## 8. Critérios de parada e risco de “coleta infinita”

### 8.1. Stop rules por rodada
Encerrar raspagens adicionais se:
- ganho marginal de **novos CORE_EX únicos** < 2% por duas rodadas seguidas; **e**
- nenhuma lacuna de eixo (multiportas/JR/digital/governança/gestão-avaliação) estiver materialmente sub-representada.

### 8.2. Sinais de alerta (requerem ajuste de strings, não mais rodadas)
- proporção de OUT elevada (>30%) em uma rodada → string ampla demais
- forte concentração em 1 termo/1 base → revisar registro de strings e balancear

---

## 9. Como isso se conecta à revisão bibliométrica e à lista final de leitura

### 9.1. O que vira bibliometria “principal”
- **CORE_EX** (com DOI, preferencialmente) sustenta:
  - produção temporal
  - top periódicos
  - termos/temas
  - redes (autores, termos)
  - impacto (citações/ano, fundacionais vs recentes)

### 9.2. O que vira robustez/nota metodológica
- **ADJ**:
  - comparar clusters FULL vs CORE_EX (sensibilidade)
  - explicitar “o que ficou fora” e por quê

### 9.3. Seleção final de leitura (após bibliometria)
A leitura final será estratificada por:
- fundacionais (impacto + antiguidade)
- centrais (centralidade em redes / recorrência)
- emergentes (crescimento + citações/ano recentes)
- metodológicos (avaliação, indicadores, métodos empíricos)

---

## 10. Checklist de execução (passo-a-passo)

1) **Freeze** da base atual + meta (hash)  
2) Rodar **R0**: construir CORE_EX e ADJ a partir da unificada  
3) Fazer **validação curta** e ajustar dicionário  
4) Se necessário, rodar **R1** (linguística controlada)  
5) Se necessário, rodar **R2** (âncoras CNJ e políticas nomeadas)  
6) Atualizar unificada para **v7**, preservando `record_query_map`  
7) Congelar `corpus_core_explicit_v1.csv` e iniciar bibliometria  
8) Gerar `reading_list_final_v1.csv` a partir das métricas

---

## 11. Notas finais (limitações declaradas)

- Cobertura de abstracts pode ser baixa; priorizar título+keywords/concepts.
- DOI é critério forte de deduplicação e rastreio; mas pode excluir literatura local (tese/dissertação) — tratar isso como **camada contextual**.
- Termos em inglês (“judicial policy”) são ambíguos; por isso, o CORE internacional requer ancoragem adicional.

---
