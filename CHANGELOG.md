# Changelog

## 2026-04-28

- Criado `config.yml` com seed, modo offline e flags para suplemento brasileiro/PoP/OpenAlex.
- Adicionado `src/pipelines/14_rebuild_full_pipeline.py` como comando único do pipeline.
- Adicionado `src/pipelines/16_brazil_supplement_compare.py` para comparação rastreável de produção brasileira local.
- Atualizados logs reprodutíveis: `logs/prisma_flow.csv` e `logs/dedup_impact.csv`.
- Atualizado `src/pipelines/11_enrich_references.py` para exportar rede de co-citação em `outputs/network/`.
- Criado `docs/REPRO_AUDIT.md` com mapa do fluxo, riscos e comando de reprodução.
- Revisado `relatorio_bibliometrico_politica_judiciaria.qmd` com PRISMA adaptado, rótulos/campos cognatos, suplemento brasileiro, temporalidade CNJ, co-citação e limitações.
- Acrescentadas referências oficiais CNJ/CNMP e literatura de capacidades estatais em `references.bib`.
