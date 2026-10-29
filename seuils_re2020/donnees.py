"""
Lecture des tables de donnees/ (une seule fois, puis gardées en mémoire).
"""
import csv
from functools import lru_cache

from .variables import DOSSIER_DONNEES, SEPARATEUR_CSV


def _nombre(texte):
    """'0.15' -> 0.15 ; 'NA' -> None (valeur absente dans le texte réglementaire)."""
    if texte in ("NA", "", None):
        return None
    return float(texte)


@lru_cache(maxsize=None)
def table(nom):
    """Liste de dictionnaires lus depuis donnees/<nom>.csv."""
    with open(DOSSIER_DONNEES / f"{nom}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=SEPARATEUR_CSV))


@lru_cache(maxsize=None)
def usages():
    """{id: {'principal': …, 'detaille': …, 'categorie3_possible': bool}}"""
    return {int(l["id"]): {"principal": l["usage_principal"], "detaille": l["usage_detaille"],
                           "categorie3_possible": l["categorie3_possible"] == "1"}
            for l in table("usages")}


@lru_cache(maxsize=None)
def zones_par_departement():
    return {l["departement"]: l["zone"] for l in table("zones_departements")}


def _ordre_numero(numero):
    """'01' … '19', '2A', '2B', '21' … : la Corse se range entre 19 et 21."""
    return float(numero.replace("2A", "20.1").replace("2B", "20.2"))


@lru_cache(maxsize=None)
def departements():
    """{nom: (numéro, zone)}, dans l'ordre des numéros."""
    lignes = sorted(table("zones_departements"), key=lambda l: _ordre_numero(l["numero"]))
    return {l["departement"]: (l["numero"], l["zone"]) for l in lignes}


@lru_cache(maxsize=None)
def index(nom, *cles):
    """Index d'une table de valeurs : (clés…) -> valeur numérique ou None."""
    return {tuple(l[c].lower() for c in cles): _nombre(l["valeur"]) for l in table(nom)}


@lru_cache(maxsize=None)
def moyennes():
    return {int(l["usage_id"]): {"bbio": float(l["bbio_maxmoyen"]), "cepnr": float(l["cepnr_maxmoyen"]),
                                 "cep": float(l["cep_maxmoyen"])} for l in table("moyennes")}


@lru_cache(maxsize=None)
def seuils_lots():
    return {int(l["usage_id"]): (float(l["seuil_infra"]), float(l["seuil_vrd"])) for l in table("seuils_lots")}


@lru_cache(maxsize=None)
def regles(coefficient):
    """Règles d'un coefficient, dans l'ordre du classeur (la première vraie l'emporte)."""
    sortie = []
    for l in table("regles"):
        if l["coefficient"] == coefficient:
            ids = None if l["usages"] == "*" else {int(x) for x in l["usages"].split(",")}
            sortie.append((ids, l["condition"], l["formule"], l["source"]))
    return sortie


@lru_cache(maxsize=None)
def aides():
    """Infobulles par champ : colonne I de l'Excel, complétée par donnees/aides_complements.csv."""
    sortie = {l["champ"]: l["texte"] for l in table("aides_complements")}
    sortie.update({l["champ"]: l["texte"] for l in table("aides")})   # l'Excel l'emporte
    return sortie


@lru_cache(maxsize=None)
def surfaces_minimales():
    """[(usages ou None pour tous, Sref maximale, message)] : petites constructions hors RE2020 complète."""
    return [(None if l["usages"] == "*" else {int(x) for x in l["usages"].split(",")}, float(l["sref_max"]), l["texte"])
            for l in table("surfaces_minimales")]
