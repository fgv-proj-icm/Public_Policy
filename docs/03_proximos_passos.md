# Próximos passos da pesquisa

## 1. Situação atual

A fase de preparação do corpus está praticamente concluída.

Hoje o projeto já dispõe de:

- uma base mestre estrutural;
- um corpus bibliométrico final robusto;
- um corpus de leitura curado, ainda provisório;
- amostras para validação manual;
- scripts e documentação rastreáveis no GitHub.

---

## 2. Objetivo da próxima fase

A próxima fase não é mais de coleta ampla, mas de **análise**.

Ela será dividida em dois movimentos paralelos:

1. validação curta do corpus de leitura;
2. análises bibliométricas sobre o corpus final congelado.

---

## 3. Passo imediato 1 — validação manual curta

### O que fazer
Preencher os arquivos de validação amostral com rótulos:

- relevante;
- parcialmente relevante;
- irrelevante.

### Arquivos a revisar
- amostra de incluídos;
- amostra de excluídos;
- amostra curada final, quando necessário.

### Finalidade
Verificar se o corpus final está metodologicamente aceitável sem depender de novas rodadas automáticas extensas.

### Critério de parada sugerido
Encerrar a curadoria se:

- pelo menos 85% dos incluídos forem considerados relevantes ou parcialmente relevantes;
- e no máximo 15% dos excluídos parecerem erros graves de exclusão.

---

## 4. Passo imediato 2 — congelamento operacional do corpus bibliométrico

### Arquivo de trabalho principal
O corpus de trabalho para as análises bibliométricas deve ser:

- `bibliometric_corpus_final_v2.csv`

### Decisão
Esse arquivo deve ser tratado como corpus bibliométrico congelado, salvo evidência forte em contrário na validação manual.

---

## 5. Passo imediato 3 — definição do corpus de leitura

### Situação atual
O corpus de leitura curado já é útil, mas ainda não deve ser tratado como definitivo sem triagem humana curta.

### O que fazer
- revisar o top 100 curado;
- excluir itens claramente tangenciais;
- separar uma lista final de leitura aprofundada.

### Resultado esperado
Produzir um arquivo ou lista final com:
- textos fundacionais;
- textos mais recentes;
- textos metodologicamente centrais;
- textos relevantes por subtema.

---

## 6. Análises bibliométricas a executar

A próxima grande etapa consiste em rodar análises bibliométricas sobre o corpus final.

### 6.1. Estatísticas descritivas
- publicações por ano;
- tipo documental;
- distribuição por base;
- distribuição por periódicos;
- distribuição por idioma, quando possível.

### 6.2. Estrutura temática
- frequência de termos;
- agrupamento por subtema;
- comparação entre:
  - reforma judicial;
  - administração judicial;
  - governança judicial;
  - políticas judiciárias;
  - CNJ/Brasil.

### 6.3. Impacto
- top artigos por citação;
- top periódicos por recorrência;
- textos fundacionais vs. textos recentes.

### 6.4. Redes e relações
- coocorrência de termos;
- redes de autores, quando houver metadados suficientes;
- redes de periódicos;
- distribuição temática por período.

---

## 7. Produtos esperados da próxima fase

Ao final da próxima fase, o projeto deverá gerar:

1. tabelas descritivas do corpus;
2. gráficos temporais e temáticos;
3. lista dos trabalhos centrais por subtema;
4. corpus final de leitura;
5. uma primeira narrativa analítica sobre o estado da arte.

---

## 8. Organização sugerida da execução

### Etapa A — validação curta
- revisar amostras;
- confirmar o corpus bibliométrico;
- ajustar, se necessário, o corpus de leitura.

### Etapa B — análises bibliométricas
- estatísticas gerais;
- tabelas e gráficos;
- agrupamentos temáticos.

### Etapa C — leitura substantiva
- leitura dos trabalhos centrais;
- registro de achados;
- identificação de lacunas e agendas.

### Etapa D — redação
- redação metodológica final;
- redação dos resultados bibliométricos;
- redação da discussão e da agenda de pesquisa.

---

## 9. Prioridade prática imediata

A prioridade mais racional agora é:

1. validar rapidamente o corpus de leitura;
2. iniciar as análises bibliométricas no corpus congelado;
3. evitar reabrir a fase de coleta, salvo necessidade muito forte.

---

## 10. Síntese final

O projeto já concluiu a fase mais pesada: construir um corpus multibase limpo, auditado, documentado e metodologicamente defensável.

Os próximos passos são mais analíticos do que estruturais.

Em termos simples:

- **o corpus bibliométrico está pronto para análise**;
- **o corpus de leitura está quase pronto**;
- **a próxima etapa é transformar o corpus em resultados**.