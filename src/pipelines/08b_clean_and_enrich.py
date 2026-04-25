"""
08b_clean_and_enrich.py
=======================
Limpeza pós-triagem e enriquecimento de metadados.

Três operações:
  1. Exclusão estendida por journal (periódicos fora do escopo)
  2. Enriquecimento de metadados faltantes (language, journal)
     cruzando com registros de outras bases via DOI
  3. Geração de amostra aleatória do anel nuclear para inspeção manual

Entrada : data/interim/03_screened.csv
          data/interim/03_excluded.csv
          data/interim/01_merged_all_sources.csv   (para enriquecimento)
Saída   : data/interim/04_cleaned.csv              (corpus limpo)
          data/interim/04_excluded_update.csv       (excluídos adicionais)
          data/interim/04_nuclear_sample.csv        (amostra para inspeção)
          data/interim/04_clean_report.txt          (relatório)

Uso:
    python src/pipelines/08b_clean_and_enrich.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_SCREENED = INTERIM_DIR / "03_screened.csv"
INPUT_EXCLUDED = INTERIM_DIR / "03_excluded.csv"
INPUT_MERGED = INTERIM_DIR / "01_merged_all_sources.csv"

OUTPUT_CLEANED = INTERIM_DIR / "04_cleaned.csv"
OUTPUT_EXCLUDED_NEW = INTERIM_DIR / "04_excluded_update.csv"
OUTPUT_SAMPLE = INTERIM_DIR / "04_nuclear_sample.csv"
OUTPUT_REPORT = INTERIM_DIR / "04_clean_report.txt"

# ── PERIÓDICOS FORA DO ESCOPO ──────────────────────────────────────────────
# Revistas que não pertencem ao campo de políticas judiciárias / governança judicial.
# Adicione outros conforme inspeção manual revelar.

BAD_JOURNALS = [
    # Ciências naturais / biológicas
    "shilap",
    "lepidopter",
    "entomol",
    "zoolog",
    "botan",
    "ecolog",
    "biolog",
    "biochem",
    "veterinar",
    "parasitol",
    # Medicina / saúde
    "nursing",
    "medical",
    "medicine",
    "health",
    "clinical",
    "surgical",
    "epidemiol",
    "oncol",
    "pharmac",
    "dental",
    "pediatr",
    # Engenharia / ciências exatas
    "engineering",
    "polymer",
    "chemistry",
    "physics",
    "mathemat",
    "material science",
    # Agricultura
    "agric",
    "agron",
    "food science",
    "animal science",
    # Outros fora de escopo
    "library science",
    "information science",
]

# ── PERIÓDICOS AMBÍGUOS (manter mas sinalizar) ────────────────────────────
# Publicam sobre judicial review constitucionalista, não sobre governança.
AMBIGUOUS_JOURNALS = [
    "judicial review",  # periódico britânico — predominantemente constitucionalista
]

# ── TÍTULOS FORA DO ESCOPO (complemento) ───────────────────────────────────
BAD_TITLE_PATTERNS = [
    "lepidoptera",
    "butterfly",
    "moth species",
    "insect",
    "larvae",
    "genus ",
    "new species",
    "taxonom",
]


def norm(text) -> str:
    if pd.isna(text):
        return ""
    return str(text).strip().lower()


def is_bad_journal(journal_norm: str) -> bool:
    return any(bad in journal_norm for bad in BAD_JOURNALS)


def is_ambiguous_journal(journal_norm: str) -> bool:
    return any(amb in journal_norm for amb in AMBIGUOUS_JOURNALS)


def is_bad_title(title_norm: str) -> bool:
    return any(bad in title_norm for bad in BAD_TITLE_PATTERNS)


def enrich_metadata(df: pd.DataFrame, df_all: pd.DataFrame) -> pd.DataFrame:
    """
    Para registros com metadados faltantes (language, journal),
    busca valores nas outras bases via DOI.
    """
    df = df.copy()
    df["doi_norm"] = df["doi"].fillna("").astype(str).str.strip().str.lower()

    # Construir lookup de metadados a partir do merged completo
    df_all = df_all.copy()
    df_all["doi_norm"] = df_all["doi"].fillna("").astype(str).str.strip().str.lower()

    # Lookup de language por DOI (priorizar registros que têm valor)
    lang_lookup = (
        df_all[
            (df_all["doi_norm"] != "")
            & (df_all["language"].fillna("").astype(str).str.strip() != "")
            & (df_all["language"].fillna("").astype(str).str.strip().str.lower() != "nan")
        ]
        .drop_duplicates(subset=["doi_norm"], keep="first")
        .set_index("doi_norm")["language"]
        .to_dict()
    )

    # Lookup de journal por DOI
    journal_lookup = (
        df_all[
            (df_all["doi_norm"] != "")
            & (df_all["journal"].fillna("").astype(str).str.strip() != "")
            & (df_all["journal"].fillna("").astype(str).str.strip().str.lower() != "nan")
            & (df_all["journal"].fillna("").astype(str).str.strip().str.lower() != "n/d")
        ]
        .drop_duplicates(subset=["doi_norm"], keep="first")
        .set_index("doi_norm")["journal"]
        .to_dict()
    )

    # Enriquecer language
    missing_lang = (
        (df["language"].fillna("").astype(str).str.strip() == "")
        | (df["language"].fillna("").astype(str).str.strip().str.lower() == "nan")
    )
    enriched_lang = 0
    for idx in df[missing_lang & (df["doi_norm"] != "")].index:
        doi = df.at[idx, "doi_norm"]
        if doi in lang_lookup:
            df.at[idx, "language"] = lang_lookup[doi]
            enriched_lang += 1

    # Enriquecer journal
    missing_journal = (
        (df["journal"].fillna("").astype(str).str.strip() == "")
        | (df["journal"].fillna("").astype(str).str.strip().str.lower() == "nan")
        | (df["journal"].fillna("").astype(str).str.strip().str.lower() == "n/d")
    )
    enriched_journal = 0
    for idx in df[missing_journal & (df["doi_norm"] != "")].index:
        doi = df.at[idx, "doi_norm"]
        if doi in journal_lookup:
            df.at[idx, "journal"] = journal_lookup[doi]
            enriched_journal += 1

    print(f"  Enriquecimento — language: {enriched_lang} registros")
    print(f"  Enriquecimento — journal:  {enriched_journal} registros")

    return df


def main():
    df = pd.read_csv(INPUT_SCREENED, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)
    df["journal_norm"] = df["journal"].fillna("").astype(str).str.strip().str.lower()
    df["title_norm"] = df["title"].fillna("").astype(str).str.strip().str.lower()

    # Carregar excluídos anteriores
    if INPUT_EXCLUDED.exists():
        df_prev_excluded = pd.read_csv(INPUT_EXCLUDED, dtype=str)
    else:
        df_prev_excluded = pd.DataFrame()

    total_input = len(df)
    report_lines = []
    report_lines.append(f"Entrada: {total_input:,} registros (pós-triagem 08)")

    # ── 1. EXCLUSÃO POR JOURNAL ────────────────────────────────────────
    mask_bad_journal = df["journal_norm"].apply(is_bad_journal)
    mask_bad_title = df["title_norm"].apply(is_bad_title)
    mask_exclude = mask_bad_journal | mask_bad_title

    excluded_new = df[mask_exclude].copy()
    excluded_new["exclusion_reason"] = "periódico_ou_título_fora_escopo"

    # Detalhar o que foi removido
    if len(excluded_new) > 0:
        print(f"\n  Excluídos por periódico/título fora de escopo: {len(excluded_new)}")
        journal_excl = excluded_new["journal"].fillna("N/D").value_counts().head(10)
        for j, cnt in journal_excl.items():
            print(f"    {j[:50]:50s}: {cnt}")
            report_lines.append(f"  Excluído — {j}: {cnt}")

    df_clean = df[~mask_exclude].copy()

    # ── 2. SINALIZAR PERIÓDICOS AMBÍGUOS ───────────────────────────────
    df_clean["flag_ambiguous_journal"] = df_clean["journal_norm"].apply(is_ambiguous_journal)
    n_ambiguous = df_clean["flag_ambiguous_journal"].sum()
    print(f"  Sinalizados como ambíguos (não excluídos): {n_ambiguous}")
    report_lines.append(f"Sinalizados como ambíguos: {n_ambiguous}")

    # ── 3. ENRIQUECER METADADOS ────────────────────────────────────────
    if INPUT_MERGED.exists():
        df_all = pd.read_csv(INPUT_MERGED, dtype=str)
        df_clean = enrich_metadata(df_clean, df_all)
    else:
        print("  AVISO: 01_merged_all_sources.csv não encontrado — sem enriquecimento")

    # ── 4. RECALCULAR ESTATÍSTICAS PÓS-LIMPEZA ────────────────────────
    n_nuclear = len(df_clean[df_clean["ring"] == "nuclear"])
    n_extended = len(df_clean[df_clean["ring"] == "extended"])
    n_total = len(df_clean)

    # Metadados faltantes após enriquecimento
    n_no_lang = (
        (df_clean["language"].fillna("").astype(str).str.strip() == "")
        | (df_clean["language"].fillna("").astype(str).str.strip().str.lower() == "nan")
    ).sum()
    n_no_journal = (
        (df_clean["journal"].fillna("").astype(str).str.strip() == "")
        | (df_clean["journal"].fillna("").astype(str).str.strip().str.lower() == "nan")
        | (df_clean["journal"].fillna("").astype(str).str.strip().str.lower() == "n/d")
    ).sum()

    # ── 5. GERAR AMOSTRA DO NUCLEAR ───────────────────────────────────
    nuclear_df = df_clean[df_clean["ring"] == "nuclear"].copy()
    sample_size = min(30, len(nuclear_df))
    nuclear_sample = nuclear_df.sample(n=sample_size, random_state=42)
    nuclear_sample = nuclear_sample[
        ["title", "doi", "publication_year", "journal", "language", "cited_by_count", "source", "query_term"]
    ]

    # ── 6. SALVAR ──────────────────────────────────────────────────────
    df_clean = df_clean.sort_values("cited_by_count", ascending=False)
    df_clean.to_csv(OUTPUT_CLEANED, index=False, encoding="utf-8-sig")

    # Consolidar todos os excluídos (anteriores + novos)
    all_excluded = pd.concat([df_prev_excluded, excluded_new], ignore_index=True)
    all_excluded.to_csv(OUTPUT_EXCLUDED_NEW, index=False, encoding="utf-8-sig")

    nuclear_sample.to_csv(OUTPUT_SAMPLE, index=False, encoding="utf-8-sig")

    # ── 7. RELATÓRIO ───────────────────────────────────────────────────
    report_lines.insert(0, "=" * 60)
    report_lines.insert(1, "RELATÓRIO DE LIMPEZA PÓS-TRIAGEM (08b)")
    report_lines.insert(2, "=" * 60)
    report_lines.append("")
    report_lines.append(f"Excluídos nesta etapa: {len(excluded_new):,}")
    report_lines.append(f"Total excluídos acumulado: {len(all_excluded):,}")
    report_lines.append(f"Corpus limpo: {n_total:,}")
    report_lines.append(f"  Nuclear: {n_nuclear:,}")
    report_lines.append(f"  Estendido: {n_extended:,}")
    report_lines.append(f"Metadados faltantes após enriquecimento:")
    report_lines.append(f"  Sem language: {n_no_lang:,}")
    report_lines.append(f"  Sem journal:  {n_no_journal:,}")

    report_text = "\n".join(report_lines)
    OUTPUT_REPORT.write_text(report_text, encoding="utf-8")

    print(f"\n{'='*60}")
    print("RESULTADO DA LIMPEZA")
    print(f"{'='*60}")
    print(f"Entrada:                        {total_input:>7,}")
    print(f"Excluídos nesta etapa:          {len(excluded_new):>7,}")
    print(f"Corpus limpo:                   {n_total:>7,}")
    print(f"  Anel nuclear:                 {n_nuclear:>7,}")
    print(f"  Anel estendido:               {n_extended:>7,}")
    print(f"Metadados após enriquecimento:")
    print(f"  Ainda sem language:           {n_no_lang:>7,}")
    print(f"  Ainda sem journal:            {n_no_journal:>7,}")
    print(f"\nAmostra nuclear ({sample_size} registros) para inspeção manual:")
    print(nuclear_sample[["title", "journal", "publication_year"]].to_string(index=False))
    print(f"\nArquivos salvos:")
    print(f"  Corpus limpo:    {OUTPUT_CLEANED}")
    print(f"  Excluídos:       {OUTPUT_EXCLUDED_NEW}")
    print(f"  Amostra nuclear: {OUTPUT_SAMPLE}")
    print(f"  Relatório:       {OUTPUT_REPORT}")
    print(f"\n>>> AÇÃO NECESSÁRIA: abra {OUTPUT_SAMPLE.name}")
    print(f"    e marque os registros que NÃO são sobre política judiciária")
    print(f"    no sentido programático (governança, gestão, CNJ).")
    print(f"    Isso valida o critério de inclusão do anel nuclear.")


if __name__ == "__main__":
    main()
