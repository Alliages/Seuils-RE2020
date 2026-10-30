"""
Lecture des paramètres d'URL : valeurs absurdes ou hors bornes ignorées, valeurs saines retenues.
"""
import pytest

from interface import lien

# ─── Paramètres ──────────────────────────────────────────────────────────────
ABSURDES = ["inf", "-inf", "nan", "1e999", "1e308", "-5"]


@pytest.mark.parametrize("valeur", ABSURDES)
def test_sref_absurde_ignoree(valeur):
    assert "sref" not in lien.lire({"sref": valeur})


def test_sref_saine_retenue():
    assert lien.lire({"sref": "3000"}) == {"sref": 3000.0}


def test_nb_logements_entier_obligatoire():
    assert "nb_logements" not in lien.lire({"nl": "2.5"})
    assert lien.lire({"nl": "50.0"})["nb_logements"] == 50
