"""
Sauvegarde d'un projet dans l'adresse de la page (paramètres d'URL).

Le lien contient les saisies, pas les résultats : rouvert, il recalcule le projet avec la
version de l'outil en ligne. Aucune donnée n'est stockée sur un serveur.
"""
import math
from urllib.parse import urlencode

from seuils_re2020 import donnees
from seuils_re2020.variables import (ALTITUDES, CLASSES_INERTIE, EXPOSITIONS_BRUIT, PERIODES_PC, TYPOLOGIES_TRAVAUX,
                                     VERSION)

# ─── Paramètres : champ -> (nom dans l'URL, type, valeur par défaut) ─────────
CHAMPS = {
    "usage_id": ("usage", int, 2),
    "departement": ("dep", str, "Paris"),
    "altitude": ("alt", str, "<400m"),
    "sref": ("sref", float, 3000.0),
    "nb_logements": ("nl", int, 50),
    "scombles": ("combles", float, 0.0),
    "hsp": ("hsp", float, 2.5),
    "sagrement": ("agr", float, 0.0),
    "igh": ("igh", bool, False),
    "periode_pc": ("pc", str, "2025 à 2027"),
    "pc_apres_juillet_2026": ("juillet", bool, True),
    "categorie": ("cat", int, 1),
    "exposition_bruit": ("bruit", str, "BR1"),
    "climatise": ("clim", bool, False),
    "iclot1": ("lot1", float, 0.0),
    "iclot2": ("lot2", float, 0.0),
    "iclot13": ("lot13", float, 0.0),
    "icded": ("ded", float, 0.0),
    "rcu": ("rcu", bool, False),
    "rcu_classe": ("classe", bool, False),
    "classe_inertie": ("inertie", str, "Lourde ou très lourde"),
    # onglet Extension et surélévation (hors calcul des seuils)
    "typologie": ("travaux", str, "extension"),
    "sexistant": ("sexist", float, 1000.0),
}
CHAMPS_TRAVAUX = {"typologie", "sexistant"}                 # champs qui ne vont pas dans Projet
DEFAUTS = {champ: defaut for champ, (_nom, _type, defaut) in CHAMPS.items()}
PARAM_VERSION = "v"
VALEURS_MIN = {"sref": 1.0, "nb_logements": 1, "hsp": 2.0, "sexistant": 1.0}   # mêmes bornes que les champs de saisie
# Bornes hautes : un lien modifié à la main ne peut pas faire exploser les calculs (ou afficher « inf »)
VALEURS_MAX = {"sref": 1e6, "nb_logements": 10_000, "hsp": 10.0, "sexistant": 1e6, "sagrement": 1e6,
               "scombles": 1e6, "iclot1": 1e4, "iclot2": 1e4, "iclot13": 1e4, "icded": 1e4}


def _choix():
    """Valeurs admises pour les champs à liste."""
    return {"usage_id": set(donnees.usages()), "departement": set(donnees.zones_par_departement()),
            "altitude": set(ALTITUDES), "periode_pc": set(PERIODES_PC), "categorie": {1, 2, 3},
            "exposition_bruit": set(EXPOSITIONS_BRUIT), "classe_inertie": set(CLASSES_INERTIE),
            "typologie": set(TYPOLOGIES_TRAVAUX)}


def _convertir(texte, type_):
    if type_ is bool:
        if texte not in ("0", "1"):
            raise ValueError(texte)
        return texte == "1"
    if type_ is int:
        nombre = float(texte)                 # accepte « 50 » et « 50.0 »
        if not math.isfinite(nombre) or not nombre.is_integer():
            raise ValueError(texte)
        return int(nombre)
    if type_ is float:
        nombre = float(texte)
        if not math.isfinite(nombre):         # « inf » et « nan » refusés
            raise ValueError(texte)
        return nombre
    return type_(texte)


def lire(params):
    """Paramètres d'URL -> {champ: valeur}, en ignorant ce qui est absent ou invalide."""
    choix, sortie = _choix(), {}
    for champ, (nom, type_, _defaut) in CHAMPS.items():
        if nom not in params:
            continue
        try:
            valeur = _convertir(params[nom], type_)
        except (TypeError, ValueError):
            continue
        if champ in choix and valeur not in choix[champ]:
            continue
        if type_ in (int, float) and not VALEURS_MIN.get(champ, 0) <= valeur <= VALEURS_MAX.get(champ, math.inf):
            continue                          # hors bornes
        sortie[champ] = valeur
    return sortie


def _texte(valeur):
    if isinstance(valeur, bool):
        return "1" if valeur else "0"
    if isinstance(valeur, float):
        return f"{valeur:g}"
    return str(valeur)


def parametres(valeurs):
    """{champ: valeur} -> paramètres d'URL, sans les valeurs par défaut (liens courts)."""
    sortie = {PARAM_VERSION: VERSION}
    for champ, (nom, _type, defaut) in CHAMPS.items():
        if champ in valeurs and valeurs[champ] != defaut:
            sortie[nom] = _texte(valeurs[champ])
    return sortie


def adresse(base, params):
    """Lien complet à partager."""
    return f"{(base or '').split('?')[0]}?{urlencode(params)}"
