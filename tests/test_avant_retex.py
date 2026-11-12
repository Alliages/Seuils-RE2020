"""
PC 2022-2024 : annexe R.172-4 avant le décret n° 2024-1258 (FAQ RE2020 n° 212), et usages soumis
à la RE2020 depuis le 1er mai 2026 (décret n° 2026-16). Valeurs attendues calculées à la main
d'après les PDF de l'annexe (versions avant RETEX et post-RETEX du site RT-RE).
"""
from dataclasses import replace

import pytest

from seuils_re2020 import Projet, calculer, hors_champ
from seuils_re2020.presentation import formules, libelle_depot, texte_applicable

# ─── Paramètres ──────────────────────────────────────────────────────────────
TOLERANCE = 1e-9
# Logements collectifs, Sref 1 000 m², 50 logements (Smoylgt 20 m²), zone H1a < 400 m, lots à 0
LC_2022 = Projet(usage_id=2, zone="H1a", altitude="<400m", sref=1000, periode_pc="2022 à 2024", nb_logements=50)
LC_2025 = replace(LC_2022, periode_pc="2025 à 2027", pc_apres_juillet_2026=False)
MAISON_2022 = Projet(usage_id=1, zone="H1a", altitude="<400m", sref=120, periode_pc="2022 à 2024", nb_logements=1)
BUREAUX_2022 = Projet(usage_id=3, zone="H1a", altitude="<400m", sref=2000, periode_pc="2022 à 2024", iclot13=50)
HOTEL = Projet(usage_id=8, zone="H1a", altitude="<400m", sref=2000, periode_pc="2025 à 2027",
               pc_apres_juillet_2026=False)
COEFS_2026_200 = {"MbHSP", "McHSP", "MiHSP", "Miagrément_ext", "Miclim_RCU"}


def proche(a, b):
    return abs(a - b) <= TOLERANCE * max(1.0, abs(b))


# ─── Icconstruction des logements collectifs ─────────────────────────────────
def test_misurf_unique_avant_2025():
    r = calculer(LC_2022)["icconstruction_max"]
    # Misurf = −0,169 + 1,30 × 1 000 / 10 000 = −0,039 ; pas de Misurf_moy (petits logements)
    assert set(r.coefficients) >= {"Micombles", "Misurf"} and "Misurf_moy" not in r.coefficients
    assert proche(r.coefficients["Misurf"], -0.039)
    assert proche(r.valeur, 740 * (1 - 0.039))


def test_misurf_moy_et_tot_apres_2025():
    r = calculer(LC_2025)["icconstruction_max"]
    # Misurf_moy = (100 − 2,5 × 20) / 650 ; Misurf_tot = −0,104 + 0,8 × 1 000 / 10 000 = −0,024
    assert proche(r.coefficients["Misurf_moy"], 50 / 650) and proche(r.coefficients["Misurf_tot"], -0.024)
    assert proche(r.valeur, 650 + 50 - 0.024 * 650)


@pytest.mark.parametrize("projet", [LC_2022, LC_2025])
def test_pas_de_coefficients_du_decret_2026_avant_juillet_2026(projet):
    for r in calculer(projet).values():
        assert not COEFS_2026_200 & set(r.coefficients)


def test_coefficients_du_decret_2026_apres_juillet_2026():
    r = calculer(replace(LC_2025, pc_apres_juillet_2026=True))
    assert {"MiHSP", "Miagrément_ext", "Miclim_RCU"} <= set(r["icconstruction_max"].coefficients)
    assert "MbHSP" in r["bbio_max"].coefficients


def test_formule_affichee_avant_2025():
    symbolique, _ = formules("icconstruction_max", "Icconstruction_max", calculer(LC_2022)["icconstruction_max"])
    assert "(1 + Micombles + Misurf)" in symbolique and "HSP" not in symbolique


# ─── Mipv ────────────────────────────────────────────────────────────────────
def test_mipv_nul_avant_2025_sauf_bureaux_de_plus_de_1000_m2():
    assert calculer(BUREAUX_2022)["icconstruction_max"].coefficients["Mipv"] == 0
    assert calculer(replace(BUREAUX_2022, emprise_sup_1000=True))["icconstruction_max"].coefficients["Mipv"] == 30
    assert calculer(replace(BUREAUX_2022, periode_pc="2025 à 2027"))["icconstruction_max"].coefficients["Mipv"] == 30
    lc = replace(LC_2022, iclot13=50)
    assert calculer(lc)["icconstruction_max"].coefficients["Mipv"] == 0


# ─── Icénergie des maisons ───────────────────────────────────────────────────
@pytest.mark.parametrize("periode, rcu, classe, gaz, moyen", [
    ("2022 à 2024", True, False, False, 160),       # pas de valeur « réseau de chaleur » avant le décret
    ("2022 à 2024", True, True, False, 160),
    ("2022 à 2024", False, False, True, 280),       # dérogation gaz (PC avant le 31/12/2023)
    ("2025 à 2027", True, False, False, 200),
    ("2025 à 2027", True, True, False, 200),        # dérogation RCU classé : valeur RCU 2022-2024 post-décret
    ("2025 à 2027", False, False, True, 160),       # dérogation gaz sans effet après 2024
])
def test_icenergie_maxmoyen_maisons(periode, rcu, classe, gaz, moyen):
    p = replace(MAISON_2022, periode_pc=periode, rcu=rcu, rcu_classe=classe, derogation_gaz=gaz)
    assert calculer(p)["icenergie_max"].moyen == moyen


# ─── Bbio des maisons ────────────────────────────────────────────────────────
@pytest.mark.parametrize("smoy, avant, apres", [(80, 49 - 40, 49 - 39.2), (120, 19 - 24, 18 - 21.6), (200, -11, -9)])
def test_mbsurf_moy_maisons(smoy, avant, apres):
    p = replace(MAISON_2022, sref=smoy)
    assert proche(calculer(p)["bbio_max"].coefficients["Mbsurf_moy"] * 63, avant)
    assert proche(calculer(replace(p, periode_pc="2025 à 2027"))["bbio_max"].coefficients["Mbsurf_moy"] * 63, apres)


# ─── Usages soumis depuis le 1er mai 2026 ────────────────────────────────────
@pytest.mark.parametrize("projet, attendu", [
    (HOTEL, False),                                                   # entre le 1er mai et le 30 juin 2026
    (replace(HOTEL, pc_apres_mai_2026=False), True),                  # avant le 1er mai 2026
    (replace(HOTEL, pc_apres_juillet_2026=True, pc_apres_mai_2026=False), False),
    (replace(HOTEL, periode_pc="2022 à 2024"), True),
    (replace(LC_2025, pc_apres_mai_2026=False), False),               # logements : soumis depuis 2022
])
def test_hors_champ(projet, attendu):
    assert hors_champ(projet) is attendu


def test_libelles_date_et_texte():
    assert libelle_depot(HOTEL).endswith("entre le 1er mai et le 30 juin 2026")
    assert libelle_depot(replace(HOTEL, pc_apres_mai_2026=False)).endswith("avant le 1er mai 2026")
    assert libelle_depot(LC_2025).endswith("avant le 1er juillet 2026")
    assert "avant le décret n° 2024-1258" in texte_applicable(LC_2022)
    assert texte_applicable(LC_2025).endswith("décret n° 2024-1258")
    assert texte_applicable(HOTEL).endswith("décret n° 2026-16")
    assert texte_applicable(replace(LC_2025, pc_apres_juillet_2026=True)).endswith("décret n° 2026-200")
