from pathlib import Path
import shutil
import re
import sys

qmd = Path("relatorio_bibliometrico_politica_judiciaria.qmd")

if not qmd.exists():
    print(f"Arquivo não encontrado: {qmd}")
    sys.exit(1)

text = qmd.read_text(encoding="utf-8")
backup = qmd.with_suffix(".qmd.tablesfix.bak")
shutil.copy2(qmd, backup)

lines = text.splitlines()
new_lines = []

for line in lines:
    if "kable_styling(" in line or "column_spec(" in line:
        continue
    new_lines.append(line)

text = "\n".join(new_lines)

# troca |> kable(...) por |> safe_kable(...)
text = re.sub(r'(\|\>\s*)kable\(', r'\1safe_kable(', text)

# remove pipe final em linhas com safe_kable(...)
text = re.sub(r'(safe_kable\([^\n]*\))\s*\|\>\s*$', r'\1', text, flags=re.M)

# remove pipe final em linhas com knitr::kable(...)
text = re.sub(r'(knitr::kable\([^\n]*\))\s*\|\>\s*$', r'\1', text, flags=re.M)

# limpa excesso de linhas vazias
text = re.sub(r'\n{3,}', '\n\n', text)

# garante existência da função safe_kable
if "safe_kable <- function" not in text:
    insert_after = r"(fmt_1 <- function\(x\)\s*\{.*?\n\})"
    replacement = r"""\1

safe_kable <- function(data, align = NULL, caption = NULL) {
  knitr::kable(data, align = align, caption = caption)
}"""
    text, n = re.subn(insert_after, replacement, text, count=1, flags=re.S)

    if n == 0:
        print("Aviso: não consegui inserir safe_kable automaticamente. Verifique o chunk setup.")

qmd.write_text(text, encoding="utf-8")

print("Correção aplicada com sucesso.")
print(f"Backup salvo em: {backup}")
print(f"Arquivo corrigido: {qmd}")
