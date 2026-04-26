from pathlib import Path
import re
import shutil

qmd = Path("relatorio_bibliometrico_politica_judiciaria.qmd")
text = qmd.read_text(encoding="utf-8")

backup = qmd.with_suffix(".qmd.pipefix.bak")
shutil.copy2(qmd, backup)

# remove linhas que terminam com |> e vêm antes de linha vazia, fim de chunk ou fechamento ```
text = re.sub(r'\|\>\s*\n(\s*\n)', r'\n\1', text)
text = re.sub(r'\|\>\s*\n(\s*```)', r'\n\1', text)

# remove |> no fim da linha imediatamente antes do fim do chunk
text = re.sub(r'(\s*safe_kable\([^\n]*\))\s*\|\>\s*$', r'\1', text, flags=re.M)

qmd.write_text(text, encoding="utf-8")

print(f"Corrigido: {qmd}")
print(f"Backup: {backup}")