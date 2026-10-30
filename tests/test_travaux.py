"""
Extensions et surélévations : régime retenu selon l'article 50-3 (donnees/travaux_*.csv),
bornes comprises, et affichage de l'onglet.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from seuils_re2020 import regime_travaux

# ─── Paramètres ──────────────────────────────────────────────────────────────
APP = str(Path(__file__).resolve().parent.parent / "app.py")
DELAI_S = 30
MAISON, COLLECTIF, BUREAUX, COMMERCES, INDUSTRIE = 1, 2, 3, 17, 23

# (usage, typologie, Sref travaux, Sref existante, régime attendu) — règles validées le 30/10/2026
CAS = [
    (COLLECTIF, "surelevation", 49, 1000, "moyens"),       # moins de 50 m²
    (COLLECTIF, "surelevation", 50, 1000, "moyens"),       # 50 m² compris dans 50-150, moins de 30 %
    (COLLECTIF, "surelevation", 90, 400, "moyens"),        # 50-150 m², 22,5 %
    (COLLECTIF, "surelevation", 90, 300, "light"),         # 30 % pile : 30 % ou plus
    (COLLECTIF, "surelevation", 150, 1000, "moyens"),      # 150 m² compris
    (COLLECTIF, "surelevation", 150, 400, "light"),        # 150 m² compris, 37,5 %
    (COLLECTIF, "surelevation", 160, 1000, "light"),       # plus de 150 m², moins de 30 %
    (COLLECTIF, "surelevation", 300, 1000, "complete"),    # plus de 150 m², 30 % pile
    (BUREAUX, "extension", 90, 400, "moyens"),             # extension hors maison, moins de 30 %
    (BUREAUX, "extension", 90, 300, "complete"),           # extension hors maison, 30 % pile
    (BUREAUX, "extension", 160, 1000, "complete"),         # extension hors maison, plus de 150 m²
    (MAISON, "extension", 49, 100, "moyens"),
    (MAISON, "extension", 50, 100, "light"),               # 50 m² compris
    (MAISON, "extension", 80, 100, "light"),               # 80 m² compris
    (MAISON, "extension", 90, 1000, "complete"),           # maison de plus de 80 m², même sous 30 %
    (MAISON, "surelevation", 70, 100, "complete"),         # surélévation de maison : pas de régime allégé
    (MAISON, "surelevation", 120, 1000, "complete"),
    (COMMERCES, "extension", 40, 100, "rt2012"),           # tertiaire spécifique, moins de 50 m²
    (COMMERCES, "surelevation", 100, 1000, "rt2012"),      # tertiaire spécifique, 50-150 m², moins de 30 %
    (INDUSTRIE, "extension", 150, 1000, "rt2012"),
    (COMMERCES, "surelevation", 100, 200, "light"),        # 50 %, surélévation hors maison
    (COMMERCES, "extension", 100, 200, "complete"),
]


@pytest.mark.parametrize("usage, typologie, sref, sexistant, attendu", CAS)
def test_regime(usage, typologie, sref, sexistant, attendu):
    assert regime_travaux(usage, typologie, sref, sexistant).cle == attendu


def test_indicateurs_par_regime():
    assert regime_travaux(COLLECTIF, "surelevation", 160, 1000).indicateurs == ["bbio_max", "icconstruction_max",
                                                                               "dh_max"]
    assert regime_travaux(COLLECTIF, "surelevation", 40, 1000).indicateurs == []
    assert regime_travaux(MAISON, "extension", 60, 100).indicateurs == ["bbio_max", "icconstruction_max", "dh_max"]
    assert len(regime_travaux(BUREAUX, "extension", 200, 100).indicateurs) == 6


def test_dh_1400_surelevation_climatisee_de_maison_50_80_m2_h2d_h3():
    r = regime_travaux(MAISON, "surelevation", 70, 100, "H3", True)
    assert r.cle == "complete" and r.dh_max == 1400                                          # RE2020 complète + 1 400
    assert regime_travaux(MAISON, "surelevation", 50, 100, "H2d", True).dh_max == 1400       # bornes comprises
    assert regime_travaux(MAISON, "surelevation", 80, 100, "H2d", True).dh_max == 1400
    assert regime_travaux(MAISON, "surelevation", 81, 100, "H3", True).dh_max is None
    assert regime_travaux(MAISON, "surelevation", 70, 100, "H3", False).dh_max is None       # non climatisée
    assert regime_travaux(MAISON, "surelevation", 70, 100, "H1a", True).dh_max is None       # autre zone
    assert regime_travaux(MAISON, "extension", 70, 100, "H3", True).dh_max is None           # extension
    assert regime_travaux(COLLECTIF, "surelevation", 160, 1000, "H3", True).dh_max is None   # hors maison : calcul


def test_rt2012_sans_seuil():
    assert regime_travaux(COMMERCES, "extension", 40, 100).indicateurs == []


def test_un_seul_cas_retenu():
    r = regime_travaux(COLLECTIF, "surelevation", 160, 1000)
    assert [v for *_x, v in r.cas_testes].count(True) == 1


def test_onglet_et_lien():
    app = AppTest.from_file(APP, default_timeout=DELAI_S)
    app.query_params.update({"usage": "2", "sref": "160", "travaux": "surelevation", "sexist": "800"})
    app.run()
    assert not app.exception
    page = " ".join(m.value for m in app.markdown)
    assert "RE2020 light" in page and "20,0 %" in page
    onglet = " ".join(m.value for m in app.tabs[1].markdown)
    assert onglet.count('class="carte-seuil"') == 3            # Bbio_max, Icconstruction_max, DH_max
    assert "regime-light" in onglet                            # bandeau coloré selon le régime
    assert any("voir l'onglet" in m.value for m in app.sidebar.markdown)   # renvoi sous la Sref
    assert app.query_params["travaux"] == "surelevation" and app.query_params["sexist"] == "800"
