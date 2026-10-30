"""
Chaque nom utilisé dans une condition ou une formule de donnees/ doit exister :
une faute de frappe ferait planter l'application (NameError) au premier calcul concerné.
"""
import ast

import pytest

from seuils_re2020 import Projet, donnees
from seuils_re2020.regles import variables
from seuils_re2020.travaux import variables_travaux
from seuils_re2020.variables import USAGE_MAISON

# ─── Paramètres ──────────────────────────────────────────────────────────────
# Variables ajoutées par le calcul elles-mêmes (voir calculs.py et travaux.py)
VARIABLES_CALCUL = {"bbiomaxmoyen", "cepnrmaxmoyen", "icconstructionmaxmoyen", "dh_max", "regime"}
FONCTIONS = {"min", "max"}
PROJET_TYPE = Projet(usage_id=USAGE_MAISON, zone="H1a", altitude="<400m", sref=100,
                     periode_pc="2025 à 2027")
CONNUS = (set(variables(PROJET_TYPE)) | set(variables_travaux(USAGE_MAISON, "extension", 100, 100))
          | VARIABLES_CALCUL | FONCTIONS)


def _expressions():
    """(fichier, expression) pour toutes les conditions et formules des tables de règles."""
    sortie = []
    for nom in ("regles", "travaux_cas", "travaux_dh", "surfaces_minimales"):
        for ligne in donnees.table(nom):
            for champ in ("condition", "formule"):
                texte = ligne.get(champ, "")
                if texte and texte != "defaut":
                    sortie.append((nom, texte))
    return sortie


def _noms(expression):
    return {n.id for n in ast.walk(ast.parse(expression, mode="eval")) if isinstance(n, ast.Name)}


@pytest.mark.parametrize("nom,expression", _expressions())
def test_noms_connus(nom, expression):
    inconnus = _noms(expression) - CONNUS
    assert not inconnus, f"{nom} : {expression} utilise {sorted(inconnus)}"
