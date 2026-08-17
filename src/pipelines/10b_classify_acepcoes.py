"""
10b_classify_acepcoes.py
========================
Classificação por acepção de "política judiciária" nos registros que usam o rótulo.

Responde à exigência do parecer ENAJUS 2026 (ID 537601) de explorar as acepções
programática, comportamental e doutrinária efetivamente encontradas no corpus, e
não apenas de distingui-las conceitualmente.

DUAS POPULAÇÕES, e a distinção importa:

  anel lexical (170)  Registros que empregam expressamente o rótulo, ANTES da
                      restrição à acepção programática aplicada por
                      08c_reclassify_nuclear.py. É a população em que a polissemia
                      pode ser observada, porque nela as três acepções convivem.

  anel final (115)    Resultado da restrição, usado em todo o resto do manuscrito.
                      Por construção quase não contém registros comportamentais —
                      08c os moveu para o anel estendido. Classificá-lo isoladamente
                      não demonstraria polissemia alguma.

O contraste entre as duas é o que torna auditável a cadeia de derivação: mostra
com números que a cartografia RESTRINGE o que o índice pode medir.

Nenhum registro muda de anel aqui. A composição do corpus congelado permanece
intacta; esta é uma camada analítica sobre ela.

Entrada : data/interim/04_cleaned.csv    (anel lexical, ring == "nuclear")
          data/final/corpus_nuclear.csv  (anel final, para marcar sobrevivência)
Saída   : data/final/nuclear_acepcoes.csv        (uma linha por registro do lexical)
          outputs/tables/acepcoes_summary.csv    (contagens nas duas populações)
          outputs/tables/acepcoes_exemplares.csv (exemplares para o manuscrito)

Uso:
    python src/pipelines/10b_classify_acepcoes.py
"""

from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src"))
from utils.acepcoes import ACEPCOES, classify_frame

INTERIM_DIR = BASE_DIR / "data" / "interim"
FINAL_DIR = BASE_DIR / "data" / "final"
TABLES_DIR = BASE_DIR / "outputs" / "tables"

INPUT_LEXICAL = INTERIM_DIR / "04_cleaned.csv"
INPUT_FINAL = FINAL_DIR / "corpus_nuclear.csv"
OUTPUT_RECORDS = FINAL_DIR / "nuclear_acepcoes.csv"
OUTPUT_SUMMARY = TABLES_DIR / "acepcoes_summary.csv"
OUTPUT_EXAMPLES = TABLES_DIR / "acepcoes_exemplares.csv"

# Quantos exemplares por acepção exportar para o manuscrito.
N_EXAMPLES = 3

RECORD_COLUMNS = [
    "title", "doi", "publication_year", "journal", "language", "cited_by_count",
    "acepcao", "subtipo", "matched_pattern", "matched_field", "no_anel_final",
]


