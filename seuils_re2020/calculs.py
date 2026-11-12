"""
Calcul des six seuils RE2020 (et du DH Effinergie) pour un projet.

Formules générales (annexe à l'article R. 172-4, chapitre II) :
    Bbio_max          = Bbio_maxmoyen × (1 + Mbgéo + Mbcombles + Mbsurf_moy + Mbsurf_tot + Mbbruit + MbHSP)
    Cep,nr_max        = Cep,nr_maxmoyen × (1 + Mcgéo + Mccombles + Mcsurf_moy + Mcsurf_tot + Mccat + McHSP)
    Cep_max           = Cep_maxmoyen × (même somme)
    Icénergie_max     = Icénergie_maxmoyen × (même somme)
    Icconstruction_max = Icconstruction_maxmoyen × (1 + Micombles + Misurf_moy + Misurf_tot)
                         + Migéo + Miinfra + Mivrd + Mipv + Mided + Miagrément_ext + MiHSP + Miclim_RCU
    DH_max            = DH_maxcat
Les valeurs viennent de donnees/ ; ce module ne fait qu'assembler.

Selon la date de dépôt du PC, les formules ne contiennent que les coefficients du texte applicable :
    - PC 2022-2024 (avant le décret 2024-1258) : Misurf unique au lieu de Misurf_moy + Misurf_tot ;
    - PC avant le 1er juillet 2026 : sans MbHSP, McHSP, MiHSP, Miagrément_ext, Miclim_RCU (décret 2026-200).
"""
from dataclasses import dataclass, field

from . import donnees
from .expressions import NonApplicable
from .regles import appliquer, avant_retex, decret_2026_applicable, variables
from .variables import (COEF_IGH, COEFS_DECRET_2026, NE_S_APPLIQUE_PAS, NOM_MISURF_AVANT_RETEX, NON_APPLICABLE,
                        PERIODE_2022, PERIODE_2025, PERIODE_2028, PERIODE_2031, PERIODE_ICENERGIE_APRES_DECRET,
                        PERIODES_APRES_DECRET, PERIODES_DEROGATION_RCU, USAGES_SANS_RCU_AVANT_RETEX)

# ─── Paramètres ──────────────────────────────────────────────────────────────
MOYEN_ENERGIE = {"cepnr_max": "cepnr", "cep_max": "cep"}   # clé de donnees.moyennes() par indicateur


@dataclass
class Resultat:
    """Un seuil : sa valeur (nombre ou texte) et le détail de ses coefficients."""
    valeur: object
    moyen: object = None
    coefficients: dict = field(default_factory=dict)


# ─── Tables de valeurs ───────────────────────────────────────────────────────
def _table(nom, *cles):
    v = donnees.index(nom, *[c[0] for c in cles]).get(tuple(str(c[1]).lower() for c in cles))
    if v is None:
        raise NonApplicable(f"{nom} : pas de valeur pour {cles}")
    return v


def _mbbruit(projet):
    if projet.categorie == 3:
        expo = "cat3"
    else:
        expo = "br1" if projet.exposition_bruit.upper() == "BR1" else "br2_br3"
    table = donnees.index("mbbruit", "usage_id", "exposition", "zone")
    for zone in (projet.zone.lower(), "*"):            # valeur par zone, sinon valeur unique
        cle = (str(projet.usage_id), expo, zone)
        if cle in table:
            if table[cle] is None:
                raise NonApplicable("Mbbruit sans objet (catégorie 3 impossible pour cet usage)")
            return table[cle]
    raise NonApplicable("Mbbruit introuvable")


def _mcgeo(projet, vars_):
    if appliquer("Mcgeo_exception_MI", projet, vars_) == "oui":
        return _table("mcgeo_exception", ("zone", projet.zone))
    return _table("mcgeo", ("usage_id", projet.usage_id), ("altitude", projet.altitude), ("zone", projet.zone))


