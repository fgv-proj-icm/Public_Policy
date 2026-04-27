cat > src/pipelines/15_build_scielo_candidate_journals.py <<'PY'
import re, requests, pandas as pd
from pathlib import Path

Path("data/interim").mkdir(parents=True, exist_ok=True)

URL="http://articlemeta.scielo.org/api/v1/journal/"
journals = requests.get(URL, params={"collection":"scl","format":"json"}, timeout=180).json()

patterns = [
    "direito","justiça","judici","tribunal","política",
    "serviço público","administração pública","gestão pública",
    "políticas públicas","estado","governo","reforma"
]
rx = re.compile("|".join(re.escape(p) for p in patterns), re.I)

rows=[]
for j in journals:
    title = ""
    for vf in (j.get("v100") or []):
        if isinstance(vf, dict) and isinstance(vf.get("_"), str) and vf["_"].strip():
            title = vf["_"].strip()
            break
    issns = j.get("issns") or []
    if title and rx.search(title):
        rows.append({"journal_title": title, "issns": ";".join(issns), "code": j.get("code","")})

df = pd.DataFrame(rows).sort_values("journal_title")
out="data/interim/scielo_candidate_journals.csv"
df.to_csv(out, index=False, encoding="utf-8-sig")
print(f"Salvo: {out} (n={len(df)})")
print(df.head(30).to_string(index=False))
PY