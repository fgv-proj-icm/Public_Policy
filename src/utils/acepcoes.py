"""
src/utils/acepcoes.py
=====================
Classificação do anel nuclear pelas três acepções de "política judiciária".

As listas de padrões nasceram em `src/pipelines/08c_reclassify_nuclear.py`, que as
usava apenas para decidir permanência no anel nuclear. Foram extraídas para cá
para que a mesma regra sirva a dois usos distintos:

  - `08c_reclassify_nuclear.py` — decide anel (nuclear vs. estendido);
  - `10b_classify_acepcoes.py`  — atribui acepção a cada registro do anel final.

Regras estáveis: PROGRAMMATIC_PATTERNS, BEHAVIORAL_PATTERNS e PENAL_PATTERNS são
reproduzidas sem alteração em relação à versão que produziu o corpus congelado.
Alterá-las muda a composição do anel nuclear e invalida os números do manuscrito.
DOCTRINAL_PATTERNS é acréscimo posterior e não participa da decisão de anel.

As três acepções seguem a tipologia adotada no artigo:

  programática   política como programa, plano, prioridade ou portfólio
                 institucional (tradição brasileira do CNJ, políticas públicas,
                 governança judicial);
  comportamental política como indução de práticas, rotinas e decisões dos atores
                 judiciais (ciência política judicial anglo-saxã). Inclui o
                 subtipo penal — política de sentenciamento —, que induz decisão
                 e não constitui acepção autônoma;
  doutrinária    política como orientação normativa e interpretativa sobre o papel
                 do Judiciário (tradição russa/pós-soviética, teoria geral chinesa,
                 dogmática institucional).

O resíduo é rotulado `indeterminado`: registros cujo título e periódico não
permitem recuperar a acepção. A indeterminação é reportada como categoria, não
suprimida — ela é evidência da instabilidade lexical que o artigo diagnostica.
"""

from __future__ import annotations

import re

import pandas as pd

# ── ACEPÇÃO PROGRAMÁTICA ──────────────────────────────────────────────────
# Idêntica a PROGRAMMATIC_SIGNALS de 08c_reclassify_nuclear.py.
PROGRAMMATIC_PATTERNS = [
    r"\bpolítica\s+judiciária\s+nacional\b",
    r"\bpolíticas\s+judiciárias\b",
    r"\bcnj\b",
    r"\bconselho\s+nacional\s+de\s+justi[cç]a\b",
    r"\bresolução\b.*\b(?:cnj|125|188|290)\b",
    r"\btratamento\s+adequado\b.*\bconflitos\b",
    r"\bgestão\s+judici[aá]l?\b",
    r"\bgovernança\s+judici[aá]l?\b",
    r"\badministração\s+(?:da\s+)?justi[cç]a\b",
    r"\bcourt\s+administration\b",
    r"\bjudicial\s+governance\b",
    r"\bjudicial\s+administration\b",
    r"\bjudicial\s+management\b",
    r"\bcourt\s+management\b",
    r"\bjudicial\s+reform\b.*\b(?:governance|management|administration|organization)\b",
    r"\bjudicial\s+council\b",
    r"\bregulatory\s+space\b",
    r"\bjudicial\s+accountability\b",
    r"\bcejusc\b",
    r"\btribunal\s+multiportas\b",
    r"\bmeios?\s+(?:alternativos?|adequados?)\s+de\s+(?:resolução|solução)\b",
    r"\bnational\s+judicial\s+policy\b",
    r"\bjudicial\s+policy\b.*\b(?:reform|governance|council|administration)\b",
    r"\bbar\s+associations?\b.*\bjudicial\s+policy\b",
]

