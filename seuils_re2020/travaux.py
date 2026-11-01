"""
Extensions et surélévations : régime RE2020 applicable (arrêté du 4 août 2021, art. 50-3).

Les cas, les régimes et la majoration de DH_max sont dans donnees/travaux_*.csv :
le premier cas vrai, dans l'ordre du fichier, donne le régime (même principe que le classeur).
"""
from dataclasses import dataclass, field

from . import donnees
from .expressions import evaluer
from .variables import DECIMALES_PART, TYPOLOGIES_TRAVAUX, USAGE_MAISON, USAGES_HORS_TERTIAIRE_SPECIFIQUE


@dataclass
class Regime:
    """Régime retenu pour les travaux et raison du choix."""
    cle: str                                  # complete, light, moyens ou rt2012
    libelle: str                              # « RE2020 light »…
    indicateurs: list                         # clés des seuils exigés (variables.INDICATEURS)
    texte: str                                # ce qui s'applique
    source: str                               # texte réglementaire du régime
    cas: str                                  # cas retenu (donnees/travaux_cas.csv)
    source_cas: str
    ordre_cas: int
    part: float                               # Sref des travaux / Sref des locaux existants
    dh_max: float = None                      # DH_max imposé par le texte, sinon None (calcul normal)
    texte_dh: str = ""
    cas_testes: list = field(default_factory=list)   # [(ordre, cas, régime, vrai ?)] pour l'affichage


def variables_travaux(usage_id, typologie, sref, sexistant, zone="", climatise=False):
    """Variables des conditions de donnees/travaux_*.csv (textes en minuscules)."""
    return {"typologie": typologie, "maison": usage_id == USAGE_MAISON,
            "tertiaire_specifique": usage_id not in USAGES_HORS_TERTIAIRE_SPECIFIQUE, "sref": float(sref),
            "part": round(float(sref) / float(sexistant), DECIMALES_PART) if sexistant else float("inf"),
            "zoneclim": zone.lower(), "climatise": bool(climatise)}


def regime_travaux(usage_id, typologie, sref, sexistant, zone="", climatise=False):
    """Régime applicable à une extension ou une surélévation (premier cas vrai)."""
    if typologie not in TYPOLOGIES_TRAVAUX:
        raise ValueError(f"typologie inconnue : {typologie}")
    v = variables_travaux(usage_id, typologie, sref, sexistant, zone, climatise)
    testes, retenu = [], None
    regimes = donnees.travaux_regimes()
    for ordre, condition, regime, libelle_cas, source in donnees.travaux_cas():
        vrai = retenu is None and bool(evaluer(condition, v))
        testes.append((ordre, libelle_cas, regimes[regime]["libelle"], vrai))
        if vrai:
            retenu = (ordre, regime, libelle_cas, source)
    ordre, cle, libelle_cas, source_cas = retenu             # la dernière ligne du fichier est toujours vraie
    r = regimes[cle]
    resultat = Regime(cle=cle, libelle=r["libelle"], indicateurs=r["indicateurs"], texte=r["texte"],
                      source=r["source"], cas=libelle_cas, source_cas=source_cas, ordre_cas=ordre,
                      part=v["part"], cas_testes=testes)
    for ligne in donnees.table("travaux_dh"):                 # majoration de DH_max (première ligne vraie)
        if evaluer(ligne["condition"], {**v, "regime": cle}):
            resultat.dh_max, resultat.texte_dh = float(ligne["dh_max"]), ligne["texte"]
            break
    return resultat
