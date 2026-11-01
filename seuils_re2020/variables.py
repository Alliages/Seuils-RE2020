"""
Paramètres et constantes du calculateur, regroupés ici pour la lisibilité.

Aucune valeur réglementaire n'est écrite dans le code : elles sont toutes dans donnees/*.csv.
Ce fichier ne contient que des listes de choix, des libellés et des paramètres techniques.
"""
from pathlib import Path

# ─── Version de l'outil ──────────────────────────────────────────────────────
VERSION = "1.0.2"

# ─── Indicateurs : (clé, libellé, unité, décimales affichées, famille) ───────
INDICATEURS = [
    ("bbio_max", "Bbio_max", "points", 1, "bioclimatique"),
    ("cepnr_max", "Cep,nr_max", "kWhep/m².an", 1, "energie"),
    ("cep_max", "Cep_max", "kWhep/m².an", 1, "energie"),
    ("icenergie_max", "Icénergie_max", "kg éq. CO₂/m²", 1, "carbone"),
    ("icconstruction_max", "Icconstruction_max", "kg éq. CO₂/m² (50 ans)", 1, "carbone"),
    ("dh_max", "DH_max", "°C.h", 0, "confort"),
]
# Nom réglementaire de la valeur moyenne : « valeur de l'exigence pour un bâtiment moyen »
NOMS_MOYENS = {"bbio_max": "Bbio_maxmoyen", "cepnr_max": "Cep,nr_maxmoyen", "cep_max": "Cep_maxmoyen",
               "icenergie_max": "Icénergie_maxmoyen", "icconstruction_max": "Icconstruction_maxmoyen",
               "dh_max": "DH_maxcat"}
# Termes ajoutés hors de la parenthèse dans Icconstruction_max (kg éq. CO₂/m²)
TERMES_ADDITIFS = {"Migéo", "Miinfra", "Mivrd", "Mipv", "Mided", "Miagrément_ext", "MiHSP", "Miclim_RCU"}

# ─── Usages particuliers (numéros de donnees/usages.csv) ─────────────────────
USAGE_MAISON, USAGE_LOGEMENT_COLLECTIF = 1, 2
USAGES_LOGEMENT = {USAGE_MAISON, USAGE_LOGEMENT_COLLECTIF}
USAGES_EFFINERGIE = {1, 2, 3, 4, 5}                  # label Effinergie : logements, bureaux, enseignement
USAGES_RE2020_DES_2022 = {1, 2, 3, 4, 5}             # autres usages : PC à partir de 2026 (décret 2026-16)
SEUIL_AGREMENT = 0.10                                # Miagrément_ext s'applique au-delà de 10 % de la Sref

# ─── Listes de choix (identiques au classeur de référence) ───────────────────
ZONES = ["H1a", "H1b", "H1c", "H2a", "H2b", "H2c", "H2d", "H3"]
ZONES_CHAUDES = {"H2d", "H3"}
ALTITUDES = ["<400m", "400m-800m", ">800m"]
LIBELLES_ALTITUDE = {"<400m": "altitude < 400 m", "400m-800m": "altitude 400 à 800 m", ">800m": "altitude > 800 m"}
PERIODES_PC = ["2022 à 2024", "2025 à 2027", "2028 à 2030", "à partir de 2031"]
PERIODE_2022, PERIODE_2025, PERIODE_2028, PERIODE_2031 = PERIODES_PC
# année représentative de chaque période (feuille Enumération, colonne P)
ANNEE_PERIODE = {PERIODE_2022: 2023, PERIODE_2025: 2026, PERIODE_2028: 2029, PERIODE_2031: 2032}
EXPOSITIONS_BRUIT = ["BR1", "BR2", "BR3"]
CATEGORIES = [1, 2, 3]
CLASSES_INERTIE = ["Très légère, légère ou moyenne", "Lourde ou très lourde"]

# Évolution affichée sous chaque seuil : jalon -> période de dépôt correspondante
JALONS_FUTURS = {"2028": PERIODE_2028, "2031": PERIODE_2031}

# ─── Décret n° 2026-200 du 18 mars 2026 ──────────────────────────────────────
# Applicable aux permis de construire déposés à partir du 1er juillet 2026 :
# MbHSP, McHSP, MiHSP, Miagrément_ext, Miclim_RCU, Misurf_tot et Icconstruction des IGH.
PERIODE_DECOUPEE_2026 = PERIODE_2025            # période où la date exacte du PC compte
PERIODES_APRES_DECRET = {PERIODE_2028, PERIODE_2031}

# ─── Dérogation IGH sur Icconstruction_maxmoyen (décret 2026-200) ────────────
# Interprétation du classeur de référence : 2028 = 95 % de la valeur 2025-2027 ;
# 2031 = 95 % de la valeur 2028 standard (point d'interprétation encore ouvert).
COEF_IGH = 0.95

# ─── Icénergie_maxmoyen (donnees/icenergie_moyen.csv) ────────────────────────
PERIODE_ICENERGIE_APRES_DECRET = "à partir de 2028"  # une seule colonne pour 2028 à 2030 et 2031
# Dérogation RCU classé : PC déposé avant le 31/12/2027 et réseau classé -> valeurs RCU de 2022-2024.
PERIODES_DEROGATION_RCU = {PERIODE_2022, PERIODE_2025}

# ─── DH_max : explication affichée au-delà de la valeur du logement ──────────
DH_REFERENCE = 1250             # DH_maxcat du logement en catégorie 1, non climatisé (°C.h)
SMOYLGT_DH = 60                 # logements collectifs : DH_max dépend de Smoylgt jusqu'à 60 m²

# ─── Extensions et surélévations (onglet dédié, donnees/travaux_*.csv) ───────
TYPOLOGIES_TRAVAUX = {"extension": "Extension", "surelevation": "Surélévation"}
# Usages hors « activités tertiaires spécifiques, usage industriel ou artisanal » (numéros de donnees/usages.csv) :
# maisons, logements collectifs, bureaux, enseignement primaire et secondaire. Tous les autres usages en relèvent.
USAGES_HORS_TERTIAIRE_SPECIFIQUE = {1, 2, 3, 4, 5}
DECIMALES_PART = 6              # arrondi de la part de l'existant : 90 / 300 donne bien 0,30 pile

# ─── Emplacements ────────────────────────────────────────────────────────────
DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "donnees"
SEPARATEUR_CSV = ";"

# ─── Affichage ───────────────────────────────────────────────────────────────
NON_APPLICABLE = "non applicable"
NE_S_APPLIQUE_PAS = "ne s'applique pas"
