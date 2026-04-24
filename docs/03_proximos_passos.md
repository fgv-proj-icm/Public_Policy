# Próximos passos da pesquisa

## 1. Situação atual

A pesquisa já dispõe de uma nova etapa de unificação e triagem baseada em PRISMA, estruturada em dois anéis:

- `CORE_EX`
- `ADJ`

A partir deste ponto, a linha principal do projeto deixa de buscar um corpus único e passa a trabalhar com:

- um núcleo explícito, pequeno e diretamente alinhado à pergunta;
- um anel adjacente, maior, útil para contextualização e comparação.

---

## 2. O que foi decidido

Foi decidido que o objeto principal da pesquisa é:

- o campo que se nomeia explicitamente como política judiciária, política judicial ou judicial policy.

Também foi decidido que:

- a literatura cognata não será descartada;
- mas ela será tratada como anel adjacente, e não como corpus principal automático.

---

## 3. O que será mantido

Serão mantidos como base da nova fase:

- a consolidação cross-base;
- a deduplicação global;
- a classificação PRISMA em `CORE_EX`, `ADJ` e `EXCLUDE`;
- os logs de screening;
- os motivos de exclusão.

---

## 4. O que será removido

Serão removidos da linha principal:

- a antiga estratégia `explicit_policy_unified_*`;
- os arquivos e scripts experimentais dessa etapa intermediária;
- outputs que não correspondem à nova lógica PRISMA.

---

## 5. Próxima sequência de trabalho

### Etapa 06
Consolidar a nova base unificada PRISMA e sua documentação.

### Etapa 07
Gerar o fluxo PRISMA completo com:
- identificados;
- deduplicados;
- triados;
- excluídos com motivo;
- incluídos no núcleo;
- incluídos no anel adjacente.

### Etapa 08
Preparar o corpus `CORE_EX` para:
- revisão metodológica;
- descrição bibliométrica;
- eventual leitura integral dos itens centrais.

### Etapa 09
Produzir a bibliometria principal do `CORE_EX`.

### Etapa 10
Produzir análises comparativas e relacionais com o `ADJ`.

### Etapa 11
Derivar a lista final de leitura a partir do `CORE_EX`, eventualmente com apoio do `ADJ` para textos-ponte.

---

## 6. Resultado esperado

Ao final da nova fase, a pesquisa deverá dispor de:

- um protocolo PRISMA transparente;
- um corpus nuclear coerente com a pergunta;
- um anel adjacente útil para comparação;
- uma bibliometria principal focada;
- uma lista final de leitura diretamente derivada do núcleo.

---

## 7. Próximo passo prático imediato

O próximo passo prático imediato é:

1. remover a linha antiga `explicit_policy_unified_*`;
2. atualizar a metodologia e os próximos passos;
3. comitar essa reorganização no GitHub;
4. seguir para as próximas pipelines da linha PRISMA.