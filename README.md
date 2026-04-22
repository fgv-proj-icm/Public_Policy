# Políticas Públicas
Pesquisas sobre Políticas Públicas
# 1. Descompacte o zip e entre na pasta
cd judicial_review

# 2. Instale dependências
pip install requests pandas rapidfuzz networkx matplotlib pyyaml pyarrow tenacity

# 3. Configure .env com as chaves das APIs
# (OpenAlex é gratuito; Scopus e WoS requerem acesso institucional)

# 4. Execute os pipelines com os dados reais
PYTHONPATH=. python src/pipelines/01_collect.py
PYTHONPATH=. python src/pipelines/02_normalize_dedup.py
PYTHONPATH=. python src/pipelines/03_audit.py
PYTHONPATH=. python src/pipelines/04_score_agenda.py
PYTHONPATH=. python src/pipelines/05_bibliometrics_full.py

# 5. Gere o Word
quarto render politicas_judiciarias_bibliometria_v2.qmd --to docx
