"""Testes unitários para src/utils/acepcoes.py.

Cobrem o que o parecer ENAJUS exige que seja auditável: precedência entre as
acepções, determinismo da regra, confinamento das regex ao campo e integridade das
contagens contra o corpus congelado.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

from utils.acepcoes import (
    ACEPCOES,
    BEHAVIORAL_PATTERNS,
    DOCTRINAL_PATTERNS,
    PENAL_PATTERNS,
    PRECEDENCE,
    PROGRAMMATIC_PATTERNS,
    classify_acepcao,
    classify_frame,
)


def row(title="", abstract="", journal=""):
    return pd.Series({"title": title, "abstract": abstract, "journal": journal})


class TestAcepcaoProgramatica:
    def test_politica_judiciaria_nacional(self):
        acepcao, _, _, field = classify_acepcao(
            row(title="A política judiciária nacional de tratamento adequado dos conflitos")
        )
        assert acepcao == "programática"
        assert field == "title"

    def test_cnj(self):
        acepcao, _, _, _ = classify_acepcao(row(title="Resolução do CNJ sobre conciliação"))
        assert acepcao == "programática"

    def test_national_judicial_policy(self):
        acepcao, _, _, _ = classify_acepcao(
            row(title="A Critical Analysis of Judicial Reforms: National Judicial Policy")
        )
        assert acepcao == "programática"


class TestAcepcaoComportamental:
    def test_policy_making(self):
        acepcao, _, _, _ = classify_acepcao(
            row(title="Judicial policy-making and Europeanization")
        )
        assert acepcao == "comportamental"

    def test_judicial_ideology(self):
        acepcao, _, _, _ = classify_acepcao(
            row(title="Ideologia Judicial e Política Judiciária: judicial ideology")
        )
        assert acepcao == "comportamental"

    def test_hifen_unicode_ainda_casa(self):
        """HYPHEN U+2010 no lugar do hífen ASCII não deve custar o registro."""
        acepcao, _, _, _ = classify_acepcao(
            row(title="Employer Liability: A Judicial Policy‐Making Study")
        )
        assert acepcao == "comportamental"

    def test_en_dash_ainda_casa(self):
        acepcao, _, _, _ = classify_acepcao(row(title="Judicial policy–making in courts"))
        assert acepcao == "comportamental"


class TestSubtipoPenal:
    def test_criminal_judicial_policy(self):
        acepcao, subtipo, _, _ = classify_acepcao(
            row(title="Criminal judicial policy of less arrest and more prosecution")
        )
        assert acepcao == "comportamental"
        assert subtipo == "penal"

    def test_penal_nao_e_acepcao_autonoma(self):
        _, subtipo, _, _ = classify_acepcao(row(title="Judicial policy-making study"))
        assert subtipo == ""

    def test_programatica_vence_penal(self):
        """Menção a matéria penal não desloca um registro programático."""
        acepcao, subtipo, _, _ = classify_acepcao(
            row(title="Política judiciária nacional e sentencing policy no CNJ")
        )
        assert acepcao == "programática"
        assert subtipo == ""


class TestAcepcaoDoutrinaria:
    def test_teoria_geral_chinesa(self):
        acepcao, _, _, _ = classify_acepcao(
            row(title="Judicial Policy: Basic Theoretical Issues Regarding Judicial Policy")
        )
        assert acepcao == "doutrinária"

    def test_tradicao_russa_pelo_periodico(self):
        acepcao, _, _, field = classify_acepcao(
            row(title="Judicial policy of Russia and Kazakhstan", journal="Gosudarstvo i pravo")
        )
        assert acepcao == "doutrinária"
        assert field == "journal"

    def test_dogmatica_islamica(self):
        acepcao, _, _, _ = classify_acepcao(
            row(title="An analysis of islamic law and judicial policy")
        )
        assert acepcao == "doutrinária"

    def test_doutrinaria_vence_comportamental(self):
        """Teoria geral é frequentemente enunciada a propósito de decisões."""
        acepcao, _, _, _ = classify_acepcao(
            row(title="Judicial interpretations and judicial decision-making")
        )
        assert acepcao == "doutrinária"


class TestIndeterminado:
    def test_sem_sinal(self):
        acepcao, subtipo, pattern, field = classify_acepcao(
            row(title="Judicial Policy Implementation in Mexico City and Merida")
        )
        assert acepcao == "indeterminado"
        assert (subtipo, pattern, field) == ("", "", "")

    def test_campos_vazios(self):
        acepcao, _, _, _ = classify_acepcao(row())
        assert acepcao == "indeterminado"

    def test_nan(self):
        acepcao, _, _, _ = classify_acepcao(
            pd.Series({"title": float("nan"), "abstract": None, "journal": float("nan")})
        )
        assert acepcao == "indeterminado"


class TestConfinamentoAoCampo:
    def test_regex_nao_atravessa_titulo_e_periodico(self):
        """`judicial policy.*administration` não pode casar via nome do periódico.

        Antes do confinamento por campo, um estudo de policy-making na "Public
        Administration Review" era lido como programático pelo periódico.
        """
        acepcao, _, _, _ = classify_acepcao(
            row(
                title="Employer Liability for Employee Sexual Harassment: A Judicial Policy-Making Study",
                journal="Public Administration Review",
            )
        )
        assert acepcao == "comportamental"

    def test_titulo_tem_prioridade_sobre_periodico(self):
        acepcao, _, _, field = classify_acepcao(
            row(title="Política judiciária nacional de conflitos", journal="Gosudarstvo i pravo")
        )
        assert acepcao == "programática"
        assert field == "title"


class TestPrecedencia:
    def test_ordem_declarada(self):
        assert [nome for nome, _ in PRECEDENCE] == [
            "programática",
            "doutrinária",
            "comportamental",
        ]

    def test_acepcoes_cobrem_precedencia_mais_residuo(self):
        assert set(ACEPCOES) == {nome for nome, _ in PRECEDENCE} | {"indeterminado"}


class TestDeterminismo:
    def test_mesma_entrada_mesma_saida(self):
        r = row(title="Judicial policy-making and Europeanization")
        assert classify_acepcao(r) == classify_acepcao(r)

    def test_classify_frame_reproduzivel(self):
        df = pd.DataFrame({
            "title": [
                "Política judiciária nacional de tratamento de conflitos",
                "Judicial policy-making in the courts",
                "Judicial Policy: Basic Theoretical Issues",
                "Neighborhood Justice as a Judicial Policy Issue",
            ],
            "abstract": [""] * 4,
            "journal": [""] * 4,
        })
        first = classify_frame(df)
        second = classify_frame(df)
        pd.testing.assert_frame_equal(first, second)
        assert list(first["acepcao"]) == [
            "programática",
            "comportamental",
            "doutrinária",
            "indeterminado",
        ]

    def test_classify_frame_nao_muta_entrada(self):
        df = pd.DataFrame({"title": ["Judicial policy-making"], "abstract": [""], "journal": [""]})
        classify_frame(df)
        assert "acepcao" not in df.columns


class TestPadroesHerdados:
    """As três listas herdadas de 08c decidem a composição do anel nuclear.

    Alterá-las invalida os números do manuscrito. Estes testes travam o tamanho
    para que qualquer mudança seja deliberada.
    """

    def test_tamanhos_congelados(self):
        assert len(PROGRAMMATIC_PATTERNS) == 24
        assert len(BEHAVIORAL_PATTERNS) == 17
        assert len(PENAL_PATTERNS) == 9

    def test_regex_russa_permanece_em_penal(self):
        """Preservada na posição original para não alterar a decisão de anel."""
        assert any("судебн" in p for p in PENAL_PATTERNS)

    def test_doutrinaria_nao_participa_da_decisao_de_anel(self):
        for pattern in DOCTRINAL_PATTERNS:
            assert pattern not in PROGRAMMATIC_PATTERNS
            assert pattern not in BEHAVIORAL_PATTERNS


CORPUS_NUCLEAR = BASE_DIR / "data" / "final" / "corpus_nuclear.csv"
CLEANED = BASE_DIR / "data" / "interim" / "04_cleaned.csv"


@pytest.mark.skipif(not CLEANED.exists(), reason="04_cleaned.csv ausente")
class TestContraCorpusCongelado:
    def test_soma_das_acepcoes_igual_ao_anel_lexical(self):
        cleaned = pd.read_csv(CLEANED, dtype=str)
        lexical = cleaned[cleaned["ring"] == "nuclear"]
        classified = classify_frame(lexical)
        assert classified["acepcao"].value_counts().sum() == len(lexical)

    def test_toda_linha_recebe_acepcao_valida(self):
        cleaned = pd.read_csv(CLEANED, dtype=str)
        lexical = cleaned[cleaned["ring"] == "nuclear"]
        classified = classify_frame(lexical)
        assert set(classified["acepcao"]) <= set(ACEPCOES)
        assert classified["acepcao"].notna().all()

    def test_as_tres_acepcoes_aparecem_no_corpus(self):
        """O achado que responde ao parecer: as três acepções existem nos dados."""
        cleaned = pd.read_csv(CLEANED, dtype=str)
        lexical = cleaned[cleaned["ring"] == "nuclear"]
        counts = classify_frame(lexical)["acepcao"].value_counts()
        for acepcao in ("programática", "comportamental", "doutrinária"):
            assert counts.get(acepcao, 0) > 0

    @pytest.mark.skipif(not CORPUS_NUCLEAR.exists(), reason="corpus_nuclear.csv ausente")
    def test_anel_final_e_subconjunto_do_lexical(self):
        cleaned = pd.read_csv(CLEANED, dtype=str)
        final = pd.read_csv(CORPUS_NUCLEAR, dtype=str)
        norm = lambda s: s.fillna("").astype(str).str.strip().str.lower()
        lexical_titles = set(norm(cleaned[cleaned["ring"] == "nuclear"]["title"]))
        assert set(norm(final["title"])) <= lexical_titles
