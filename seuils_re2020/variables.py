"""
Paramètres et constantes du calculateur, regroupés ici pour la lisibilité.

Aucune valeur réglementaire n'est écrite dans le code : elles sont toutes dans donnees/*.csv.
Ce fichier ne contient que des listes de choix, des libellés et des paramètres techniques.
"""
from pathlib import Path

# ─── Version de l'outil ──────────────────────────────────────────────────────
VERSION = "0.8.0"
EXCEL_REFERENCE = "calcul_seuils_RE2020_NU v2.2"

# ─── Emplacements ────────────────────────────────────────────────────────────
DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "donnees"
SEPARATEUR_CSV = ";"

# ─── Listes de choix (identiques au classeur de référence) ───────────────────
ZONES = ["H1a", "H1b", "H1c", "H2a", "H2b", "H2c", "H2d", "H3"]
ALTITUDES = ["<400m", "400m-800m", ">800m"]
PERIODES_PC = ["2022 à 2024", "2025 à 2027", "2028 à 2030", "à partir de 2031"]
# année représentative de chaque période (feuille Enumération, colonne P)
ANNEE_PERIODE = {"2022 à 2024": 2023, "2025 à 2027": 2026, "2028 à 2030": 2029, "à partir de 2031": 2032}
EXPOSITIONS_BRUIT = ["BR1", "BR2", "BR3"]
CATEGORIES = [1, 2, 3]
CLASSES_INERTIE = ["Très légère, légère ou moyenne", "Lourde ou très lourde"]

# ─── Décret n° 2026-200 du 18 mars 2026 ──────────────────────────────────────
# Applicable aux permis de construire déposés à partir du 1er juillet 2026 :
# MbHSP, McHSP, MiHSP, Miagrément_ext, Miclim_RCU, Misurf_tot et Icconstruction des IGH.
PERIODE_DECOUPEE_2026 = "2025 à 2027"           # période où la date exacte du PC compte
PERIODES_APRES_DECRET = {"2028 à 2030", "à partir de 2031"}

# ─── Dérogation IGH sur Icconstruction_maxmoyen (décret 2026-200) ────────────
# Interprétation du classeur de référence : 2028 = 95 % de la valeur 2025-2027 ;
# 2031 = 95 % de la valeur 2028 standard (point d'interprétation encore ouvert).
COEF_IGH = 0.95

# ─── Dérogation RCU classé sur Icénergie_maxmoyen ────────────────────────────
# PC déposé avant le 31/12/2027 et réseau classé : valeurs RCU de la période 2022-2024.
PERIODES_DEROGATION_RCU = {"2022 à 2024", "2025 à 2027"}

# ─── Affichage ───────────────────────────────────────────────────────────────
NON_APPLICABLE = "non applicable"
PAS_DE_SEUIL = "pas de seuil"
NE_S_APPLIQUE_PAS = "ne s'applique pas"
TOLERANCE_TESTS = 1e-6