# ── ACEPÇÃO DOUTRINÁRIA ───────────────────────────────────────────────────
# Acréscimo posterior a 08c. Não participa da decisão de anel.
DOCTRINAL_PATTERNS = [
    # Tradição russa / pós-soviética
    r"\bсудебн\w+\s+политик\w+\b",
    r"\bgosudarstvo\s+i\s+pravo\b",
    r"\brussian\s+justice\b",
    # Teoria geral chinesa e interpretação judicial
    r"\bbasic\s+theoretical\s+issues?\b",
    r"\bjudicial\s+polic(?:y|ies)\b.*\btheory\s+and\s+practice\b",
    r"\btheory\s+and\s+practice\b.*\bjudicial\s+polic(?:y|ies)\b",
    r"\bjudicial\s+interpretations?\b",
    r"\bpeople'?s\s+court\b",
    r"\bnational\s+congress\s+of\s+cpc\b",
    r"\bcountry\s+under\s+the\s+rule\s+of\s+law\b",
    # Dogmática islâmica e direito religioso doutrinário
    r"\bالسياسة\s+القضائية\b",
    r"\bislamic\s+law\b",
    r"\bimam\b",
    r"\bshari'?ah?\b",
    r"\bfiqh\b",
    # Dogmática constitucional e teoria geral
    r"\bconstitutional\s+complaints?\s+system\b",
    r"\bestado\s+constitucional\b",
    r"\bpoderes\s+judiciales\b",
    r"\btransforming\s+constitution\b",
    r"\bteoria\s+geral\b",
    r"\bdogmática\b",
    r"\bjurisprudential\s+analysis\b",
    r"\bscope\s+of\s+judicial\s+policy\b",
    r"\bjudicial\s+policy\s+perspective\b",
]

# ── ACEPÇÃO COMPORTAMENTAL ────────────────────────────────────────────────
# Idêntica a POLICYMAKING_PATTERNS de 08c_reclassify_nuclear.py.
BEHAVIORAL_PATTERNS = [
    r"\bpolicy[\s-]?making\b",
    r"\bpolicy[\s-]?maker[s]?\b",
    r"\bpolicy\s+preferences?\b",
    r"\bpolicy\s+choices?\b",
    r"\bjudicial\s+activism\b",
    r"\bjudicial\s+behavio[u]?r\b",
    r"\bjudicial\s+decision[\s-]?making\b",
    r"\bjudicial\s+attitudes?\b",
    r"\bjudicial\s+ideology\b",
    r"\bjudicial\s+voting\b",
    r"\blegislative\s+deferr?als?\b",
    r"\bseparation\s+of\s+powers?\b",
    r"\bgod\s+save\s+this\s+honora?ble\s+court\b",
    r"\breligion\s+as\s+a\s+source\b",
    r"\bsupreme\s+court\b.*\bconsensus\b",
    r"\bsupreme\s+court\b.*\bideology\b",
    r"\bcharter\s+decisions?\b",
]

# ── SUBTIPO PENAL DA ACEPÇÃO COMPORTAMENTAL ───────────────────────────────
# Idêntica a CRIMINAL_PATTERNS de 08c_reclassify_nuclear.py, inclusive a regex
# russa — preservada na posição original para não alterar a decisão de anel.
# Na classificação por acepção, DOCTRINAL_PATTERNS é avaliada antes, de modo que
# o uso doutrinário russo não é capturado aqui.
PENAL_PATTERNS = [
    r"\bcriminal\s+judicial\s+polic(?:y|ies)\b",
    r"\bcriminal\s+(?:law\s+)?polic(?:y|ies)\b.*\bjudicial\b",
    r"\bsentenc(?:ing|e)\s+polic(?:y|ies)\b",
    r"\bpenal\s+polic(?:y|ies)\b",
    r"\bleniency\s+and\s+severity\b",
    r"\bjuvenile\s+delinquency\b.*\bjudicial\b",
    r"\bcriminal\s+influence\b",
    r"\bсудебн\w+\s+политик\w+\b",  # russo: судебная политика em contexto penal
    r"\bpunishment\b.*\bjudicial\s+polic\b",
]

