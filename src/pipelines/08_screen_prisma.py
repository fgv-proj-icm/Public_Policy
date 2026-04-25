"""
08_screen_prisma.py
===================
PRISMA — Etapa "Screening" + "Eligibility"

Classifica cada registro em:
  - NUCLEAR   : expressão exata "judicial policy" / "política judiciária" etc.
                no título OU no abstract
  - EXTENDED  : trata do sistema de justiça como objeto de gestão/governança/
                política pública (termos cognatos)
  - EXCLUDED  : fora do escopo, com motivo registrado

Entrada : data/interim/02_deduplicated.csv
Saída   : data/interim/03_screened.csv          (incluídos, com coluna 'ring')
          data/interim/03_excluded.csv           (excluídos, com coluna 'exclusion_reason')
          data/interim/03_prisma_counts.csv      (contagens para diagrama)

Uso:
    python src/pipelines/08_screen_prisma.py
"""

from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"

INPUT_FILE = INTERIM_DIR / "02_deduplicated.csv"
OUTPUT_INCLUDED = INTERIM_DIR / "03_screened.csv"
OUTPUT_EXCLUDED = INTERIM_DIR / "03_excluded.csv"
OUTPUT_COUNTS = INTERIM_DIR / "03_prisma_counts.csv"

# ── CRITÉRIOS ───────────────────────────────────────────────────────────────

# Anel nuclear: expressões exatas que definem o campo
NUCLEAR_PATTERNS = [
    r"\bjudicial\s+polic(?:y|ies)\b",
    r"\bjudiciary\s+polic(?:y|ies)\b",
    r"\bpol[ií]tica[s]?\s+judici[aá]ri[ao]s?\b",
    r"\bpol[ií]tica[s]?\s+judicial(?:es)?\b",
]

# Anel estendido: termos cognatos — sistema de justiça como objeto de gestão
EXTENDED_ANCHORS = [
    r"\bjudicial\s+governance\b",
    r"\bjudicial\s+administration\b",
    r"\bcourt\s+administration\b",
    r"\bcourt\s+governance\b",
    r"\bcourt\s+management\b",
    r"\bjudicial\s+management\b",
    r"\bjudicial\s+reform\b",
    r"\breforma\s+(?:do\s+)?judici[aá]ri[ao]\b",
    r"\breforma\s+judicial\b",
    r"\bgovernança\s+judicial\b",
    r"\badministra[cç][aã]o\s+(?:da\s+)?justi[cç]a\b",
    r"\badministra[cç][aã]o\s+judici[aá]ri[ao]\b",
    r"\bgest[aã]o\s+(?:de\s+)?tribunais\b",
    r"\bgest[aã]o\s+judicial\b",
    r"\bconselho\s+nacional\s+de\s+justi[cç]a\b",
]

# Exclusão: sinais de que o artigo trata de outro tema
EXCLUDE_CONSTITUTIONALIST = [
    # judicial review no sentido de controle de constitucionalidade
    r"\bjudicial\s+review\b.*\b(?:constitutionality|unconstitutional|statute|legislation)\b",
    r"\bconstitutional\s+adjudication\b",
]

EXCLUDE_JUDICIALISATION = [
    r"\bjudiciali[sz]a(?:tion|ção)\b",
    r"\bjudicializ\b",
]

EXCLUDE_OFF_TOPIC_TITLE = [
    r"\bnursing\b",
    r"\bchemistry\b",
    r"\blepidopter\b",
    r"\bpolymer\b",
    r"\bsex\s+workers?\b",
    r"\bagricultural\b",
    r"\bwto\b",
    r"\bmedieval\b",
    r"\bpoverty\s+reduction\b",
]

# Metadados mínimos obrigatórios
MIN_TITLE_LENGTH = 10