def _icenergie_moyen(projet, vars_):
    avant = avant_retex(projet)
    if avant:
        # maisons, PC déposé avant le 31/12/2023 avec gaz prévu par un PA ou une ZAC : valeur dérogatoire
        gaz = appliquer("Icenergie_maxmoyen_gaz", projet, vars_)
        if gaz:
            return gaz
    # avant le décret 2024-1258, pas de valeur « réseau de chaleur » pour les maisons (160 dans tous les cas)
    rcu = projet.rcu and not (avant and projet.usage_id in USAGES_SANS_RCU_AVANT_RETEX)
    # dérogation RCU classé : valeurs RCU 2022-2024 pour les PC déposés avant fin 2027
    if rcu and projet.rcu_classe and projet.periode_pc in PERIODES_DEROGATION_RCU:
        periode = PERIODE_2022
    elif projet.periode_pc in PERIODES_APRES_DECRET:
        periode = PERIODE_ICENERGIE_APRES_DECRET
    else:
        periode = projet.periode_pc
    return _table("icenergie_moyen", ("usage_id", projet.usage_id), ("rcu", "oui" if rcu else "non"),
                  ("periode", periode))


def _selon_textes(coefs, projet):
    """Retire les coefficients du décret 2026-200 quand il ne s'applique pas (ils valent 0 dans ce cas)."""
    if decret_2026_applicable(projet):
        return coefs
    return {k: v for k, v in coefs.items() if k not in COEFS_DECRET_2026}


def _icconstruction_moyen(projet):
    lire = lambda p: _table("icconstruction_moyen", ("usage_id", projet.usage_id), ("periode", p))
    if projet.periode_pc == PERIODE_2028:
        return lire(PERIODE_2025) * COEF_IGH if projet.igh else lire(PERIODE_2028)
    if projet.periode_pc == PERIODE_2031:
        return lire(PERIODE_2028) * COEF_IGH if projet.igh else lire(PERIODE_2031)
    return lire(projet.periode_pc)


# ─── Indicateurs ─────────────────────────────────────────────────────────────
def _assembler(moyen, coefs):
    return moyen * (1 + sum(coefs.values()))


def bbio_max(projet, vars_):
    decret = decret_2026_applicable(projet)
    moyen = donnees.moyennes()[projet.usage_id]["bbio"]
    vars_ = {**vars_, "bbiomaxmoyen": moyen}
    c = {
        "Mbgéo": _table("mbgeo", ("usage_id", projet.usage_id), ("altitude", projet.altitude), ("zone", projet.zone)),
        "Mbcombles": appliquer("Mbcombles", projet, vars_),
        "Mbsurf_moy": appliquer("Mbsurf_moy", projet, vars_),
        "Mbsurf_tot": appliquer("Mbsurf_tot", projet, vars_),
        "Mbbruit": _mbbruit(projet),
        "MbHSP": appliquer("MbHSP", projet, vars_) if decret else 0.0,
    }
    c = _selon_textes(c, projet)
    return Resultat(_assembler(moyen, c), moyen, c)


def coefficients_mc(projet, vars_, cepnr_moyen):
    decret = decret_2026_applicable(projet)
    vars_ = {**vars_, "cepnrmaxmoyen": cepnr_moyen}
    return _selon_textes({
        "Mcgéo": _mcgeo(projet, vars_),
        "Mccombles": appliquer("Mccombles", projet, vars_),
        "Mcsurf_moy": appliquer("Mcsurf_moy", projet, vars_),
        "Mcsurf_tot": appliquer("Mcsurf_tot", projet, vars_),
        "Mccat": _table("mccat", ("usage_id", projet.usage_id), ("categorie", projet.categorie), ("zone", projet.zone)),
        "McHSP": appliquer("McHSP", projet, vars_) if decret else 0.0,
    }, projet)