# Ordem de precedência da classificação por acepção.
# Programática primeiro: é a acepção que o artigo delimita e mede, e seus sinais
# (CNJ, política judiciária nacional, governança) são os mais específicos.
# Doutrinária antes de comportamental: teoria geral da função jurisdicional é
# frequentemente enunciada a propósito de decisões, e a ordem inversa capturaria
# esses casos como comportamentais.
PRECEDENCE = [
    ("programática", PROGRAMMATIC_PATTERNS),
    ("doutrinária", DOCTRINAL_PATTERNS),
    ("comportamental", BEHAVIORAL_PATTERNS),
]

ACEPCOES = ["programática", "comportamental", "doutrinária", "indeterminado"]


def _match_any(text: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _first_match(text: str, patterns: list[str]) -> str:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


# Metadados vindos das bases usam pontuação tipográfica de forma inconsistente:
# "Judicial Policy‐Making" aparece com HYPHEN (U+2010) em vez do hífen ASCII, e
# `\bpolicy[\s-]?making\b` não casaria. Normalizar antes de aplicar as regex evita
# perder registros por detalhe de codificação.
#
# A normalização vive só aqui. `08c_reclassify_nuclear.py` monta seu próprio texto
# de busca e permanece bit a bit no comportamento que produziu o corpus congelado.
_PUNCT_MAP = str.maketrans({
    "‐": "-", "‑": "-", "‒": "-", "–": "-",
    "—": "-", "―": "-", "−": "-", "﹣": "-", "－": "-",
    "‘": "'", "’": "'", "ʼ": "'", "“": '"', "”": '"',
})


def _field(row, name: str) -> str:
    value = row.get(name)
    if value is None or pd.isna(value):
        return ""
    return str(value).lower().translate(_PUNCT_MAP)


# Ordem de consulta dos campos. O título é a evidência primária; resumo e
# periódico só decidem quando o título não carrega sinal algum.
#
# A avaliação é POR CAMPO, e não sobre a concatenação dos três. Vários padrões
# herdados usam curinga (`judicial policy.*administration`), e sobre texto
# concatenado eles atravessam a fronteira entre título e periódico: um estudo de
# *policy-making* publicado na "Public Administration Review" seria lido como
# programático pelo nome do periódico. Confinar cada regex a um campo elimina
# essa contaminação.
SEARCH_FIELDS = ["title", "abstract", "journal"]


def classify_acepcao(row) -> tuple[str, str, str, str]:
    """Atribui acepção a um registro que emprega o rótulo "política judiciária".

    Retorna (acepcao, subtipo, matched_pattern, matched_field). `subtipo` é
    "penal" quando o registro é comportamental por política de sentenciamento, e
    "" nos demais casos. Registros sem nenhum sinal recebem "indeterminado".

    A regra é determinística: mesma entrada, mesma saída, sem julgamento de
    codificador e sem estado entre chamadas.
    """
    for field in SEARCH_FIELDS:
        text = _field(row, field)
        if not text:
            continue

        for acepcao, patterns in PRECEDENCE:
            if _match_any(text, patterns):
                return acepcao, "", _first_match(text, patterns), field

        # Política de sentenciamento: subtipo comportamental, avaliado depois das
        # três acepções para não sequestrar registros programáticos ou
        # doutrinários que apenas mencionem matéria penal.
        if _match_any(text, PENAL_PATTERNS):
            return "comportamental", "penal", _first_match(text, PENAL_PATTERNS), field

    return "indeterminado", "", "", ""


def classify_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica `classify_acepcao` linha a linha e devolve cópia com 4 colunas novas."""
    out = df.copy()
    results = out.apply(classify_acepcao, axis=1, result_type="expand")
    out["acepcao"] = results[0]
    out["subtipo"] = results[1]
    out["matched_pattern"] = results[2]
    out["matched_field"] = results[3]
    return out
