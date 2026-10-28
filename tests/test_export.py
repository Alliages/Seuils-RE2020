"""
Export texte et évolution des seuils aux jalons 2028 et 2031.
"""
from dataclasses import replace

from seuils_re2020 import Projet, calculer
from seuils_re2020.export import evolution, nombre_fr, texte_export
from seuils_re2020.variables import INDICATEURS

# ─── Paramètres ──────────────────────────────────────────────────────────────
PROJET = Projet(usage_id=2, zone="H1a", altitude="<400m", sref=3000, periode_pc="2025 à 2027",
                nb_logements=50)


def test_evolution_egale_au_calcul_direct():
    evol = evolution(PROJET)
    assert set(evol) == {"2028", "2031"}
    direct = calculer(replace(PROJET, periode_pc="2028 à 2030"))
    assert all(evol["2028"][cle] == direct[cle].valeur for cle, *_ in INDICATEURS)


def test_pas_d_evolution_apres_2031():
    assert evolution(replace(PROJET, periode_pc="à partir de 2031")) == {}
    assert set(evolution(replace(PROJET, periode_pc="2028 à 2030"))) == {"2031"}


def test_export_contient_seuils_puis_modulations():
    texte = texte_export(PROJET, calculer(PROJET), evolution(PROJET), departement="Paris", lien="http://x/?usage=2")
    assert texte.index("SEUILS") < texte.index("MODULATIONS")
    assert all(libelle in texte for _cle, libelle, *_ in INDICATEURS)
    assert "Paris (H1a)" in texte and "Permis de construire (PC) déposé" in texte
    assert "http://x/?usage=2" in texte


def test_nombre_fr():
    assert nombre_fr(12345.678, 1) == "12 345,7"
    assert nombre_fr("non applicable") == "non applicable"
