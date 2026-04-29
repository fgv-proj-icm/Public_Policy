# Makefile — Bibliometria "Política Judiciária"
# Comando 1-linha para reproduzir: make pipeline
#
# Alvos disponíveis:
#   make setup     — instala dependências Python
#   make pipeline  — roda o pipeline completo (offline, sem enrich de API)
#   make brazil    — roda a curadoria do suplemento Brasil (step 18)
#   make enrich    — enriquece metadados via OpenAlex (requer rede)
#   make report    — renderiza o relatório Quarto (.docx)
#   make test      — roda os testes pytest
#   make validate  — valida schema do corpus congelado
#   make all       — setup + pipeline + validate + test

PYTHON ?= python
PIPELINE_SCRIPT = src/pipelines/14_rebuild_full_pipeline.py
CORPUS_V1 = data/interim/06_frozen_corpus.csv
CORPUS_V2 = data/interim/07_frozen_corpus_v2.csv
REPORT_QMD = relatorio_bibliometrico_politica_judiciaria.qmd

.PHONY: setup pipeline brazil enrich report test validate all help

help:
	@echo "Alvos disponíveis:"
	@echo "  make setup     — instala dependências Python"
	@echo "  make pipeline  — pipeline completo (offline, sem API)"
	@echo "  make brazil    — curadoria do suplemento Brasil (step 18)"
	@echo "  make enrich    — enriquecimento OpenAlex (requer rede)"
	@echo "  make report    — renderiza relatório Quarto (.docx)"
	@echo "  make test      — pytest (47 testes unitários)"
	@echo "  make validate  — valida schema do corpus congelado"
	@echo "  make all       — setup + pipeline + validate + test"
	@echo ""
	@echo "Reprodução completa (1 linha):"
	@echo "  pip install -r requirements.txt && make pipeline"

setup:
	$(PYTHON) -m pip install -r requirements.txt

pipeline:
	$(PYTHON) $(PIPELINE_SCRIPT) --offline --skip-enrich

brazil:
	$(PYTHON) src/pipelines/18_brazil_curation_merge.py

enrich:
	$(PYTHON) src/pipelines/19_enrich_metadata.py --force-online

report:
	quarto render $(REPORT_QMD) --to docx

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

validate:
	@if [ -f "$(CORPUS_V2)" ]; then \
		CORPUS="$(CORPUS_V2)"; \
	else \
		CORPUS="$(CORPUS_V1)"; \
	fi; \
	$(PYTHON) -c "\
import sys, pandas as pd; sys.path.insert(0, 'src'); \
from validation.schema_check import validate_schema, check_duplicates, check_prisma_consistency; \
df = pd.read_csv('$$CORPUS', dtype=str); \
errs = validate_schema(df); \
dups = check_duplicates(df); \
prisma_errs = check_prisma_consistency('logs/prisma_flow.csv'); \
print(f'Schema: {len(errs)} erro(s)'); \
[print(f'  ! {e}') for e in errs]; \
print(f'Duplicatas por DOI: {dups[\"by_doi\"]}'); \
print(f'Duplicatas por fallback: {dups[\"by_fallback\"]}'); \
print(f'PRISMA: {len(prisma_errs)} inconsistência(s)'); \
[print(f'  ! {e}') for e in prisma_errs]; \
exit(len(errs) + len(prisma_errs))"

all: setup pipeline validate test
