# Auditoria de Reprodutibilidade

Data: 2026-04-28  
Ambiente: Windows/PowerShell, Python 3.14.4, Quarto 1.9.37

## Fluxo ponta a ponta

1. **Coleta/snapshots brutos**  
   `data/raw/*_refined.csv` e `data/raw/semantic_scholar_results_core.csv` alimentam a rodada principal. SciELO e Google Scholar/PoP existem como fontes opcionais/suplementares quando seus snapshots estão presentes.

2. **Unificação multibase**  
   `src/pipelines/06_merge_cross_base.py` padroniza colunas e gera `data/interim/01_merged_all_sources.csv`.

3. **Deduplicação**  
   `src/pipelines/07_dedup_cross_base.py` deduplica por `doi_norm`; quando DOI está ausente, usa `title_norm + publication_year + journal_norm`. Saídas: `data/interim/02_deduplicated.csv` e `logs/dedup_impact.csv`.

4. **Triagem PRISMA e anéis**  
   `src/pipelines/08_screen_prisma.py` classifica registros em `nuclear`, `extended` ou `excluded`. A regra nuclear usa rótulos explícitos; a regra estendida usa campos cognatos.

5. **Limpeza e reclassificação**  
   `08b_clean_and_enrich.py`, `08c_reclassify_nuclear.py` e `08d_final_nuclear_adjustment.py` removem fora de escopo, enriquecem metadados e congelam o corpus em `data/interim/06_frozen_corpus.csv`.

6. **PRISMA e exportação**  
   `09_prisma_flow.py` gera `docs/04_prisma_flow.md`, `data/interim/prisma_flow.html` e `logs/prisma_flow.csv`. `10_export_bibliometrix.py` gera `data/final/corpus_complete.csv`, `corpus_nuclear.csv` e `corpus_extended.csv`.

7. **Co-citação e completude**  
   `11_enrich_references.py` enriquece referências do núcleo via OpenAlex e exporta pares em `data/interim/07_cocitation_matrix_edges.csv` e `outputs/network/`. `12_metadata_completeness.py` gera `data/interim/08_metadata_completeness.csv`.

8. **Suplemento brasileiro**  
   `16_brazil_supplement_compare.py` compara `data/brazil_supplement.csv` e snapshots locais SciELO/PoP com o corpus congelado. Saída: `outputs/tables/brazil_supplement_comparison.csv`.

9. **Relatório**  
   `relatorio_bibliometrico_politica_judiciaria.qmd` lê os CSVs finais e renderiza DOCX/HTML via Quarto.

## Pontos frágeis

- **Idioma**: 47,5% preenchido no corpus completo; afeta inferências por distribuição linguística.
- **Abstract**: 14,8% preenchido no corpus completo e 9,6% no núcleo; restringe co-word e triagem semântica baseada em resumo.
- **Autores**: 52,7% preenchido no corpus completo; limita análise de autoria e colaboração.
- **Referências**: apenas 31 de 115 registros nucleares têm referências indexadas via OpenAlex; co-citação é exploratória.
- **Fontes brasileiras**: revistas de tribunais, repositórios institucionais e periódicos jurídicos podem não estar cobertos nas quatro bases principais.
- **APIs externas**: OpenAlex/Semantic Scholar/Scopus/Crossref podem variar por rate limit, credencial, paginação e atualização incremental. A execução reproduzível deve usar snapshots locais em `data/raw`.

## Comando reprodutível

```powershell
$env:PYTHONIOENCODING='utf-8'
python src\pipelines\14_rebuild_full_pipeline.py --offline --skip-enrich
quarto render relatorio_bibliometrico_politica_judiciaria.qmd --to docx
```

Observação: `--skip-enrich` evita nova chamada à API OpenAlex e reutiliza o snapshot de referências já salvo. Para atualizar referências, defina `pipeline.refresh_openalex_references: true` em `config.yml`.
