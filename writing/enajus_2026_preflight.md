# EnAJUS 2026 — Preflight da Submissão (ID 537601)

**Data da verificação:** 17 de agosto de 2026
**Etapa:** Trabalho completo (2ª etapa — versão identificada)
**ID ENAJUS:** 537601
**Prazo:** 25/09/2026
**Tipo de trabalho:** Trabalho empírico concluído
**Tema de interesse:** 9) Políticas Públicas de Justiça. Formulação, Implementação e Avaliação
**Título:** Política Judiciária como Campo Emergente: Da Cartografia Bibliométrica à Maturidade Observável das PJNP

> Substitui o preflight de 04/06/2026, que registrava o título anterior
> ("Uma Análise Bibliométrica Multibase", 9 palavras) e um critério de contagem
> diferente — ver §"Mudança de critério de contagem".
>
> **Rodada de 17/08/2026.** Fecha o ponto do parecer sobre as três acepções, que a
> rodada de 01/08 havia registrado como atendido apenas no plano conceitual. A
> subseção *Polissemia como achado bibliométrico* passou de 58 palavras sem
> evidência para classificação medida do corpus, com tabela e codebook próprio
> (suplemento item E). Ver §"Classificação por acepção".

## Metadados congelados

| Campo | Valor | Fonte |
| --- | --- | --- |
| Título | Idêntico, byte a byte, ao do resumo expandido aceito | `enajus_2026_resumo_expandido_blind.qmd` l. 2 |
| Autoria | Igor Caires Machado; Marina Brazil Bonani; Antonio Ferreira de Melo Filho; Juliana Almeida Costa Cronemberger | Página oficial de aceites |
| Afiliação | Conselho Nacional de Justiça – Escola Nacional do Judiciário | Página oficial de aceites |
| Área temática | Políticas Públicas de Justiça. Formulação, Implementação e Avaliação | Página oficial de aceites |
| Palavras-chave | 5, separadas por ponto-e-vírgula | Reduzidas de 6 (aceite) para o limite do evento |

**Palavras-chave adotadas:** política judiciária; análise bibliométrica; governança
judicial; políticas judiciárias nacionais programáticas; PRISMA.

**Descartada:** "avaliação de políticas", por sobreposição com "políticas
judiciárias nacionais programáticas". O aceite registra 6 termos; o limite do
evento é 5.

## Mudança de critério de contagem

O preflight de 04/06 declarou **8.638 palavras** para o trabalho completo. Esse
número **exclui o texto contido em tabelas**. Pelo mesmo arquivo DOCX, a contagem
que inclui tabelas — equivalente à do contador do Word — resultava em **9.782**,
acima do teto de 9.000.

**Decisão (01/08/2026):** adotar o critério conservador. O teto de 9.000 passa a
ser aplicado sobre a contagem **com tabelas**. A norma do evento determina que a
contagem inclui título, referências e pós-textuais, e não abre exceção para
tabelas.

Consequência: o texto foi reduzido para caber no critério mais estrito.

## Verificações

| Critério | Resultado | Status |
| --- | ---: | --- |
| Título idêntico ao do resumo aceito | diff vazio | OK |
| Título — extensão | 13 palavras | Acima de 12; **prevalece a identidade com o resumo selecionado** |
| Autores | 4 | OK: até 5 |
| Trabalho completo — **com tabelas** | **8.970 palavras** | **OK: 4.000–9.000** (margem 30) |
| Trabalho completo — só parágrafos | 7.167 palavras | OK (critério antigo, informativo) |
| Resumo do trabalho completo | 222 palavras | OK: até 250 |
| Palavras-chave | 5, com ponto-e-vírgula | OK |
| Estrutura empírica | Introdução; Quadro Teórico-Conceitual; Métodos e Técnicas; Resultados; Discussão; Conclusões e Recomendações | OK |
| Notas | Sem notas de rodapé ou de fim | OK |
| Sumário | Ausente | OK |
| Referências e citações | APA por `apa.csl`; 43 entradas, todas as chaves resolvem | OK |
| Apêndices | Externalizados como material suplementar citável (A–E) | Ver §"Material suplementar" |
| Classificação por acepção | 170 registros do anel lexical, soma confere | Ver §"Classificação por acepção" |
| Fonte dos PDFs | Times New Roman (4 variantes) + LatinModernMath na equação do índice | OK |
| Layout | A4; Times New Roman 12; espaço simples; margens 3 cm superior/esquerda e 2 cm inferior/direita | OK |
| Trabalho completo PDF | 29 páginas; sem senha | OK |

## Material suplementar

Os quatro apêndices foram retirados do corpo do artigo e depositados como material
suplementar citável, em `supplementary/`:

| Item | Conteúdo |
| --- | --- |
| A | Strings de busca por base, exatamente como executadas |
| B | Manifesto do corpus de texto completo |
| C | Protocolo de reprodução dos dois pipelines |
| D | Codebook completo do IMO-PJNP |
| E | Codebook da classificação por acepção: padrões, precedência, resultado e limites |

**Justificativa metodológica.** A externalização segue a recomendação da extensão
PRISMA-S, que admite as estratégias de busca como material suplementar. O que é
necessário à **avaliação crítica** dos resultados permanece no corpo do artigo:
desenho da busca, fluxo PRISMA, dimensões do índice, pesos, fórmula, regra de
codificação, tratamento de ausência documental, limites de inferência e análise de
sensibilidade. O depósito acrescenta detalhe de **reprodução**, não substitui
informação necessária à leitura.

**Publicado em 01/08/2026** em repositório público dedicado:
`https://github.com/fgv-proj-icm/enajus-2026-537601-supplementary`

