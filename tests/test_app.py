"""
L'interface Streamlit s'exécute sans erreur et affiche les six seuils.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

# ─── Paramètres ──────────────────────────────────────────────────────────────
APP = str(Path(__file__).resolve().parent.parent / "app.py")
NB_SEUILS = 6
DELAI_S = 30


def test_app_par_defaut():
    app = AppTest.from_file(APP, default_timeout=DELAI_S).run()
    assert not app.exception
    assert len(app.metric) == NB_SEUILS


def test_app_maison_avant_juillet_2026():
    app = AppTest.from_file(APP, default_timeout=DELAI_S).run()
    app.sidebar.selectbox[0].select(1).run()          # usage 1 : maisons
    app.sidebar.radio[0].set_value("Non").run()        # PC avant le 01/07/2026
    assert not app.exception
    assert any("non appliqué" in i.value for i in app.info)
