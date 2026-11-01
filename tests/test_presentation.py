"""
Export texte et évolution des seuils aux jalons 2028 et 2031.
"""
from dataclasses import replace

from seuils_re2020 import Projet, calculer, donnees
from seuils_re2020.presentation import (details, evolution, formules, libelle_departement, nombre_fr,
                                  texte_export)
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
    assert texte.index("SEUILS") < texte.index("FORMULES ET MODULATIONS")
    assert all(libelle in texte for _cle, libelle, *_ in INDICATEURS)
    assert "Paris (H1a)" in texte and "Permis de construire (PC) déposé" in texte
    assert "http://x/?usage=2" in texte
    assert "Extension et surélévation : non exportées" in texte


def test_nombre_fr():
    assert nombre_fr(12345.678, 1) == "12 345,7"
    assert nombre_fr("non applicable") == "non applicable"


def test_formules_symbolique_et_chiffree():
    r = calculer(PROJET)["bbio_max"]
    symbolique, chiffres = formules("bbio_max", "Bbio_max", r)
    assert symbolique == "Bbio_max = Bbio_maxmoyen × (1 + Mbgéo + Mbcombles + Mbsurf_moy + Mbsurf_tot + Mbbruit + MbHSP)"
    assert chiffres.startswith("Bbio_max = 65,00 × (1 + 0,1 + 0") and "= 71,50" in chiffres
    assert formules("dh_max", "DH_max", calculer(PROJET)["dh_max"])[0] == "DH_max = DH_maxcat"


def test_details_toutes_les_saisies_utiles():
    p = replace(PROJET, sagrement=400, sref=3130)
    texte = details(p)
    assert "agrément 400 m² (12,8 % de la SHAB)" in texte and "HSP" in texte and "lot 13" in texte
    assert "combles" not in texte                      # sans objet pour un logement collectif


def test_departements_par_numero():
    noms = list(donnees.departements())
    assert noms[0] == "Ain" and noms.index("Corse-du-Sud") < noms.index("Côte-d'Or")
    assert libelle_departement("Paris") == "75 – Paris (H1a)"
