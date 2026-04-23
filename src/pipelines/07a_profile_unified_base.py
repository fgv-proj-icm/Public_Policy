from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
FINAL_DIR = BASE_DIR / "data" / "final"
AUDIT_DIR = FINAL_DIR / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = FINAL_DIR / "unified_base.csv"

df = pd.read_csv(INPUT_FILE, low_memory=False)

overview = pd.DataFrame(
    {
        "metric": ["n_rows", "n_cols"],
        "value": [len(df), len(df.columns)],
    }
)
overview.to_csv(AUDIT_DIR / "overview.csv", index=False, encoding="utf-8-sig")

missing = pd.DataFrame(
    {
        "column": df.columns,
        "n_missing": df.isna().sum().values,
        "pct_missing": (df.isna().mean().values * 100).round(2),
        "dtype": [str(df[c].dtype) for c in df.columns],
    }
).sort_values(["pct_missing", "n_missing"], ascending=False)

missing.to_csv(AUDIT_DIR / "missingness_by_column.csv", index=False, encoding="utf-8-sig")

if "source_file" in df.columns:
    source_dist = df["source_file"].fillna("N/D").value_counts().reset_index()
    source_dist.columns = ["source_file", "n"]
    source_dist.to_csv(AUDIT_DIR / "rows_by_source_file.csv", index=False, encoding="utf-8-sig")

print("Arquivo base analisado:", INPUT_FILE)
print("Linhas:", len(df))
print("Colunas:", len(df.columns))
print("Relatórios salvos em:", AUDIT_DIR)
print("\nTop 10 colunas com mais missing:")
print(missing.head(10).to_string(index=False))
