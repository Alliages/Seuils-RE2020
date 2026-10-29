"""
Interface Streamlit : affichage, champs selon l'usage, sauvegarde et relecture par lien.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from interface import lien

# ─── Paramètres ──────────────────────────────────────────────────────────────
APP = str(Path(__file__).resolve().parent.parent / "app.py")
NB_SEUILS = 6
DELAI_S = 30


def lancer(params=None):
    app = AppTest.from_file(APP, default_timeout=DELAI_S)
    for nom, valeur in (params or {}).items():
        app.query_params[nom] = valeur
    return app.run()


def textes(app):
    return " ".join(m.value for m in app.markdown)


def test_affichage_par_defaut():
    app = lancer()
    assert not app.exception
    assert textes(app).count('class="carte-seuil"') == NB_SEUILS
    assert "Paris (H1a)" in textes(app)
    assert "déposé : 2025 à 2027, à partir du 1er juillet 2026" in textes(app)
    assert "référence" not in " ".join(c.value for c in app.caption)


def test_lien_relu_au_demarrage():
    app = lancer({"usage": "1", "dep": "Var", "pc": "2025 à 2027", "juillet": "0", "sref": "150"})
    assert not app.exception
    assert app.session_state["usage_id"] == 1 and app.session_state["departement"] == "Var"
    assert "83 – Var (H3)" in textes(app) and "avant le 1er juillet 2026" in textes(app)
    assert app.query_params["usage"] == "1" and app.query_params["v"]


def test_lien_invalide_ignore():
    app = lancer({"usage": "99", "sref": "abc", "cat": "7"})
    assert not app.exception
    assert app.session_state["usage_id"] == lien.DEFAUTS["usage_id"]


def test_categorie_3_proposee_seulement_si_possible():
    app = lancer({"usage": "2"})                       # logements collectifs : pas de catégorie 3
    choix = next(s for s in app.sidebar.selectbox if s.label.startswith("Catégorie"))
    assert choix.options == ["Catégorie 1", "Catégorie 2"]


def test_aller_retour_du_lien():
    valeurs = {**lien.DEFAUTS, "usage_id": 3, "sref": 1234.5, "igh": True, "categorie": 3, "nb_logements": 12}
    assert lien.lire(lien.parametres(valeurs)) == {k: v for k, v in valeurs.items() if v != lien.DEFAUTS[k]}


def test_nombre_de_logements_entier():
    app = lancer({"nl": "40.0"})
    assert app.session_state["nb_logements"] == 40 and isinstance(app.session_state["nb_logements"], int)
    assert lancer({"nl": "40.5"}).session_state["nb_logements"] == lien.DEFAUTS["nb_logements"]


def test_agrement_en_pourcentage_de_la_shab():
    app = lancer({"agr": "450", "sref": "3000"})
    assert any("15,0 % de la SHAB" in c.value for c in app.sidebar.caption)