def icconstruction_max(projet, vars_):
    decret = decret_2026_applicable(projet)
    moyen = _icconstruction_moyen(projet)
    vars_ = {**vars_, "icconstructionmaxmoyen": moyen}
    seuil_infra, seuil_vrd = donnees.seuils_lots()[projet.usage_id]
    surf_moy, surf_tot = appliquer("Misurf_moy", projet, vars_), appliquer("Misurf_tot", projet, vars_)
    if avant_retex(projet):
        # avant le décret 2024-1258 : coefficient unique Misurf (surface moyenne pour les maisons,
        # Sref pour les autres usages) ; les règles 2022-2024 donnent Misurf_moy = 0 hors maisons
        surfaces = {NOM_MISURF_AVANT_RETEX: surf_moy + surf_tot}
    else:
        surfaces = {"Misurf_moy": surf_moy, "Misurf_tot": surf_tot}
    multiplicatifs = {"Micombles": appliquer("Micombles", projet, vars_), **surfaces}
    additifs = {
        "Migéo": _table("migeo", ("usage_id", projet.usage_id), ("altitude", projet.altitude), ("zone", projet.zone)),
        "Miinfra": 0.0 if projet.iclot2 <= seuil_infra else projet.iclot2 - seuil_infra,
        "Mivrd": 0.0 if projet.iclot1 <= seuil_vrd else projet.iclot1 - seuil_vrd,
        "Mipv": appliquer("Mipv", projet, vars_),
        "Mided": appliquer("Mided", projet, vars_),
        "Miagrément_ext": appliquer("Miagrement_ext", projet, vars_) if decret else 0.0,
        "MiHSP": appliquer("MiHSP", projet, vars_) if decret else 0.0,
        "Miclim_RCU": appliquer("Miclim_RCU", projet, vars_),
    }
    additifs = _selon_textes(additifs, projet)
    valeur = _assembler(moyen, multiplicatifs) + sum(additifs.values())
    return Resultat(valeur, moyen, {**multiplicatifs, **additifs})


def dh_max(projet, vars_):
    return Resultat(appliquer("DH_max", projet, vars_))


def dh_effinergie(projet, vars_, dh):
    """Label Effinergie (hors réglementation) : maisons, logements, bureaux, enseignement."""
    if not any(ids is None or projet.usage_id in ids for ids, *_ in donnees.regles("DH_effinergie")):
        return Resultat(NE_S_APPLIQUE_PAS)
    valeur = appliquer("DH_effinergie", projet, {**vars_, "dh_max": dh})
    # comme le classeur : un DH_max sans objet rend le label « sans objet »
    return Resultat(NE_S_APPLIQUE_PAS if valeur == NON_APPLICABLE else valeur)


# ─── Point d'entrée ──────────────────────────────────────────────────────────
def _protege(fonction):
    try:
        return fonction()
    except NonApplicable:
        return Resultat(NON_APPLICABLE)


def calculer(projet):
    """Renvoie {indicateur: Resultat} pour les six seuils et le DH Effinergie."""
    vars_ = variables(projet)
    sortie = {"bbio_max": _protege(lambda: bbio_max(projet, vars_))}

    # Les coefficients Mc sont communs à Cep,nr, Cep et Icénergie : calculés une seule fois
    moyens = donnees.moyennes()[projet.usage_id]
    try:
        mc = coefficients_mc(projet, vars_, moyens["cepnr"])
    except NonApplicable:
        mc = None

    def energie(cle):
        if mc is None:
            raise NonApplicable("coefficients Mc sans objet")
        moyen = _icenergie_moyen(projet, vars_) if cle == "icenergie_max" else moyens[MOYEN_ENERGIE[cle]]
        return Resultat(_assembler(moyen, mc), moyen, mc)

    for cle in ("cepnr_max", "cep_max", "icenergie_max"):
        sortie[cle] = _protege(lambda c=cle: energie(c))
    sortie["icconstruction_max"] = _protege(lambda: icconstruction_max(projet, vars_))
    sortie["dh_max"] = _protege(lambda: dh_max(projet, vars_))
    dh = sortie["dh_max"].valeur
    sortie["dh_effinergie"] = _protege(lambda: dh_effinergie(projet, vars_, dh))
    return sortie
