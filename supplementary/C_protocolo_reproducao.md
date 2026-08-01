# C — Protocolo de reprodução

Reproduz o Apêndice C do manuscrito, ampliado para cobrir as duas frentes.

**Semente analítica: 42**, fixa em todas as execuções. Nenhum número do manuscrito
foi digitado à mão; todos vêm dos pipelines.

## Frente A — Cartografia bibliométrica (`Public_Policy`)

```powershell
$env:PYTHONIOENCODING='utf-8'
pip install -r requirements.txt

python src\pipelines\14_rebuild_full_pipeline.py --offline --skip-enrich
python pdfs\download_pipeline_scielo.py
python pdfs\extrair_texto_pdfs.py
```

Alvos do `Makefile`:

| Alvo | Efeito |
| --- | --- |
| `make pipeline` | Reconstrói o corpus (offline, sem enriquecimento) |
| `make validate` | Valida o schema do corpus congelado |
| `make test` | 47 testes pytest |
| `make brazil` | Curadoria do suplemento Brasil (step 18) |
| `make enrich` | Enriquecimento OpenAlex — **requer rede** |

Artefatos: `data/final/corpus_complete.csv`, `corpus_extended.csv`,
`corpus_nuclear.csv`, `data/interim/06_frozen_corpus.csv`.
Logs: `logs/prisma_flow.csv`, `logs/dedup_impact.csv`.

## Frente B — Maturidade observável (`pjnp-avaliacao`)

```bash
git switch chore/enajus-2026     # o material ENAJUS não está em master
python -m pip install -r requirements.txt
python -m pjnp.run --input data/raw --out outputs --seed 42
```

Alvos: `make report` (pipeline + relatório), `make run` (`--skip-report`),
`make test`, `make lint`.

Artefatos em `outputs/tables/`: `pjnp_policy_features.csv`, `pjnp_indices_all.csv`,
`index_summary.csv`, `index_specifications.json`, `pjnp_clusters.csv`,
`cluster_diagnostics.csv`, `models_association_results.csv`,
`missingness_by_table.csv`.

> **Bloqueio conhecido.** `data/raw/*.xlsx` (`Base_painel.xlsx`, `Gov_PJNP.xlsx`,
> `Colegiados_PJNP.xlsx`) está no `.gitignore`. Um clone limpo **não** reproduz o
> pipeline. Os arquivos precisam ser obtidos do Painel PJNP do CNJ ou solicitados
> aos autores.

## Renderização do manuscrito

O manuscrito lê as tabelas da Frente B por caminho relativo
(`../../pjnp-avaliacao/outputs/tables`). Os dois repositórios devem estar lado a
lado no mesmo diretório-pai.

```powershell
cd Public_Policy
.\writing\build_enajus.ps1
```

O script normaliza o documento de referência DOCX (espaçamento simples, título em
preto 12 pt) e renderiza resumo expandido e trabalho completo.

Requisitos: Quarto ≥ 1.10, R ≥ 4.6 com `bibliometrix`, `tidyverse`, `knitr`,
`scales`, `patchwork`, `ggrepel`, `igraph`, `RColorBrewer`; XeLaTeX com Times New
Roman.

## Manifesto do pipeline PJNP

```json
{"seed": 42, "n_policies": "40", "n_initiatives": "253", "n_colegiados": "96",
 "selected_cluster_k": "6", "best_silhouette": "0.1843", "models": "15"}
```
