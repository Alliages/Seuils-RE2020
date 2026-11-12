"""
Calculateur de seuils RE2020 — interface Streamlit (point d'entrée).

Lancement : streamlit run app.py
Ce fichier enchaîne : état et lien -> menu -> calcul -> page. Le calcul est fait par le paquet
seuils_re2020 ; l'affichage est dans interface/ (menu.py, onglet_neuf.py, onglet_extension.py).
"""
from dataclasses import fields
from pathlib import Path

import streamlit as st

from interface import icones as I
from interface import lien, menu, onglet_extension, onglet_neuf
from interface.parametres import (COLONNES_ENTETE, INFOBULLE_VERSION, LIBELLE_VERSION, MESSAGE_HORS_CHAMP, ONGLETS,
                                  PIED_DE_PAGE, TITRE, VALEURS_NEUTRES)
from interface.style import CSS, logo
from seuils_re2020 import Projet, calculer, donnees, hors_champ
from seuils_re2020.presentation import champs_utiles, evolution, texte_export

# ─── Paramètres ──────────────────────────────────────────────────────────────
ZONES_PAR_DEPT = donnees.zones_par_departement()
CHAMPS_PROJET = {f.name for f in fields(Projet)}
# Favicon : hexagone à six secteurs, un par indicateur (source vectorielle : static/favicon.svg)
FAVICON = str(Path(__file__).parent / "static" / "favicon.png")
st.set_page_config(page_title=TITRE, page_icon=FAVICON, layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

# ─── État : lien (au premier affichage), puis valeurs conservées d'un écran à l'autre ──
etat = st.session_state
if "_initialise" not in etat:
    etat.update(lien.DEFAUTS)
    etat.update(lien.lire(dict(st.query_params)))
    etat["_initialise"] = True
for champ in lien.CHAMPS:                           # empêche Streamlit d'oublier un champ masqué
    etat[champ] = etat.get(champ, lien.DEFAUTS[champ])
etat["nb_logements"] = int(etat["nb_logements"])

menu.afficher()

# ─── Calcul ──────────────────────────────────────────────────────────────────
saisies = {champ: etat[champ] for champ in lien.CHAMPS}
utiles = champs_utiles(saisies["usage_id"], saisies["periode_pc"], saisies["pc_apres_juillet_2026"])
for champ, utile in utiles.items():                 # champ masqué : valeur sans effet sur les seuils
    if not utile:
        saisies[champ] = VALEURS_NEUTRES.get(champ, lien.DEFAUTS[champ])
projet = Projet(**{k: v for k, v in saisies.items() if k in CHAMPS_PROJET}, zone=ZONES_PAR_DEPT[saisies["departement"]])
resultats = calculer(projet)
evol = evolution(projet)

# lien de sauvegarde : l'adresse de la page suit les saisies des champs visibles
params_url = lien.parametres({k: v for k, v in saisies.items() if utiles.get(k, True)})
st.query_params.from_dict(params_url)
adresse = lien.adresse(st.context.url, params_url)
export = texte_export(projet, resultats, evol, departement=etat["departement"], lien=adresse)

# ─── Page ────────────────────────────────────────────────────────────────────
entete, version = st.columns(COLONNES_ENTETE)
entete.markdown(f'<div class="titre-page">{logo()}{TITRE}</div>', unsafe_allow_html=True)
version.markdown(f'<div style="text-align:right"><span class="version" title="{INFOBULLE_VERSION}">{LIBELLE_VERSION}</span></div>',
                 unsafe_allow_html=True)
if hors_champ(projet):          # usage soumis à la RE2020 seulement depuis le 1er mai 2026 : aucun seuil
    st.error(MESSAGE_HORS_CHAMP)
    st.caption(PIED_DE_PAGE)
    st.stop()
onglet_n, onglet_e = st.tabs([f"{I.ico(I.ONGLETS[cle])} {ONGLETS[cle]}" for cle in ("neuf", "extension")])
with onglet_n:
    onglet_neuf.afficher(projet, etat["departement"], resultats, evol, adresse, export)
with onglet_e:
    onglet_extension.afficher(projet, resultats)
st.caption(PIED_DE_PAGE)
