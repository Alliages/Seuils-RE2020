"""
Description du projet et choix des règles applicables (période, décret 2026-200, RCU…).
"""
from dataclasses import dataclass

from . import donnees
from .expressions import NonApplicable, evaluer
from .variables import ANNEE_PERIODE, PERIODE_DECOUPEE_2026, PERIODES_APRES_DECRET


@dataclass
class Projet:
    """Saisies du projet (mêmes notions que la feuille Input_resultats du classeur)."""
    usage_id: int                         # 1 à 28, voir donnees/usages.csv
    zone: str                             # H1a … H3
    altitude: str                         # '<400m', '400m-800m', '>800m'
    sref: float                           # surface de référence (m²)
    periode_pc: str                       # '2022 à 2024' … 'à partir de 2031'
    pc_apres_juillet_2026: bool = True    # utile seulement pour la période 2025-2027
    nb_logements: float = 1               # Smoylgt = Sref / NL
    scombles: float = 0                   # combles aménagés < 1,8 m (maisons)
    exposition_bruit: str = "BR1"         # BR1, BR2, BR3
    categorie: int = 1                    # catégorie de contraintes extérieures
    climatise: bool = False
    rcu: bool = False                     # raccordé à un réseau de chaleur urbain
    rcu_classe: bool = False              # réseau classé (art. L. 712-1 du code de l'énergie)
    igh: bool = False                     # immeuble de grande hauteur
    sagrement: float = 0                  # surface cumulée d'agrément extérieur (m²)
    hsp: float = 2.5                      # hauteur sous plafond moyenne (m)
    iclot1: float = 0                     # impact lot 1 VRD (kg éq. CO2/m²)
    iclot2: float = 0                     # impact lot 2 fondations / infrastructure
    iclot13: float = 0                    # impact lot 13 photovoltaïque
    icded: float = 0                      # impact des données par défaut et forfaits
    classe_inertie: str = "Lourde ou très lourde"   # pour le DH Effinergie seulement


def decret_applicable(periode_pc, pc_apres_juillet_2026):
    """Le décret n° 2026-200 s'applique aux PC déposés à partir du 01/07/2026."""
    if periode_pc in PERIODES_APRES_DECRET:
        return True
    return periode_pc == PERIODE_DECOUPEE_2026 and pc_apres_juillet_2026


def decret_2026_applicable(projet):
    return decret_applicable(projet.periode_pc, projet.pc_apres_juillet_2026)


def variables(projet):
    """Variables utilisées par les expressions de donnees/regles.csv (textes en minuscules)."""
    usage = donnees.usages()[projet.usage_id]
    oui = lambda b: "oui" if b else "non"
    return {
        "usage": usage["principal"].replace("\xa0", " ").strip().lower(),
        "usage_detaille": usage["detaille"].replace("\xa0", " ").strip().lower(),
        "sref": float(projet.sref),
        "smoylgt": float(projet.sref) / float(projet.nb_logements),
        "scombles": float(projet.scombles),
        "hspmoy": float(projet.hsp),
        "sagrement": float(projet.sagrement),
        "expobruit": projet.exposition_bruit.lower(),
        "depotpc": projet.periode_pc.lower(),
        "depotpc_annee": ANNEE_PERIODE[projet.periode_pc],
        "rcu": oui(projet.rcu), "rcu_classe": oui(projet.rcu_classe),
        "climatise": oui(projet.climatise), "est_igh": oui(projet.igh),
        "decret2026": decret_2026_applicable(projet),
        "categorie": f"catégorie {projet.categorie}",
        "zoneclim": projet.zone.lower(),
        "elevation": projet.altitude.lower(),
        "icded": float(projet.icded), "iclot1": float(projet.iclot1),
        "iclot2": float(projet.iclot2), "iclot13": float(projet.iclot13),
        "classe_inertie": projet.classe_inertie.lower(),
    }


def appliquer(coefficient, projet, vars_):
    """Première règle vraie du coefficient pour l'usage ; à défaut, la règle « defaut »."""
    defaut = None
    for ids, condition, formule, _source in donnees.regles(coefficient):
        if ids is not None and projet.usage_id not in ids:
            continue
        if condition == "defaut":
            defaut = formule
            continue
        if evaluer(condition, vars_):
            return _valeur(evaluer(formule, vars_))
    if defaut is not None:
        return _valeur(evaluer(defaut, vars_))
    raise NonApplicable(f"aucune règle {coefficient} pour l'usage {projet.usage_id}")


def _valeur(x):
    """Les booléens Excel (VRAI/FAUX) valent 1/0 ; les textes passent tels quels."""
    return float(x) if isinstance(x, bool) else x
