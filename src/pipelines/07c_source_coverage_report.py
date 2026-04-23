from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
AUDIT_DIR = FINAL_DIR / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = FINAL_DIR / "unified_base.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

group_col = "source_file" if "source_file" in df.columns else "source"

rows = []
for source_name, group in df.groupby(group_col):
    row = {"source_name": source_name, "n_rows": len(group)}
    for col in df.columns:
        series = group[col]
        pct_present = ((series.notna()) & (series.astype(str).str.strip() != "")).mean() * 100
        row[f"{col}__pct_present"] = round(pct_present, 2)
    rows.append(row)

coverage = pd.DataFrame(rows)
coverage.to_csv(AUDIT_DIR / "coverage_by_source.csv", index=False, encoding="utf-8-sig")

print("Relatório salvo em:", AUDIT_DIR / "coverage_by_source.csv")
print(coverage.to_string(index=False))
