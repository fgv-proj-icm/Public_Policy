# Roteiro de melhoria da base unificada

## Objetivo
Transformar a `unified_base.csv` em uma base limpa, deduplicada e pronta para análise.

## Problemas principais identificados
1. duplicação residual por DOI mal normalizado;
2. duplicação residual em registros sem DOI;
3. heterogeneidade de `type`;
4. cobertura desigual entre fontes;
5. alto volume de `journal = N/D`;
6. risco de viés em análises com `authors`, `abstract` e `language`.

## Etapas

### Etapa 1 — Congelamento
Preservar a `unified_base.csv` como snapshot bruto consolidado.

### Etapa 2 — Auditoria reprodutível
Gerar relatórios automáticos de:
- missingness;
- cobertura por fonte;
- duplicatas por DOI;
- duplicatas sem DOI;
- distribuição de `type`.

### Etapa 3 — Normalização forte
Padronizar:
- DOI;
- título;
- periódico;
- tipo documental;
- idioma;
- ano.

### Etapa 4 — Deduplicação final
Aplicar hierarquia:
1. DOI limpo
2. IDs externos
3. título + ano + periódico
4. título + ano

### Etapa 5 — Escolha do melhor registro
Critério:
1. maior completude;
2. maior citação;
3. prioridade de fonte adequada ao campo.

### Etapa 6 — Base limpa
Gerar:
- `unified_base_clean.csv`
- `unified_base_clean_report.json`

### Etapa 7 — Base pronta para análise
Gerar:
- `unified_base_analysis_ready.csv`

## Critérios de aceite
- duplicação residual por DOI = 0 ou residual mínimo justificado;
- `type` harmonizado;
- metadados-chave padronizados;
- relatório comparativo antes/depois disponível.