Contém os 4 materiais suplementares, o pipeline (`src/`), a documentação
metodológica (`docs/`) e os testes. Licenças CC BY 4.0 (documentação) e MIT
(código). Auditado antes da publicação: nenhum PDF de terceiro, nenhum e-mail real,
nenhum caminho local, nenhuma chave. `Public_Policy` e `pjnp-avaliacao` permanecem
**privados**.

O artigo cita o depósito como `@machado2026supl` e traz a seção *Disponibilidade de
Dados, Códigos e Materiais Suplementares* (p. 26).

> ⚠️ **Pendência: DOI ainda não emitido.** A referência resolve hoje para o
> repositório GitHub, que é mutável. Emitir via integração Zenodo–GitHub (release
> `v1.0`), acrescentar `doi = {...}` à entrada `machado2026supl` em `references.bib`
> e re-renderizar. **Não é bloqueante para submeter** — a referência já resolve para
> material público e versionado —, mas é o que torna a citação permanente.

## Classificação por acepção

Atende à exigência do parecer de explorar as acepções programática, comportamental e
doutrinária **encontradas** — ponto que o avaliador ligou ao objetivo geral.

A classificação incide sobre duas populações, e a distinção é o que a torna
informativa. O **anel lexical** (170) reúne os registros que empregam o rótulo antes
da restrição à acepção programática aplicada por `08c_reclassify_nuclear.py`; o **anel
nuclear final** (115) é o resultado dessa restrição. Classificar apenas o anel final
não demonstraria polissemia, porque os registros comportamentais já foram movidos para
o anel estendido.

| Acepção | Anel lexical | % | Periódicos | Anel nuclear |
| --- | ---: | ---: | ---: | ---: |
| programática | 38 | 22,4% | 28 | 38 |
| comportamental | 41 | 24,1% | 23 | 1 |
| doutrinária | 14 | 8,2% | 9 | 13 |
| indeterminado | 77 | 45,3% | 53 | 63 |
| **total** | **170** | **100%** | **112** | **115** |

| Verificação | Resultado | Status |
| --- | --- | --- |
| Soma das acepções = anel lexical | 170 = 170 | OK |
| Anel final é subconjunto do lexical | 115 de 170, 0 órfãos | OK |
| Determinismo (duas execuções) | SHA-256 idêntico nas 3 saídas | OK |
| Testes unitários | 78 (47 anteriores + 31 novos) | OK |
| Schema do corpus congelado | 0 erros, 0 duplicatas, 0 inconsistências PRISMA | OK |
| Composição do anel nuclear | Inalterada — nenhum arquivo de `data/` modificado | OK |

**Salvaguarda.** As listas `PROGRAMMATIC_PATTERNS`, `BEHAVIORAL_PATTERNS` e
`PENAL_PATTERNS` foram extraídas de `08c_reclassify_nuclear.py` para
`src/utils/acepcoes.py` sem alteração. A equivalência da decisão de anel foi verificada
registro a registro contra `data/interim/05_reclassification_log.csv`: **170 registros,
zero divergências** nos quatro motivos de reclassificação. `DOCTRINAL_PATTERNS` é
acréscimo desta rodada e não participa da decisão de anel.

**Duas correções de precisão** foram introduzidas apenas no classificador novo, sem
retroagir ao corpus congelado: as regex passam a ser avaliadas dentro de cada campo
(antes, `judicial policy.*administration` atravessava título → periódico e lia um
estudo de *policy-making* na *Public Administration Review* como programático); e a
pontuação tipográfica é normalizada (o HYPHEN U+2010 em "Judicial Policy‐Making"
impedia o casamento com `policy[\s-]?making`). O primeiro caso permanece no anel
nuclear como vazamento residual declarado — é o único registro comportamental entre os
115.

## Integridade

| Arquivo | SHA-256 |
| --- | --- |
| `enajus_2026_trabalho_completo.pdf` | `7570F8AC2A929E698DD06B93FFB252445DB38930CAA02B0FC60BF88403B39136` |
| `enajus_2026_trabalho_completo.docx` | `759A426D510905FD5BEA6E8A14AE9160147D16237E49B071EFF3F5F069AB39E6` |

Hashes anteriores (rodada de 01/08/2026), para rastreabilidade:
`FF50…C626` (PDF) e `6A50…78D8` (DOCX).

## Reprodução

```powershell
cd C:\Users\Adm\OneDrive\02_Academico\Producao_Cientifica\GitHub\Lab Lepp\02_pesquisa\Public_Policy
$env:PATH = "C:\Program Files\R\R-4.6.1\bin\x64;$env:PATH"
.\writing\build_enajus.ps1
```

A tabela das acepções é lida de `outputs/tables/acepcoes_summary.csv`, versionado. Para
regerá-la a partir do corpus:

```powershell
python src/pipelines/10b_classify_acepcoes.py
python -m pytest tests/ -q
```

O passo integra `make pipeline` (em `PIPELINE_STEPS`, após `10_export_bibliometrix.py`).

Requisitos verificados em 01/08/2026: Quarto 1.10.18; R 4.6.1 com `bibliometrix`,
`tidyverse`, `knitr`, `scales`, `patchwork`, `ggrepel`, `igraph`, `RColorBrewer`;
XeLaTeX (TeX Live 2026). As tabelas do IMO-PJNP são lidas de
`../../pjnp-avaliacao/outputs/tables` — os dois repositórios precisam estar lado a
lado.

## Fontes oficiais

- https://enajus.org.br/submissao-de-trabalhos/
- https://enajus.org.br/temas-de-interesse/
- https://enajus.org.br/datas-importantes/