def _norm_title(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower()


def summarize(df: pd.DataFrame, populacao: str) -> pd.DataFrame:
    total = len(df)
    rows = []
    for acepcao in ACEPCOES:
        subset = df[df["acepcao"] == acepcao]
        rows.append({
            "populacao": populacao,
            "acepcao": acepcao,
            "n": len(subset),
            "pct": round(100 * len(subset) / total, 1) if total else 0.0,
            "mediana_citacoes": float(subset["cited_by_count"].median()) if len(subset) else 0.0,
            "periodicos_distintos": int(subset["journal"].dropna().nunique()),
        })
    rows.append({
        "populacao": populacao,
        "acepcao": "total",
        "n": total,
        "pct": 100.0 if total else 0.0,
        "mediana_citacoes": float(df["cited_by_count"].median()) if total else 0.0,
        "periodicos_distintos": int(df["journal"].dropna().nunique()),
    })
    return pd.DataFrame(rows)


def build_examples(df: pd.DataFrame) -> pd.DataFrame:
    """Exemplares por acepção: mais citados primeiro, título como desempate.

    Ordenação total, independente da ordem de leitura do CSV, para que duas
    execuções produzam arquivos idênticos.
    """
    frames = [
        df[df["acepcao"] == acepcao]
        .sort_values(["cited_by_count", "title"], ascending=[False, True])
        .head(N_EXAMPLES)
        for acepcao in ACEPCOES
    ]
    out = pd.concat(frames, ignore_index=True)
    keep = ["acepcao", "title", "publication_year", "journal", "cited_by_count", "matched_pattern"]
    return out[[c for c in keep if c in out.columns]]


def main():
    for path, hint in (
        (INPUT_LEXICAL, "python src/pipelines/08b_clean_and_enrich.py"),
        (INPUT_FINAL, "python src/pipelines/10_export_bibliometrix.py"),
    ):
        if not path.exists():
            raise SystemExit(f"Arquivo nao encontrado: {path}\nRode antes: {hint}")

    cleaned = pd.read_csv(INPUT_LEXICAL, dtype=str)
    lexical = cleaned[cleaned["ring"] == "nuclear"].copy()
    lexical["cited_by_count"] = pd.to_numeric(
        lexical["cited_by_count"], errors="coerce"
    ).fillna(0)

    final = pd.read_csv(INPUT_FINAL, dtype=str)

    print(f"Anel lexical (pre-restricao): {len(lexical):,} registros")
    print(f"Anel nuclear final:           {len(final):,} registros")

    classified = classify_frame(lexical)

    # Marca quais registros do anel lexical sobreviveram ao anel final.
    final_keys = set(_norm_title(final["title"]))
    classified["no_anel_final"] = _norm_title(classified["title"]).isin(final_keys)

    orphans = final_keys - set(_norm_title(classified["title"]))
    if orphans:
        print(
            f"\nAVISO: {len(orphans)} registro(s) do anel final nao casam no lexical. "
            "As porcentagens do anel final ficam aproximadas."
        )

    # Ordenacao estavel para tornar a saida reproduzivel entre execucoes.
    classified = classified.sort_values(
        ["acepcao", "cited_by_count", "title"], ascending=[True, False, True]
    )

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    classified[[c for c in RECORD_COLUMNS if c in classified.columns]].to_csv(
        OUTPUT_RECORDS, index=False, encoding="utf-8-sig"
    )

    summary = pd.concat(
        [
            summarize(classified, "lexical"),
            summarize(classified[classified["no_anel_final"]], "final"),
        ],
        ignore_index=True,
    )
    summary.to_csv(OUTPUT_SUMMARY, index=False, encoding="utf-8-sig")

    examples = build_examples(classified)
    examples.to_csv(OUTPUT_EXAMPLES, index=False, encoding="utf-8-sig")

    # ── Relatório ──────────────────────────────────────────────────────
    for populacao, rotulo in (
        ("lexical", "ANEL LEXICAL — registros que usam o rotulo"),
        ("final", "ANEL NUCLEAR FINAL — apos a restricao programatica"),
    ):
        block = summary[summary["populacao"] == populacao]
        print(f"\n{'='*66}")
        print(rotulo)
        print(f"{'='*66}")
        for _, row in block.iterrows():
            marker = "  " if row["acepcao"] != "total" else "→ "
            print(
                f"{marker}{row['acepcao']:<15}: {row['n']:>4,} ({row['pct']:>5.1f}%)  "
                f"mediana cit. {row['mediana_citacoes']:>5.1f}  "
                f"periodicos {row['periodicos_distintos']:>3}"
            )

    total_lex = len(classified)
    soma = int(summary[(summary["populacao"] == "lexical")
                       & (summary["acepcao"] != "total")]["n"].sum())
    assert soma == total_lex, f"Soma das acepcoes ({soma}) difere do anel lexical ({total_lex})"

    penal = classified[classified["subtipo"] == "penal"]
    print(f"\nSubtipo penal (dentro de comportamental): {len(penal)}")

    movidos = classified[~classified["no_anel_final"]]
    print(f"\nRemovidos pela restricao programatica: {len(movidos)}")
    print(pd.crosstab(classified["acepcao"], classified["no_anel_final"]).to_string())

    print("\nCampo que decidiu a classificacao:")
    field_counts = classified[classified["matched_field"] != ""]["matched_field"].value_counts()
    for field, cnt in field_counts.items():
        print(f"  {field:<12}: {cnt:>4,}")
    print(f"  {'sem padrao':<12}: {int((classified['matched_field'] == '').sum()):>4,}")

    print("\nArquivos salvos:")
    print(f"  Registros:  {OUTPUT_RECORDS}")
    print(f"  Resumo:     {OUTPUT_SUMMARY}")
    print(f"  Exemplares: {OUTPUT_EXAMPLES}")


if __name__ == "__main__":
    main()
