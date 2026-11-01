"""
Onglet « Extension et surélévation » : régime applicable (arrêté du 4 août 2021, art. 50-3)
et seuils exigés. Usage, Sref, zone et climatisation viennent du menu. Non repris dans l'export texte.
"""
from html import escape

import streamlit as st

from interface import icones as I
from interface.menu import champ
from interface.onglet_neuf import titre_carte
from interface.parametres import (COLONNES_TYPOLOGIE, LARGEURS_ENCADRES, MENTION_EXPORT_TRAVAUX, NOTE_BORNES,
                                  TEXTE_SEUILS_TRAVAUX, TEXTE_VALIDER, TITRE_BORNES, TITRES_CARTES, URL_ARTICLE_50_3,
                                  URL_FICHE_EXTENSION)
from interface.style import carte_seuil
from seuils_re2020 import regime_travaux
from seuils_re2020.presentation import libelle_usage, nombre_fr, unite_surface
from seuils_re2020.variables import INDICATEURS, TYPOLOGIES_TRAVAUX

etat = st.session_state


def afficher(projet, resultats):
    unite = unite_surface(projet.usage_id)
    regime = _saisies(projet, unite)
    _regime(regime)
    _seuils_exiges(regime, resultats)
    _justification(regime)


def _saisies(projet, unite):
    """Type de travaux et Sref existante ; renvoie le régime retenu."""
    with st.container(key="carte_extension"):
        st.markdown(f'<div class="titre-carte">{I.ico_html(I.CARTES["extension"])}{TITRES_CARTES["extension"]}'
                    f'<span class="titre-complement">{escape(libelle_usage(projet.usage_id))} · zone {projet.zone}'
                    f'</span></div>', unsafe_allow_html=True)
        _gauche, milieu, _droite = st.columns(COLONNES_TYPOLOGIE)
        milieu.radio(options=list(TYPOLOGIES_TRAVAUX), format_func=TYPOLOGIES_TRAVAUX.get, horizontal=True,
                     **champ("typologie"))
        # deux encadrés : surface existante (saisie) et surface des travaux (rappel du menu)
        _m1, case_existant, _m2, case_travaux, _m3 = st.columns(LARGEURS_ENCADRES)
        with case_existant.container(key="encadre_existant"):
            st.number_input(min_value=1.0, step=10.0, **champ("sexistant", unite=unite))
            st.caption(TEXTE_VALIDER)
        regime = regime_travaux(projet.usage_id, etat["typologie"], projet.sref, etat["sexistant"], projet.zone,
                                projet.climatise)
        with case_travaux.container(key="encadre_travaux"):
            st.markdown(f'<div class="rappel-travaux">Surface des travaux (Sref du menu) :<br>'
                        f'<span class="valeur-travaux">{nombre_fr(projet.sref, 0)} {unite}</span>'
                        f'<div class="part-existant">Part de l\'existant : <b>{nombre_fr(100 * regime.part, 1)} %</b>'
                        f'</div></div>', unsafe_allow_html=True)
    return regime


def _regime(regime):
    """Bandeau de la couleur du régime, avec une flèche dans la marge."""
    st.markdown(f'<div class="bandeau bandeau-regime regime-{regime.cle}"><b>{I.ico_html(I.CARTES["regime"])}'
                f'{escape(regime.libelle)}</b><div class="sous-bandeau">{escape(regime.cas)}</div></div>',
                unsafe_allow_html=True)
    st.write(regime.texte)
    st.caption(f"{regime.source} · cas : {regime.source_cas}")


def _seuils_exiges(regime, resultats):
    """Mêmes valeurs que l'onglet Construction neuve, calculées sur la Sref des travaux."""
    exiges = [ind for ind in INDICATEURS if ind[0] in regime.indicateurs]
    for debut in range(0, len(exiges), 3):
        for colonne, (cle, nom, unite, dec, famille) in zip(st.columns(3), exiges[debut:debut + 3]):
            valeur = regime.dh_max if cle == "dh_max" and regime.dh_max is not None else resultats[cle].valeur
            colonne.markdown(carte_seuil(nom, nombre_fr(valeur, dec), unite, famille, icone=I.SEUILS[cle]),
                             unsafe_allow_html=True)
    if regime.texte_dh:
        st.info(regime.texte_dh, icon=I.ico(I.DIVERS["info"]))
    if exiges:
        st.caption(TEXTE_SEUILS_TRAVAUX)
    st.caption(MENTION_EXPORT_TRAVAUX)


def _justification(regime):
    """Cas testés dans l'ordre, lecture des bornes, textes."""
    with st.container(key="carte_cas"):
        titre_carte("cas")
        st.table({"cas": [c for _o, c, _r, _v in regime.cas_testes],
                  "régime": [r for _o, _c, r, _v in regime.cas_testes],
                  "retenu": ["oui" if v else "" for _o, _c, _r, v in regime.cas_testes]})
        with st.expander(f"{I.ico(I.DIVERS['alerte'])} {TITRE_BORNES}"):
            st.write(NOTE_BORNES)
        st.markdown(f"- [{I.ico(I.LIENS['officiel'])} Article 50-3 de l'arrêté du 4 août 2021]({URL_ARTICLE_50_3})\n"
                    f"- [{I.ico(I.LIENS['officiel'])} Fiche d'application DHUP « extension et construction "
                    f"< 50 m² »]({URL_FICHE_EXTENSION})")
