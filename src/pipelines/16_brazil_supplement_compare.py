"""
16_brazil_supplement_compare.py
===============================
Compara o corpus congelado com uma rodada suplementar brasileira rastreavel.

O suplemento nao altera o corpus principal por padrao. Ele consolida itens de
data/brazil_supplement.csv e snapshots locais SciELO/PoP, deduplica por DOI ou
titulo+ano+periodico e reporta quantos itens ja estavam no corpus congelado.
"""

from pathlib import Path
import re
import pandas as pd
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config.yml"
INTERIM_DIR = BASE_DIR / "data" / "interim"
OUTPUT_TABLES = BASE_DIR / "outputs" / "tables"
OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

STANDARD_COLS = [
    "source", "source_id", "title", "doi", "publication_year", "journal",
    "type", "language", "cited_by_count", "authors", "abstract", "url",
    "criteria_note", "ring",
]

BR_TERMS = [
    "politica judiciaria", "politicas judiciarias", "política judiciária",
    "políticas judiciárias", "politica judicial", "política judicial",
    "governanca judicial", "governança judicial", "administracao judiciaria",
    "administração judiciária", "conselho nacional de justica",
    "conselho nacional de justiça", "cnj", "fgv", "idp", "unb",
]


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


def ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[STANDARD_COLS]


def norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"https?://doi\.org/", "", text)
    return text


def norm_key(df: pd.DataFrame) -> pd.Series:
    doi = df["doi"].fillna("").map(norm_text)
    title = df["title"].fillna("").map(norm_text)
    year = df["publication_year"].fillna("").astype(str).str.extract(r"((?:19|20)\d{2})", expand=False).fillna("")
    journal = df["journal"].fillna("").map(norm_text)
    fallback = title + "::" + year + "::" + journal
    return doi.where(doi != "", fallback)


def load_curated(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=STANDARD_COLS)
    return ensure_cols(pd.read_csv(path, dtype=str))


def load_raw_standard(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=STANDARD_COLS)
    df = pd.read_csv(path, dtype=str)
    if "Title" in df.columns:
        out = pd.DataFrame()
        out["source"] = "google_scholar_pop"
        out["source_id"] = df.get("ArticleURL", df.get("DOI", "")).fillna("")
        out["title"] = df.get("Title", "").fillna("")
        out["doi"] = df.get("DOI", "").fillna("")
        out["publication_year"] = df.get("Year", "").fillna("")
        out["journal"] = df.get("Source", "").fillna("")
        out["type"] = df.get("Type", "").fillna("")
        out["language"] = ""
        out["cited_by_count"] = df.get("Cites", "0")
        out["authors"] = df.get("Authors", "").fillna("")
        out["abstract"] = df.get("Abstract", "").fillna("")
        out["url"] = df.get("ArticleURL", "").fillna("")
        out["criteria_note"] = "snapshot Publish or Perish/Google Scholar"
        return ensure_cols(out)
    return ensure_cols(df)


def is_brazil_candidate(row) -> bool:
    haystack = " ".join(
        norm_text(row.get(col, "")) for col in ["title", "journal", "abstract", "authors", "url", "criteria_note"]
    )
    return any(term in haystack for term in BR_TERMS)


def classify_ring(row) -> str:
    text = " ".join(norm_text(row.get(col, "")) for col in ["title", "abstract"])
    nuclear = [
        r"\bjudicial\s+polic(?:y|ies)\b",
        r"\bpol[ií]tica[s]?\s+judici[aá]ri[ao]s?\b",
        r"\bpol[ií]tica[s]?\s+judicial(?:es)?\b",
    ]
    for pat in nuclear:
        if re.search(pat, text, flags=re.IGNORECASE):
            return "nuclear"
    return "extended"


def main() -> None:
    config = load_config()
    raw_files = config.get("brazil_supplement", {}).get("raw_files", [])
    curated = Path(config.get("brazil_supplement", {}).get("curated_file", "data/brazil_supplement.csv"))
    if not curated.is_absolute():
        curated = BASE_DIR / curated

    frames = [load_curated(curated)]
    for rel in raw_files:
        path = BASE_DIR / rel
        frames.append(load_raw_standard(path))

    supplement = pd.concat(frames, ignore_index=True)
    supplement = supplement[supplement.apply(is_brazil_candidate, axis=1)].copy()
    if supplement.empty:
        supplement = pd.DataFrame(columns=STANDARD_COLS)
    supplement["dedup_key"] = norm_key(supplement)
    supplement = supplement[supplement["dedup_key"] != ":::"].drop_duplicates("dedup_key", keep="first")
    supplement["ring_supplement"] = supplement.apply(classify_ring, axis=1) if len(supplement) else []

    frozen_path = INTERIM_DIR / "06_frozen_corpus.csv"
    corpus = pd.read_csv(frozen_path, dtype=str) if frozen_path.exists() else pd.DataFrame(columns=STANDARD_COLS)
    corpus = ensure_cols(corpus)
    corpus["dedup_key"] = norm_key(corpus)

    existing = set(corpus["dedup_key"])
    supplement["already_in_frozen_corpus"] = supplement["dedup_key"].isin(existing)

    comparison = pd.DataFrame([
        {"metric": "corpus_principal_total", "n": len(corpus), "note": "Corpus congelado atual"},
        {"metric": "corpus_principal_nuclear", "n": int((corpus.get("ring", "") == "nuclear").sum()) if "ring" in corpus else 0, "note": "CORE_EX atual"},
        {"metric": "suplemento_br_candidatos", "n": len(supplement), "note": "Itens rastreaveis filtrados por termos/instituicoes brasileiras"},
        {"metric": "suplemento_br_ja_no_corpus", "n": int(supplement["already_in_frozen_corpus"].sum()) if len(supplement) else 0, "note": "Mesma chave DOI ou titulo+ano+periodico"},
        {"metric": "suplemento_br_novos", "n": int((~supplement["already_in_frozen_corpus"]).sum()) if len(supplement) else 0, "note": "Exigem curadoria antes de incorporar ao corpus principal"},
        {"metric": "suplemento_br_nuclear_estimado", "n": int((supplement.get("ring_supplement", "") == "nuclear").sum()) if len(supplement) else 0, "note": "Classificacao automatica exploratoria"},
    ])

    supplement_out = OUTPUT_TABLES / "brazil_supplement_candidates.csv"
    comparison_out = OUTPUT_TABLES / "brazil_supplement_comparison.csv"
    supplement.to_csv(supplement_out, index=False, encoding="utf-8-sig")
    comparison.to_csv(comparison_out, index=False, encoding="utf-8-sig")

    print("Suplemento Brasil")
    print(comparison.to_string(index=False))
    print(f"Arquivos: {comparison_out}, {supplement_out}")


if __name__ == "__main__":
    main()
