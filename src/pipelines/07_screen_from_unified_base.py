"""
07_screen_from_unified_base.py
Triagem (CORE / ADJACENTE / REVISAR) a partir da unified_base.csv (v6).

Regras:
- Combina (a) bucket por query_term + (b) dicionário auditável em title/abstract/concepts/journal.
- Gera CSV triage-ready + relatório md + meta json com hashes.

Uso:
  python 07_screen_from_unified_base.py --input data/final/unified_base.csv --outdir data/final/audit

Obs.: Ajuste os dicionários CORE_TERMS / ADJACENT_TERMS conforme seu codebook.
"""
from __future__ import annotations
from pathlib import Path
import argparse, json, hashlib, datetime, re
import pandas as pd
import numpy as np

CORE_TERMS = [
    "judicial policy", "judicial policies", "política judiciária", "políticas judiciárias",
    "judicial administration", "court administration", "judicial governance", "court governance",
    "judicial council", "conselho nacional de justiça", "cnj",
    "judicial reform", "reforma judicial", "reforma do judiciário",
    "court management", "judicial management", "case management",
    "backlog", "caseload", "court efficiency", "judicial efficiency",
    "performance", "court performance", "access to justice", "acesso à justiça",
    "e-justice", "digital justice", "court modernization", "judicial modernization",
    "governance", "public administration", "policy evaluation", "evaluation",
]

ADJACENT_TERMS = [
    "judicial review", "constitutional court", "constitutional law", "supreme court",
    "case law", "jurisprudence", "precedent", "stare decisis", "judicialization", "judicialisation"
]

TEXT_COLS = ["title", "abstract", "concepts", "journal", "query_term"]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_str(x) -> str:
    if pd.isna(x):
        return ""
    return str(x)

def count_hits(text: str, terms: list[str]) -> list[str]:
    hits = []
    for t in terms:
        if t in text:
            hits.append(t)
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Caminho para unified_base.csv")
    ap.add_argument("--outdir", required=True, help="Diretório de saída")
    args = ap.parse_args()

    in_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    # texto combinado
    df["_text_all"] = (
        df[TEXT_COLS].apply(lambda row: " | ".join(safe_str(v) for v in row), axis=1).str.lower()
    )

    df["core_hits"] = df["_text_all"].apply(lambda t: count_hits(t, CORE_TERMS))
    df["adjacent_hits"] = df["_text_all"].apply(lambda t: count_hits(t, ADJACENT_TERMS))
    df["core_hit_count"] = df["core_hits"].apply(len)
    df["adjacent_hit_count"] = df["adjacent_hits"].apply(len)

    # bucket por query_term (origem)
    q = df["query_term"].fillna("").astype(str).str.lower()
    df["query_bucket"] = np.select(
        [
            q.str.contains("judicial review"),
            q.str.contains("access to justice"),
            q.str.contains("judicial administration") | q.str.contains("court administration"),
            q.str.contains("judicial governance") | q.str.contains("court governance"),
            q.str.contains("judicial policy") | q.str.contains("judicial policies") | q.str.contains("política judiciária") | q.str.contains("políticas judiciárias"),
            q.str.contains("judicial reform") | q.str.contains("reforma judicial") | q.str.contains("reforma do judiciário"),
            q.str.contains("conselho nacional de justiça") | q.eq("cnj"),
        ],
        [
            "adjacent_judicial_review",
            "core_or_adjacent_access_to_justice",
            "core_admin",
            "core_governance",
            "core_policy_label",
            "core_reform",
            "core_cnj_brazil",
        ],
        default="other_or_unknown",
    )

    # escopo por texto
    df["scope_text"] = np.select(
        [
            (df["core_hit_count"] > 0) & (df["adjacent_hit_count"] == 0),
            (df["core_hit_count"] > 0) & (df["adjacent_hit_count"] > 0),
            (df["core_hit_count"] == 0) & (df["adjacent_hit_count"] > 0),
        ],
        ["core", "core_with_adjacent_signals", "adjacent"],
        default="unknown",
    )

    core_query_set = {"core_admin", "core_governance", "core_policy_label", "core_reform", "core_cnj_brazil"}
    adj_query_set = {"adjacent_judicial_review"}

    df["scope_suggested"] = np.select(
        [
            df["scope_text"].isin(["core", "core_with_adjacent_signals"]),
            (df["scope_text"] == "unknown") & df["query_bucket"].isin(list(core_query_set)),
            (df["scope_text"] == "adjacent") | df["query_bucket"].isin(list(adj_query_set)),
            (df["scope_text"] == "unknown") & (df["query_bucket"] == "core_or_adjacent_access_to_justice"),
        ],
        ["CORE", "CORE_low_text", "ADJACENTE", "REVISAR_access_to_justice"],
        default="REVISAR",
    )

    df["scope_confidence"] = np.select(
        [
            (df["scope_suggested"] == "CORE") & (df["core_hit_count"] >= 2),
            (df["scope_suggested"] == "CORE") & (df["core_hit_count"] == 1),
            (df["scope_suggested"] == "CORE_low_text"),
            (df["scope_suggested"] == "ADJACENTE") & (df["adjacent_hit_count"] >= 2),
            (df["scope_suggested"] == "ADJACENTE") & (df["adjacent_hit_count"] == 1),
            df["scope_suggested"].astype(str).str.startswith("REVISAR"),
        ],
        [0.85, 0.70, 0.55, 0.80, 0.65, 0.50],
        default=0.45,
    )

    df["scope_reason_terms"] = df.apply(
        lambda r: ";".join(sorted(set((r["core_hits"] or [])[:10] + (r["adjacent_hits"] or [])[:10]))),
        axis=1,
    )

    df["flag_editorial_like"] = df["type"].fillna("").astype(str).str.lower().str.contains("editorial|erratum|note")

    out_csv = outdir / "unified_base_v6_triage_ready_v1.csv"
    df.drop(columns=["_text_all"]).to_csv(out_csv, index=False, encoding="utf-8-sig")

    # relatório
    report = outdir / "unified_base_v6_triage_report_v1.md"
    lines = []
    lines.append("# Relatório de triagem — unified_base v6 (v1)\n\n")
    lines.append(f"- Linhas: **{len(df)}**\n")
    lines.append(f"- Query terms únicos: **{df['query_term'].nunique()}**\n\n")
    lines.append("## Distribuição por bucket de query\n")
    for k, v in df["query_bucket"].value_counts().items():
        lines.append(f"- {k}: {v}\n")
    lines.append("\n## Sugestão de escopo (texto+query)\n")
    for k, v in df["scope_suggested"].value_counts().items():
        lines.append(f"- {k}: {v}\n")
    lines.append("\n## Nota importante\n")
    lines.append("- `query_term` em base deduplicada pode refletir apenas uma das queries que capturou o registro; por isso, não exclua só por query.\n")
    report.write_text("".join(lines), encoding="utf-8")

    meta = {
        "generated_at": datetime.datetime.now().isoformat(),
        "input_file": str(in_path),
        "input_sha256": sha256_file(in_path),
        "output_csv": str(out_csv),
        "output_sha256": sha256_file(out_csv),
        "report_file": str(report),
        "report_sha256": sha256_file(report),
        "rules": {
            "core_terms_count": len(CORE_TERMS),
            "adjacent_terms_count": len(ADJACENT_TERMS),
            "core_query_buckets": sorted(list(core_query_set)),
            "adjacent_query_buckets": sorted(list(adj_query_set)),
        },
    }
    meta_path = outdir / "unified_base_v6_triage_meta_v1.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK -> {out_csv.name}")

if __name__ == "__main__":
    main()
