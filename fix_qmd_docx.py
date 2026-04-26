from pathlib import Path
import re
import shutil
import sys

QMD = Path("relatorio_bibliometrico_politica_judiciaria.qmd")

if not QMD.exists():
    print(f"Arquivo não encontrado: {QMD}")
    sys.exit(1)

text = QMD.read_text(encoding="utf-8")

# Backup
backup = QMD.with_suffix(".qmd.bak")
shutil.copy2(QMD, backup)

# 1) Inserir safe_kable no setup, se ainda não existir
if "safe_kable <- function" not in text:
    # tenta inserir depois da função fmt_1, se existir
    pattern = r'(fmt_1 <- function\(x\) \{.*?\n\})'
    replacement = r"""\1

safe_kable <- function(data, align = NULL, caption = NULL) {
  knitr::kable(data, align = align, caption = caption)
}"""
    text, n = re.subn(pattern, replacement, text, count=1, flags=re.S)

    if n == 0:
        # fallback: inserir depois do bloco options(...)
        pattern2 = r'(options\([\s\S]*?\)\n)'
        replacement2 = r"""\1
safe_kable <- function(data, align = NULL, caption = NULL) {
  knitr::kable(data, align = align, caption = caption)
}
"""
        text, _ = re.subn(pattern2, replacement2, text, count=1, flags=re.S)

# 2) Trocar |> kable(...) por |> safe_kable(...)
text = re.sub(r'(\|\>\s*)kable\(', r'\1safe_kable(', text)

# 3) Remover qualquer linha contendo kable_styling(...)
text = re.sub(r'^[^\n]*kable_styling\([^\n]*\n?', '', text, flags=re.M)

# 4) Remover qualquer linha contendo column_spec(...)
text = re.sub(r'^[^\n]*column_spec\([^\n]*\n?', '', text, flags=re.M)

# 5) Limpar linhas com pipes “órfãos” deixados por remoção parcial
text = re.sub(r'\|\>\s*\n\s*\n', '\n', text)
text = re.sub(r'\n{3,}', '\n\n', text)

QMD.write_text(text, encoding="utf-8")

print("Patch aplicado com sucesso.")
print(f"Backup criado em: {backup}")
print(f"Arquivo corrigido: {QMD}")