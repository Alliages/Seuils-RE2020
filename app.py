"""
Calculateur de seuils RE2020 — interface Streamlit.

Lancement : streamlit run app.py
Le calcul est fait par le paquet seuils_re2020 ; ce fichier gère la saisie, l'affichage,
l'export et la sauvegarde par lien (paramètres d'URL, voir interface/lien.py).
"""
from datetime import date

import streamlit as st

from interface import lien
from interface.style import CSS, carte_seuil
from seuils_re2020 import Projet, alertes, calculer, donnees
from seuils_re2020.export import evolution, libelle_depot, libelle_usage, nombre_fr, recapitulatif, texte_export
from seuils_re2020.variables import (ALTITUDES, CLASSES_INERTIE, EXPOSITIONS_BRUIT, INDICATEURS,
                                     LIBELLES_ALTITUDE, PERIODES_PC, VERSION)

# ─── Paramètres ──────────────────────────────────────────────────────────────
TITRE = "Seuils RE2020"
URL_DEPOT = "https://github.com/Alliages/Seuils-RE2020"
URL_ZONES = "https://alliages.github.io/zones-climatiques-re2020/"
URL_OFFICIEL = "https://rt-re-batiment.developpement-durable.gouv.fr/re2020-r320.html"
URL_WIKIPEDIA = "https://fr.wikipedia.org/wiki/R%C3%A9glementation_environnementale_2020"
USAGE_MAISON, USAGE_LOGEMENT_COLLECTIF = 1, 2
USAGES_LOGEMENT = {USAGE_MAISON, USAGE_LOGEMENT_COLLECTIF}
USAGES_EFFINERGIE = {1, 2, 3, 4, 5}                 # label Effinergie : logements, bureaux, enseignement
ZONES_PAR_DEPT = donnees.zones_par_departement()
DEPARTEMENTS = sorted(ZONES_PAR_DEPT)
AIDES = donnees.aides()
ETAPES = ["1 · Bâtiment", "2 · Permis de construire (PC)", "3 · Contraintes extérieures", "4 · Carbone",
          "5 · Réseau de chaleur et label"]