def _match_any(text: str, patterns: list[str]) -> bool:
    """Retorna True se qualquer padrão regex casar no texto."""
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def classify_record(row) -> tuple[str, str]:
    """
    Retorna (ring, exclusion_reason).
    ring = 'nuclear' | 'extended' | 'excluded'
    exclusion_reason = '' se incluído, ou motivo se excluído.
    """
    title = str(row.get("title_norm", ""))
    abstract = str(row.get("abstract", "")).lower() if pd.notna(row.get("abstract")) else ""
    journal = str(row.get("journal_norm", ""))
    search_text = f"{title} {abstract}"

    # ── Pré-filtro: metadados mínimos ──────────────────────────────────
    if len(title) < MIN_TITLE_LENGTH:
        return "excluded", "metadados_insuficientes"

    # ── Exclusão por tema fora do escopo ───────────────────────────────
    if _match_any(title, EXCLUDE_OFF_TOPIC_TITLE):
        return "excluded", "tema_fora_escopo"

    # ── Anel nuclear ───────────────────────────────────────────────────
    if _match_any(search_text, NUCLEAR_PATTERNS):
        return "nuclear", ""

    # ── Verificação de judicial review constitucionalista ──────────────
    # Só exclui se não tiver âncoras de gestão/governança
    if _match_any(search_text, EXCLUDE_CONSTITUTIONALIST):
        return "excluded", "judicial_review_constitucionalista"

    # ── Verificação de judicialização ──────────────────────────────────
    if _match_any(search_text, EXCLUDE_JUDICIALISATION):
        # Judicialização pode ser relevante se tratar de política judiciária
        # como resposta institucional — mas por default exclui
        return "excluded", "judicializacao_politicas"

    # ── Anel estendido ─────────────────────────────────────────────────
    if _match_any(search_text, EXTENDED_ANCHORS):
        return "extended", ""

    # ── Não se encaixa em nenhum critério ──────────────────────────────
    # Verificar se ao menos menciona sistema de justiça no título
    justice_anchors = r"\b(?:judicial|judiciary|court[s]?|tribunal|judici[aá]ri[ao]|justi[cç]a)\b"
    if re.search(justice_anchors, title, re.IGNORECASE):
        return "extended", ""

    return "excluded", "sem_relacao_sistema_justica"


def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)

    total_input = len(df)
    print(f"Registros de entrada (pós-deduplicação): {total_input:,}")

    # ── Classificar cada registro ──────────────────────────────────────
    results = df.apply(classify_record, axis=1, result_type="expand")
    df["ring"] = results[0]
    df["exclusion_reason"] = results[1]

    # ── Separar incluídos e excluídos ──────────────────────────────────
    included = df[df["ring"].isin(["nuclear", "extended"])].copy()
    excluded = df[df["ring"] == "excluded"].copy()

    included = included.sort_values("cited_by_count", ascending=False)
    excluded = excluded.sort_values("cited_by_count", ascending=False)

    # ── Salvar ─────────────────────────────────────────────────────────
    included.to_csv(OUTPUT_INCLUDED, index=False, encoding="utf-8-sig")
    excluded.to_csv(OUTPUT_EXCLUDED, index=False, encoding="utf-8-sig")

    # ── Contagens PRISMA ───────────────────────────────────────────────
    n_nuclear = len(included[included["ring"] == "nuclear"])
    n_extended = len(included[included["ring"] == "extended"])
    n_excluded = len(excluded)

    exclusion_breakdown = excluded["exclusion_reason"].value_counts()

    counts = {
        "etapa": [
            "01_identificados_bruto",
            "02_apos_deduplicacao",
            "03_incluidos_total",
            "03a_anel_nuclear",
            "03b_anel_estendido",
            "03_excluidos_total",
        ],
        "n": [
            "ver_script_07",
            total_input,
            n_nuclear + n_extended,
            n_nuclear,
            n_extended,
            n_excluded,
        ],
    }

    # Adicionar breakdown de exclusões
    for reason, count in exclusion_breakdown.items():
        counts["etapa"].append(f"  excl_{reason}")
        counts["n"].append(count)

    df_counts = pd.DataFrame(counts)
    df_counts.to_csv(OUTPUT_COUNTS, index=False, encoding="utf-8-sig")

    # ── Relatório ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRISMA — SCREENING & ELIGIBILITY")
    print(f"{'='*60}")
    print(f"Entrada (pós-deduplicação):     {total_input:>7,}")
    print(f"Incluídos — anel nuclear:       {n_nuclear:>7,}")
    print(f"Incluídos — anel estendido:     {n_extended:>7,}")
    print(f"Total incluídos:                {n_nuclear + n_extended:>7,}")
    print(f"Total excluídos:                {n_excluded:>7,}")
    print(f"\nMotivos de exclusão:")
    print(exclusion_breakdown.to_string())
    print(f"\nSalvo em:")
    print(f"  Incluídos:  {OUTPUT_INCLUDED}")
    print(f"  Excluídos:  {OUTPUT_EXCLUDED}")
    print(f"  Contagens:  {OUTPUT_COUNTS}")


if __name__ == "__main__":
    main()
