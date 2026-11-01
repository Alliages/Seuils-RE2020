"""
Menu latéral : saisie du projet en cinq étapes repliables.
Les valeurs saisies restent dans st.session_state, sous le nom du champ (voir lien.CHAMPS).
"""
import streamlit as st

from interface import icones as I
from interface.parametres import (AIDE_IGH_GRISE, AIDES_REMPLACEES, ETAPES, LIBELLES, LIEN_ZONES, RENVOI_TRAVAUX,
                                  SREF_RENVOI_TRAVAUX, TEXTE_AGREMENT, TEXTE_CARBONE, TEXTE_SMOYLGT, TITRE_MENU,
                                  URL_ZONES)
from seuils_re2020 import decret_applicable, donnees
from seuils_re2020.presentation import libelle_departement, libelle_usage, nombre_fr, unite_surface
from seuils_re2020.variables import (ALTITUDES, CATEGORIES, CLASSES_INERTIE, EXPOSITIONS_BRUIT, LIBELLES_ALTITUDE,
                                     PERIODE_DECOUPEE_2026, PERIODES_PC, SEUIL_AGREMENT, USAGE_LOGEMENT_COLLECTIF,
                                     USAGE_MAISON, USAGES_EFFINERGIE, USAGES_LOGEMENT)

# ─── Paramètres ──────────────────────────────────────────────────────────────
AIDES = {**donnees.aides(), **AIDES_REMPLACEES}
DEPARTEMENTS = list(donnees.departements())          # dans l'ordre des numéros
etat = st.session_state


def champ(cle, aide=None, **valeurs):
    """Arguments communs d'un champ : libellé avec icône, clé d'état, infobulle (celle du classeur par défaut)."""
    return {"label": I.ico_libelle(cle, LIBELLES[cle].format(**valeurs)), "key": cle, "help": aide or AIDES.get(cle)}


def _etape(cle, ouverte=False):
    """Étape repliable, avec son icône dans le titre (garde la flèche de Streamlit)."""
    return st.expander(f"{I.ico(I.ETAPES[cle])} {ETAPES[cle]}", expanded=ouverte)


def _changement_usage():
    """Maison : un logement par défaut (Smoylgt = Sref), comme dans le classeur."""
    if etat["usage_id"] == USAGE_MAISON:
        etat["nb_logements"] = 1


def afficher():
    with st.sidebar:
        st.markdown(f'<div class="titre-menu">{I.ico_html(I.MENU)}{TITRE_MENU}</div>', unsafe_allow_html=True)
        _batiment()
        _permis()
        _contraintes()
        _carbone()
        _reseau()


def _batiment():
    with _etape("batiment", ouverte=True):
        st.selectbox(options=list(donnees.usages()), format_func=libelle_usage, on_change=_changement_usage,
                     **champ("usage_id"))
        usage = etat["usage_id"]
        st.selectbox(options=DEPARTEMENTS, format_func=libelle_departement, **champ("departement"))
        st.markdown(f'<div class="lien-zones">{I.ico_html(I.LIENS["zones"])}<a href="{URL_ZONES}" target="_blank">'
                    f'{LIEN_ZONES}</a></div>', unsafe_allow_html=True)
        st.selectbox(options=ALTITUDES, format_func=lambda a: LIBELLES_ALTITUDE[a][len("altitude "):],
                     **champ("altitude"))
        st.number_input(min_value=1.0, step=10.0, **champ("sref", unite=unite_surface(usage)))
        if etat["sref"] < SREF_RENVOI_TRAVAUX:
            st.markdown(f'<div class="renvoi-onglet">{I.ico_html(I.DIVERS["alerte"])}{RENVOI_TRAVAUX}</div>',
                        unsafe_allow_html=True)
        if usage in USAGES_LOGEMENT:
            st.number_input(min_value=1, step=1, format="%d", **champ("nb_logements"))
            st.caption(TEXTE_SMOYLGT.format(smoylgt=nombre_fr(etat["sref"] / etat["nb_logements"], 1)))
        if usage == USAGE_MAISON:
            st.number_input(min_value=0.0, **champ("scombles"))
        if usage in USAGES_LOGEMENT:
            st.number_input(min_value=2.0, step=0.05, **champ("hsp"))
        if usage == USAGE_LOGEMENT_COLLECTIF:
            st.number_input(min_value=0.0, **champ("sagrement"))
            st.caption(TEXTE_AGREMENT.format(taux=nombre_fr(100 * etat["sagrement"] / etat["sref"], 1),
                                             seuil=nombre_fr(100 * SEUIL_AGREMENT, 0)))
        if usage != USAGE_MAISON:
            # case IGH active seulement si le décret 2026-200 s'applique (PC déposé à partir du 1er juillet 2026)
            igh_possible = decret_applicable(etat["periode_pc"], etat["pc_apres_juillet_2026"])
            if not igh_possible:
                etat["igh"] = False
            st.checkbox(disabled=not igh_possible, **champ("igh", aide=None if igh_possible else AIDE_IGH_GRISE))


def _permis():
    with _etape("permis"):
        st.selectbox(options=PERIODES_PC, **champ("periode_pc"))
        if etat["periode_pc"] == PERIODE_DECOUPEE_2026:
            st.radio(options=[True, False], format_func=lambda b: "Oui" if b else "Non", horizontal=True,
                     **champ("pc_apres_juillet_2026"))


def _contraintes():
    with _etape("contraintes"):
        categories = CATEGORIES if donnees.usages()[etat["usage_id"]]["categorie3_possible"] else CATEGORIES[:2]
        if etat["categorie"] not in categories:
            etat["categorie"] = categories[0]
        st.selectbox(options=categories, format_func=lambda c: f"Catégorie {c}", **champ("categorie"))
        st.selectbox(options=EXPOSITIONS_BRUIT, **champ("exposition_bruit"))
        st.checkbox(**champ("climatise"))


def _carbone():
    with _etape("carbone"):
        st.caption(TEXTE_CARBONE)
        for cle in ("iclot1", "iclot2", "iclot13", "icded"):
            st.number_input(min_value=0.0, **champ(cle))


def _reseau():
    with _etape("reseau"):
        st.checkbox(**champ("rcu"))
        if not etat["rcu"]:
            etat["rcu_classe"] = False
        st.checkbox(disabled=not etat["rcu"], **champ("rcu_classe"))
        if etat["usage_id"] in USAGES_EFFINERGIE:
            st.selectbox(options=CLASSES_INERTIE, **champ("classe_inertie"))