st.set_page_config(page_title=TITRE, layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


# ─── État : lien (au premier affichage), puis valeurs conservées d'un écran à l'autre ──
etat = st.session_state
if "_initialise" not in etat:
    etat.update(lien.DEFAUTS)
    etat.update(lien.lire(dict(st.query_params)))
    etat["_initialise"] = True
for champ in lien.CHAMPS:                           # empêche Streamlit d'oublier un champ masqué
    etat[champ] = etat.get(champ, lien.DEFAUTS[champ])


def aide(champ):
    return AIDES.get(champ)


def changement_usage():
    """Maison : un logement par défaut (Smoylgt = Sref), comme dans le classeur."""
    if etat["usage_id"] == USAGE_MAISON:
        etat["nb_logements"] = 1.0


# ─── Menu latéral en étapes ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Projet")

    with st.expander(ETAPES[0], expanded=True):
        st.selectbox("Usage", list(donnees.usages()), format_func=libelle_usage, key="usage_id", help=aide("usage"),
                     on_change=changement_usage)
        usage = etat["usage_id"]
        st.selectbox("Département", DEPARTEMENTS, key="departement", help=aide("departement"),
                     format_func=lambda d: f"{d} ({ZONES_PAR_DEPT[d]})")
        st.markdown(f"[Carte des zones climatiques]({URL_ZONES})")
        st.selectbox("Altitude du terrain", ALTITUDES, key="altitude", format_func=lambda a: LIBELLES_ALTITUDE[a][len("altitude "):],
                     help=aide("altitude"))
        unite = "m² SHAB" if usage in USAGES_LOGEMENT else "m² SU"
        st.number_input(f"Surface de référence Sref ({unite})", min_value=1.0, step=10.0, key="sref",
                        help=aide("sref"))
        if usage in USAGES_LOGEMENT:
            st.number_input("Nombre de logements (NL)", min_value=1.0, step=1.0, key="nb_logements",
                            help=aide("nb_logements"))
            st.caption(f"Smoylgt = {nombre_fr(etat['sref'] / etat['nb_logements'], 1)} m²")
        if usage == USAGE_MAISON:
            st.number_input("Combles aménagés de moins de 1,8 m (m²)", min_value=0.0, key="scombles",
                            help=aide("scombles"))
        if usage in USAGES_LOGEMENT:
            st.number_input("Hauteur sous plafond moyenne (m)", min_value=2.0, step=0.05, key="hsp",
                            help=aide("hsp"))
        if usage == USAGE_LOGEMENT_COLLECTIF:
            st.number_input("Surface cumulée d'agrément extérieur (m²)", min_value=0.0, key="sagrement",
                            help=aide("sagrement"))
        if usage != USAGE_MAISON:
            st.checkbox("Immeuble de grande hauteur (IGH)", key="igh", help=aide("igh"))

    with st.expander(ETAPES[1]):
        st.selectbox("Période de dépôt du permis de construire (PC)", PERIODES_PC, key="periode_pc",
                     help=aide("periode_pc"))
        if etat["periode_pc"] == "2025 à 2027":
            st.radio("Permis de construire (PC) déposé à partir du 1er juillet 2026 ?", [True, False],
                     format_func=lambda b: "Oui" if b else "Non", horizontal=True, key="pc_apres_juillet_2026",
                     help=aide("pc_apres_juillet_2026"))

    with st.expander(ETAPES[2]):
        categories = [1, 2, 3] if donnees.usages()[usage]["categorie3_possible"] else [1, 2]
        if etat["categorie"] not in categories:
            etat["categorie"] = 1
        st.selectbox("Catégorie de contraintes extérieures", categories, key="categorie",
                     format_func=lambda c: f"Catégorie {c}", help=aide("categorie"))
        st.selectbox("Exposition au bruit", EXPOSITIONS_BRUIT, key="exposition_bruit", help=aide("exposition_bruit"))
        st.checkbox("Partie de bâtiment climatisée", key="climatise", help=aide("climatise"))

    with st.expander(ETAPES[3]):
        st.caption("kg éq. CO₂/m² — laisser à 0 pour une première estimation")
        st.number_input("Lot 1 – VRD", min_value=0.0, key="iclot1", help=aide("iclot1"))
        st.number_input("Lot 2 – fondations et infrastructure", min_value=0.0, key="iclot2", help=aide("iclot2"))
        st.number_input("Lot 13 – production locale d'électricité", min_value=0.0, key="iclot13", help=aide("iclot13"))
        st.number_input("Données par défaut et forfaits (Icded)", min_value=0.0, key="icded", help=aide("icded"))

    with st.expander(ETAPES[4]):
        st.checkbox("Raccordé à un réseau de chaleur urbain", key="rcu", help=aide("rcu"))
        if not etat["rcu"]:
            etat["rcu_classe"] = False
        st.checkbox("Réseau classé (art. L. 712-1 du code de l'énergie)", key="rcu_classe",
                    disabled=not etat["rcu"], help=aide("rcu_classe"))
        if usage in USAGES_EFFINERGIE:
            st.selectbox("Classe d'inertie (label Effinergie)", CLASSES_INERTIE, key="classe_inertie",
                         help=aide("classe_inertie"))

# ─── Calcul ──────────────────────────────────────────────────────────────────
# les champs masqués pour cet usage reprennent leur valeur neutre (sans effet sur les seuils)
saisies = {champ: etat[champ] for champ in lien.CHAMPS}
NEUTRES = {"nb_logements": usage in USAGES_LOGEMENT, "scombles": usage == USAGE_MAISON,
           "hsp": usage in USAGES_LOGEMENT, "sagrement": usage == USAGE_LOGEMENT_COLLECTIF,
           "igh": usage != USAGE_MAISON, "classe_inertie": usage in USAGES_EFFINERGIE,
           "pc_apres_juillet_2026": saisies["periode_pc"] == "2025 à 2027"}
for champ, visible in NEUTRES.items():
    if not visible:
        saisies[champ] = lien.DEFAUTS[champ] if champ != "nb_logements" else 1.0
projet = Projet(**{k: v for k, v in saisies.items() if k != "departement"},
                zone=ZONES_PAR_DEPT[saisies["departement"]])
resultats = calculer(projet)
evol = evolution(projet)

# lien de sauvegarde : l'adresse de la page suit les saisies
parametres = lien.parametres({k: v for k, v in saisies.items() if NEUTRES.get(k, True)})   # champs visibles seulement
st.query_params.from_dict(parametres)
adresse = lien.adresse(st.context.url, parametres)
export = texte_export(projet, resultats, evol, departement=etat["departement"], lien=adresse)


def ligne_evolution(cle, decimales):
    """« 2028 : 545,5 · 2031 : 460,8 » ou « identique en 2028 et 2031 »."""
    if not evol or not isinstance(resultats[cle].valeur, (int, float)):
        return ""
    valeurs = {jalon: v[cle] for jalon, v in evol.items()}
    if all(v == resultats[cle].valeur for v in valeurs.values()):
        return "identique en " + " et ".join(valeurs)
    return " · ".join(f"{jalon} : {nombre_fr(v, decimales)}" for jalon, v in valeurs.items())


# ─── Page ────────────────────────────────────────────────────────────────────
entete, version = st.columns([4, 1])
entete.markdown(f'<div class="titre-page">{TITRE}</div>', unsafe_allow_html=True)
version.markdown(f'<div style="text-align:right"><span class="version">v{VERSION} · non officiel</span></div>',
                 unsafe_allow_html=True)
st.markdown(f'<div class="barre-recap">{recapitulatif(projet, etat["departement"])}</div>', unsafe_allow_html=True)

principal, cote = st.columns([2.6, 1], gap="large")

with principal:
    depot = libelle_depot(projet)
    st.markdown(f'<div class="bandeau"><b>{depot[0].upper() + depot[1:]}</b></div>', unsafe_allow_html=True)
    for message in alertes(projet):
        st.warning(message)

    for rangee in (INDICATEURS[:3], INDICATEURS[3:]):
        for colonne, (cle, nom, unite, dec, famille) in zip(st.columns(3), rangee):
            colonne.markdown(carte_seuil(nom, nombre_fr(resultats[cle].valeur, dec), unite, famille,
                                         ligne_evolution(cle, dec)), unsafe_allow_html=True)

    with st.container(key="carte_detail"):
        st.markdown('<div class="titre-carte">Détail des modulations</div>', unsafe_allow_html=True)
        for cle, nom, _unite, _dec, _famille in INDICATEURS[:5]:
            r = resultats[cle]
            with st.expander(f"{nom} = {nombre_fr(r.valeur, 2)}"):
                if r.moyen is not None:
                    st.write(f"Valeur moyenne : {nombre_fr(r.moyen, 2)}")
                st.table({"coefficient": list(r.coefficients),
                          "valeur": [nombre_fr(v, 4) for v in r.coefficients.values()]})

with cote:
    with st.container(key="carte_partage"):
        st.markdown('<div class="titre-carte">Sauvegarder par lien</div>', unsafe_allow_html=True)
        st.code(adresse, language=None, wrap_lines=True)
        st.caption("Le lien garde les saisies, pas les résultats : rouvert, il recalcule le projet "
                   "avec la version de l'outil en ligne.")

    with st.container(key="carte_export"):
        st.markdown('<div class="titre-carte">Exporter les valeurs</div>', unsafe_allow_html=True)
        st.download_button("Télécharger (.txt)", data=export, file_name=f"seuils_re2020_{date.today():%Y%m%d}.txt",
                           mime="text/plain", use_container_width=True)
        with st.expander("Copier le texte"):
            st.code(export, language=None)

    if usage in USAGES_EFFINERGIE:
        with st.container(key="carte_effinergie"):
            st.markdown('<div class="titre-carte">Label Effinergie</div>', unsafe_allow_html=True)
            st.write(f"DH Effinergie : **{nombre_fr(resultats['dh_effinergie'].valeur, 0)}** °C.h")
            st.caption("Hors réglementation.")

    with st.container(key="carte_liens"):
        st.markdown('<div class="titre-carte">Pour aller plus loin</div>', unsafe_allow_html=True)
        st.markdown(f"- [Site officiel de la RE2020]({URL_OFFICIEL})\n"
                    f"- [La RE2020 sur Wikipédia]({URL_WIKIPEDIA})\n"
                    f"- [Carte des zones climatiques]({URL_ZONES})\n"
                    f"- [Code source et données]({URL_DEPOT})")

st.caption("Document non officiel, à utiliser avec toutes les vérifications nécessaires · licence GNU GPL v3 · "
           "Guillaume Meunier, d'après l'annexe à l'article R. 172-4 du CCH et ses décrets modificatifs.")
