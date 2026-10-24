"""
Non-régression : le moteur doit redonner les résultats du classeur Excel v2.2
sur tous les cas de tests/cas_reference.csv (générés par outils/creer_cas_reference.py).
"""
import csv
from pathlib import Path

import pytest

from seuils_re2020 import Projet, calculer, decret_2026_applicable
from seuils_re2020.expressions import evaluer
from seuils_re2020.variables import TOLERANCE_TESTS

# ─── Paramètres ──────────────────────────────────────────────────────────────
FICHIER_CAS = Path(__file__).parent / "cas_reference.csv"
INDICATEURS = ["bbio_max", "cepnr_max", "cep_max", "icenergie_max", "icconstruction_max",
               "dh_max", "dh_effinergie"]
TEXTES_NON_APPLICABLE = {"erreur", "non applicable"}
NB_ECARTS_AFFICHES = 25


def lire_cas():
    with open(FICHIER_CAS, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def projet_depuis(l):
    entier = lambda k: bool(int(l[k]))
    return Projet(
        usage_id=int(l["usage_id"]), zone=l["zone"], altitude=l["altitude"], sref=float(l["sref"]),
        periode_pc=l["periode_pc"], pc_apres_juillet_2026=entier("pc_apres_juillet_2026"),
        nb_logements=float(l["nb_logements"]), scombles=float(l["scombles"]),
        exposition_bruit=l["exposition_bruit"], categorie=int(l["categorie"]),
        climatise=entier("climatise"), rcu=entier("rcu"), rcu_classe=entier("rcu_classe"), igh=entier("igh"),
        sagrement=float(l["sagrement"]), hsp=float(l["hsp"]), iclot1=float(l["iclot1"]),
        iclot2=float(l["iclot2"]), iclot13=float(l["iclot13"]), icded=float(l["icded"]),
        classe_inertie=l["classe_inertie"])


def identiques(attendu, obtenu):
    """Même nombre (à la tolérance près), même texte, ou « non applicable » des deux côtés."""
    try:
        a = float(attendu)
    except ValueError:
        texte = str(obtenu).lower()
        if attendu.lower() in TEXTES_NON_APPLICABLE:
            return texte in TEXTES_NON_APPLICABLE
        return texte == attendu.lower()
    return isinstance(obtenu, (int, float)) and abs(a - obtenu) <= TOLERANCE_TESTS * max(1.0, abs(a))


def test_tous_les_cas_du_classeur():
    ecarts = []
    cas = lire_cas()
    for n, l in enumerate(cas, start=2):
        resultats = calculer(projet_depuis(l))
        for ind in INDICATEURS:
            if not identiques(l[ind], resultats[ind].valeur):
                ecarts.append(f"ligne {n} [{l['groupe']}] usage {l['usage_id']} {ind} : "
                              f"Excel {l[ind]} / moteur {resultats[ind].valeur}")
    assert not ecarts, f"{len(ecarts)} écarts sur {len(cas)} cas :\n" + "\n".join(ecarts[:NB_ECARTS_AFFICHES])


@pytest.mark.parametrize("periode, apres_juillet, attendu", [
    ("2022 à 2024", True, False), ("2025 à 2027", False, False), ("2025 à 2027", True, True),
    ("2028 à 2030", False, True), ("à partir de 2031", False, True)])
def test_date_du_decret_2026(periode, apres_juillet, attendu):
    p = Projet(usage_id=2, zone="H1a", altitude="<400m", sref=1000, periode_pc=periode,
               pc_apres_juillet_2026=apres_juillet)
    assert decret_2026_applicable(p) is attendu


def test_les_expressions_refusent_le_code_arbitraire():
    with pytest.raises(ValueError):
        evaluer("__import__('os').system('echo')", {})
