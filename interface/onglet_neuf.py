"""
Onglet « Construction neuve » : récapitulatif, six cartes de seuils, détail des modulations,
sauvegarde par lien, export texte, label Effinergie et liens.
"""
from datetime import date
from html import escape

import streamlit as st

from interface import icones as I
from interface.parametres import (BOUTON_TELECHARGER, COLONNES_NEUF, COPIER_TEXTE, NOM_FICHIER_EXPORT, TEXTE_EFFINERGIE,
                                  TEXTE_LIEN, TITRES_CARTES, URL_DEPOT, URL_OFFICIEL, URL_WIKIPEDIA, URL_ZONES)
from interface.style import BRONZE_SPICE, carte_seuil
from seuils_re2020 import alertes
from seuils_re2020.presentation import details, explication_dh, formules, libelle_depot, nombre_fr, recapitulatif
from seuils_re2020.variables import INDICATEURS, NOMS_MOYENS, USAGES_EFFINERGIE


def titre_carte(cle):
    st.markdown(f'<div class="titre-carte">{I.ico_html(I.CARTES[cle])}{TITRES_CARTES[cle]}</div>',
                unsafe_allow_html=True)


def _ligne_evolution(actuel, valeurs_futures, decimales):
    """(« 2028 : 545,5 · 2031 : 460,8 » ou « identique en 2028 et 2031 », icône du sens d'évolution)."""
    if not valeurs_futures or not isinstance(actuel, (int, float)):
        return "", None
    if all(v == actuel for v in valeurs_futures.values()):
        return "identique en " + " et ".join(valeurs_futures), I.DIVERS["stable"]
    dernier = list(valeurs_futures.values())[-1]
    sens = I.DIVERS["baisse"] if isinstance(dernier, (int, float)) and dernier < actuel else I.DIVERS["hausse"]
    return " · ".join(f"{jalon} : {nombre_fr(v, decimales)}" for jalon, v in valeurs_futures.items()), sens


def afficher(projet, departement, resultats, evol, adresse, export):
    st.markdown(f'<div class="barre-recap">{I.ico_html(I.DIVERS["recap"], BRONZE_SPICE)}'
                f'{escape(recapitulatif(projet, departement))}'
                f'<div class="details-saisies">{escape(details(projet))}</div></div>', unsafe_allow_html=True)
    principal, cote = st.columns(COLONNES_NEUF, gap="large")
    with principal:
        _seuils(projet, resultats, evol)
        _detail(projet, resultats)
    with cote:
        _cartes_laterales(projet, resultats, adresse, export)


def _seuils(projet, resultats, evol):
    st.markdown(f'<div class="bandeau"><b>{I.ico_html(I.DIVERS["bandeau"])}'
                f'{escape(libelle_depot(projet, majuscule=True))}</b></div>', unsafe_allow_html=True)
    for message in alertes(projet):
        st.warning(message, icon=I.ico(I.DIVERS["alerte"]))
    for rangee in (INDICATEURS[:3], INDICATEURS[3:]):
        for colonne, (cle, nom, unite, dec, famille) in zip(st.columns(3), rangee):
            futures = {jalon: v[cle] for jalon, v in evol.items()}
            texte_evol, sens = _ligne_evolution(resultats[cle].valeur, futures, dec)
            colonne.markdown(carte_seuil(nom, nombre_fr(resultats[cle].valeur, dec), unite, famille, texte_evol,
                                         icone=I.SEUILS[cle], icone_evolution=sens), unsafe_allow_html=True)


def _detail(projet, resultats):
    with st.container(key="carte_detail"):
        titre_carte("detail")
        for cle, nom, unite, dec, _famille in INDICATEURS:
            r = resultats[cle]
            symbolique, chiffres = formules(cle, nom, r)
            with st.expander(f"{I.ico(I.SEUILS[cle])} {nom} = {nombre_fr(r.valeur, dec)} {unite}"):
                st.markdown(f'<div class="formule">{escape(symbolique)}</div>'
                            f'<div class="formule chiffres">{escape(chiffres)}</div>', unsafe_allow_html=True)
                if r.moyen is not None:
                    st.write(f"{NOMS_MOYENS[cle]} : {nombre_fr(r.moyen, 2)}")
                explication = explication_dh(projet, r.valeur) if cle == "dh_max" else ""
                if explication:
                    st.info(explication, icon=I.ico(I.DIVERS["info"]))
                if r.coefficients:
                    st.table({"modulation": list(r.coefficients),
                              "valeur": [nombre_fr(v, 4) for v in r.coefficients.values()]})


def _cartes_laterales(projet, resultats, adresse, export):
    with st.container(key="carte_partage"):
        titre_carte("partage")
        st.code(adresse, language=None, wrap_lines=True)
        st.caption(TEXTE_LIEN)

    with st.container(key="carte_export"):
        titre_carte("export")
        st.download_button(BOUTON_TELECHARGER, data=export, file_name=NOM_FICHIER_EXPORT.format(jour=date.today()),
                           mime="text/plain", use_container_width=True, icon=I.ico(I.DIVERS["telecharger"]))
        with st.expander(f"{I.ico(I.DIVERS['copier'])} {COPIER_TEXTE}"):
            st.code(export, language=None)

    if projet.usage_id in USAGES_EFFINERGIE:
        with st.container(key="carte_effinergie"):
            titre_carte("effinergie")
            st.write(f"DH Effinergie : **{nombre_fr(resultats['dh_effinergie'].valeur, 0)}** °C.h")
            st.caption(TEXTE_EFFINERGIE)

    with st.container(key="carte_liens"):
        titre_carte("liens")
        st.markdown(f"- [{I.ico(I.LIENS['officiel'])} Site officiel de la RE2020]({URL_OFFICIEL})\n"
                    f"- [{I.ico(I.LIENS['wikipedia'])} La RE2020 sur Wikipédia]({URL_WIKIPEDIA})\n"
                    f"- [{I.ico(I.LIENS['zones'])} Carte des zones climatiques]({URL_ZONES})\n"
                    f"- [{I.ico(I.LIENS['depot'])} Code source et données]({URL_DEPOT})")
