# Codebook do IMO-PJNP — v1

**Índice de Maturidade Observável das Políticas Judiciárias Nacionais Programáticas**

| Campo | Valor |
| --- | --- |
| Versão | 1.0 |
| Data | 31/07/2026 |
| Artigo vinculado | ENAJUS 537601 — "Política Judiciária como Campo Emergente: Da Cartografia Bibliométrica à Maturidade Observável das PJNP" |
| Especificação de origem | `pjnp-avaliacao/outputs/tables/index_specifications.json` |
| Semente analítica | 42 |
| Correspondência no manuscrito | Apêndice D |

> Este codebook responde ao comentário 4 do parecer ENAJUS ("operacionalização do
> IMO-PJNP insuficiente"). Ele documenta a regra completa de construção do índice,
> de modo que um terceiro possa recalculá-lo a partir das planilhas do Painel PJNP.

## 1. Construto

O IMO-PJNP mede **maturidade observável**: o grau em que atributos mínimos de
governança, monitoramento e alinhamento estratégico aparecem **documentados** no
Painel PJNP.

O adjetivo "observável" é a delimitação central. O índice mede a camada documental
da política — não sua qualidade, sua implementação nos tribunais nem seus efeitos
sociais.

## 2. Unidade de análise

A política judiciária nacional programática, conforme registrada no Painel PJNP
(40 registros). Iniciativas (253) e colegiados (96) são **atributos** da política,
não unidades autônomas de análise.

## 3. Fontes documentais

| Planilha | Registros | Uso |
| --- | ---: | --- |
| `Base_painel.xlsx` | 40 políticas × 14 variáveis | Todas as variáveis do índice |
| `Gov_PJNP.xlsx` | 253 iniciativas | Outputs administrativos (fora do índice) |
| `Colegiados_PJNP.xlsx` | 96 colegiados | Densidade institucional (fora do índice) |

Nenhuma fonte externa ao painel entra na composição do índice. Exportação de
abril de 2026.

## 4. Regra geral de codificação

Todas as variáveis do índice são **binárias**.

- **1** — o campo está preenchido com conteúdo substantivo.
- **0** — o campo está vazio ou preenchido com o marcador `"-"`, usado pelo painel
  para campo vago ou não registrado.

Nenhum campo é imputado, inferido a partir de outra política ou completado por
consulta externa. A codificação é aplicada por script sobre campos estruturados.

## 5. Dimensões, variáveis e pesos

| Dimensão | Peso | Variável no painel | Peso da variável | Regra |
| --- | ---: | --- | ---: | --- |
| Monitoramento e rastreabilidade | 40% | Link monitoramento | 40,00 | 1 se há URL de painel de monitoramento |
| Governança formal | 35% | Coordenador(a) | 11,67 | 1 se há ministro(a)/conselheiro(a) designado(a) |
| | | Supervisor(a) | 11,67 | 1 se há juiz(a) auxiliar designado(a) |
| | | Gerente | 11,67 | 1 se há servidor(a) responsável |
| Alinhamento estratégico | 25% | Meta Nacional | 6,25 | 1 se há meta nacional associada |
| | | ODS | 6,25 | 1 se há ODS indicado |
| | | Macrodesafio | 6,25 | 1 se há macrodesafio da Estratégia Nacional |
| | | Objetivo estratégico | 6,25 | 1 se há objetivo do Planejamento Estratégico |

Os pesos são atribuídos por **dimensão** e distribuídos igualmente entre as
variáveis de cada dimensão.

### Justificativa dos pesos

Pesos normativos, teoricamente informados e auditáveis — lógica multicritério em
sentido fraco. **Não houve** elicitação formal por painel de especialistas, AHP ou
estimação empírica.

- **Monitoramento (40%)** — a gestão do desempenho público sustenta o peso maior:
  medidas só são úteis quando produzem informação para acompanhar, aprender e
  corrigir rotas (Behn, 2003; Moynihan & Pandey, 2010; Pandey, 2015).
- **Governança formal (35%)** — papéis designados tornam a política coordenável,
  responsabilizável e auditável (Lascoumes & Le Galès, 2007; Pires, 2016).
- **Alinhamento estratégico (25%)** — conecta a política a prioridades
  institucionais, com alcance dependente de validação posterior (Ng, 2011;
  Akutsu & Guimarães, 2012).

## 6. Escalas e agregação

| Medida | Escala | Cálculo |
| --- | --- | --- |
| Índice base | 0–4 | Soma simples de coordenador + supervisor + gerente + link de monitoramento |
| IMO-PJNP | 0–100 | Soma ponderada das oito variáveis da seção 5 |
| Componentes | 0–100 cada | Governança formal, monitoramento e alinhamento estratégico, separadamente |

Formalmente:

```
IMO-PJNP = 40 × M + 35 × G + 25 × A
```

em que `M` é a presença de link de monitoramento, `G` é a média dos três atributos
de governança formal e `A` é a média dos quatro atributos de alinhamento
estratégico.

## 7. Tratamento de ausência documental

**Regra:** ausência é codificada como 0 e significa **ausência de registro no
painel**, não ausência do atributo na política.

Uma política pode ter gerente designado por ato interno sem que o painel o
registre. Essa é a limitação central do índice e a razão de o construto se chamar
maturidade *observável*.

Nenhum valor é tratado como faltante para fins de exclusão de caso: **a completude
do cadastro é parte do fenômeno medido**, não ruído a ser corrigido.

## 8. Exclusões deliberadas

Ficam **fora** do índice principal:

- número de iniciativas;
- número de colegiados;
- percentual de iniciativas concluídas;
- percentual de iniciativas com produto.

**Motivo:** esses campos são usados como *outputs administrativos* nas análises de
associação. Incluí-los no índice criaria circularidade entre preditor e desfecho.
São tratados como densidade institucional observável e usados apenas em análises
exploratórias.

## 9. Confiabilidade

A codificação é **determinística**: deriva de regra aplicada por script sobre
campos estruturados, sem julgamento de codificador. Isso dispensa teste de
concordância entre avaliadores (Kappa, alfa de Krippendorff).

A confiabilidade relevante é a **do cadastro de origem**, não a da codificação — e
ela não é verificável a partir do próprio painel. Validação cadastral junto às
unidades responsáveis é a etapa seguinte necessária.

## 10. Sensibilidade

O escore é comparado a duas especificações alternativas:

| Especificação | Pesos M/G/A |
| --- | --- |
| Atual | 40 / 35 / 25 |
| Pesos iguais | 33,3 / 33,3 / 33,3 |
| Governança maior | 30 / 40 / 30 |

Reportados: correlação de Spearman com o escore atual e número de políticas que
mudam mais de 10 posições no ranking. O exercício é checagem de estabilidade da
classificação, não validação dos pesos.

## 11. Limites de inferência

O índice **mede**:

- presença documental de atributos de governança, monitoramento e alinhamento;
- rastreabilidade mínima da política no painel;
- completude do cadastro como capacidade administrativa observável.

O índice **não mede**:

- qualidade, periodicidade ou uso efetivo do monitoramento;
- implementação da política nos tribunais;
- mudança de rotinas de magistrados e servidores;
- efetividade, resultado ou impacto social da política;
- as acepções comportamental e doutrinária de política judiciária.

**Escores altos indicam política bem registrada, não política bem-sucedida.**

## 12. Reprodução

```powershell
cd C:\PROJETOS\GITHUB\LAB-LEPP\pjnp-avaliacao
git switch chore/enajus-2026
python -m pjnp.run --input data/raw --out outputs --seed 42
```

Saídas relevantes em `outputs/tables/`: `pjnp_indices_all.csv`,
`index_summary.csv`, `index_specifications.json`, `pjnp_policy_features.csv`.

> **Bloqueio conhecido:** `data/raw/*.xlsx` está no `.gitignore`. Um clone limpo
> não reproduz o pipeline; os arquivos do Painel PJNP precisam ser obtidos à parte.

## 13. Agenda de validação

1. Validação cadastral junto às unidades responsáveis pelas políticas.
2. Elicitação formal de pesos com painel de especialistas.
3. Verificação de correspondência entre registro no painel e ato interno.
4. Estudos de caso contrastantes para examinar implementação real.
5. Extensão do codebook às acepções comportamental e doutrinária, com fontes
   distintas do painel.
