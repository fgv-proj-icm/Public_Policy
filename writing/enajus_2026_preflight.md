# EnAJUS 2026 — Preflight da Submissão (ID 537601)

**Data da verificação:** 1 de agosto de 2026
**Etapa:** Trabalho completo (2ª etapa — versão identificada)
**ID ENAJUS:** 537601
**Prazo:** 25/09/2026
**Tipo de trabalho:** Trabalho empírico concluído
**Tema de interesse:** 9) Políticas Públicas de Justiça. Formulação, Implementação e Avaliação
**Título:** Política Judiciária como Campo Emergente: Da Cartografia Bibliométrica à Maturidade Observável das PJNP

> Substitui o preflight de 04/06/2026, que registrava o título anterior
> ("Uma Análise Bibliométrica Multibase", 9 palavras) e um critério de contagem
> diferente — ver §"Mudança de critério de contagem".

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
| Trabalho completo — **com tabelas** | **8.956 palavras** | **OK: 4.000–9.000** (margem 44) |
| Trabalho completo — só parágrafos | 7.049 palavras | OK (critério antigo, informativo) |
| Resumo do trabalho completo | 222 palavras | OK: até 250 |
| Palavras-chave | 5, com ponto-e-vírgula | OK |
| Estrutura empírica | Introdução; Quadro Teórico-Conceitual; Métodos e Técnicas; Resultados; Discussão; Conclusões e Recomendações | OK |
| Notas | Sem notas de rodapé ou de fim | OK |
| Sumário | Ausente | OK |
| Referências e citações | APA por `apa.csl`; 43 entradas, todas as chaves resolvem | OK |
| Apêndices | Externalizados como material suplementar citável | Ver §"Material suplementar" |
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

## Integridade

| Arquivo | SHA-256 |
| --- | --- |
| `enajus_2026_trabalho_completo.pdf` | `FF500338964FAD47551E86D2A2F52A418A12D9AB17357F15A6C7DC1EA44EC626` |
| `enajus_2026_trabalho_completo.docx` | `6A5030B511C0773A41758934A6F97A34917DDE33F6FDDC1EB0EFE894AD9878D8` |

## Reprodução

```powershell
cd C:\Users\Adm\OneDrive\02_Academico\Producao_Cientifica\GitHub\Lab Lepp\02_pesquisa\Public_Policy
$env:PATH = "C:\Program Files\R\R-4.6.1\bin\x64;$env:PATH"
.\writing\build_enajus.ps1
```

Requisitos verificados em 01/08/2026: Quarto 1.10.18; R 4.6.1 com `bibliometrix`,
`tidyverse`, `knitr`, `scales`, `patchwork`, `ggrepel`, `igraph`, `RColorBrewer`;
XeLaTeX (TeX Live 2026). As tabelas do IMO-PJNP são lidas de
`../../pjnp-avaliacao/outputs/tables` — os dois repositórios precisam estar lado a
lado.

## Fontes oficiais

- https://enajus.org.br/submissao-de-trabalhos/
- https://enajus.org.br/temas-de-interesse/
- https://enajus.org.br/datas-importantes/
