"""
Calculateur de seuils RE2020 — interface Streamlit.

Lancement : streamlit run app.py
Le calcul est fait par le paquet seuils_re2020 ; ce fichier gère la saisie, l'affichage,
l'export et la sauvegarde par lien (paramètres d'URL, voir interface/lien.py).
"""
from datetime import date
from html import escape
from types import SimpleNamespace

import streamlit as st

from interface import icones as I
from interface import lien
from interface.textes import NOTE_BORNES
from interface.style import CSS, carte_seuil
from seuils_re2020 import Projet, alertes, calculer, decret_2026_applicable, donnees, regime_travaux
from seuils_re2020.export import (champs_visibles, details, evolution, explication_dh, formules, libelle_departement,
                                  libelle_depot, libelle_usage, nombre_fr, recapitulatif, texte_export)
from seuils_re2020.variables import (ALTITUDES, CLASSES_INERTIE, EXPOSITIONS_BRUIT, INDICATEURS, LIBELLES_ALTITUDE,
                                     NOMS_MOYENS, PERIODES_PC, SEUIL_AGREMENT, TYPOLOGIES_TRAVAUX,
                                     USAGE_LOGEMENT_COLLECTIF, USAGE_MAISON, USAGES_EFFINERGIE, USAGES_LOGEMENT,
                                     VERSION)

# ─── Paramètres ──────────────────────────────────────────────────────────────
TITRE = "Les 6 seuils de la RE2020"
TITRE_MENU = "Les paramètres du projet"
URL_DEPOT = "https://github.com/alliages/seuils-re2020"
URL_ZONES = "https://alliages.github.io/zones-climatiques-re2020/"
URL_OFFICIEL = "https://rt-re-batiment.developpement-durable.gouv.fr/re2020-r320.html"
URL_WIKIPEDIA = "https://fr.wikipedia.org/wiki/R%C3%A9glementation_environnementale_2020"
ZONES_PAR_DEPT = donnees.zones_par_departement()
DEPARTEMENTS = list(donnees.departements())          # dans l'ordre des numéros
# Infobulles : celles du classeur (donnees/aides.csv), sauf celles que l'interface remplace
AIDES = {**donnees.aides(),
         "altitude": "Afficher les coordonnées : [cartes.gouv.fr](https://cartes.gouv.fr/explorer-les-cartes/)"}
ETAPES = {"batiment": "1 · Bâtiment", "permis": "2 · Permis de construire (PC)",
          "contraintes": "3 · Contraintes extérieures", "carbone": "4 · Carbone",
          "reseau": "5 · Réseau de chaleur et label"}
ONGLETS = {"neuf": "Construction neuve", "extension": "Extension et surélévation"}
LARGEURS_ENCADRES = [0.4, 4, 0.8, 4, 0.4]     # marge, surface existante, écart, surface des travaux, marge
RENVOI_TRAVAUX = "Si c'est une extension ou une surélévation, voir l'onglet « Extension et surélévation »"
SREF_RENVOI_TRAVAUX = 200       # renvoi affiché sous la Sref seulement en dessous de cette surface (m²)
AIDE_IGH_GRISE = ("Les règles IGH (décret n° 2026-200) ne s'appliquent qu'aux permis de construire déposés "
                  "à partir du 1er juillet 2026 : choisir la date de dépôt à l'étape 2.")
URL_ARTICLE_50_3 = "https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000050146201/2026-07-02"
URL_FICHE_EXTENSION = ("https://rt-re-batiment.developpement-durable.gouv.fr/IMG/pdf/"
                       "20250415_fiche_application_extension_batiment_et_const_inf_50.pdf")
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
etat["nb_logements"] = int(etat["nb_logements"])    # nombre de logements : entier


def aide(champ):
    return AIDES.get(champ)


def etape(cle, ouverte=False):
    """Étape repliable du menu, avec son icône."""
    return st.expander(f"{I.ico(I.ETAPES[cle])} {ETAPES[cle]}", expanded=ouverte)   # icône dans le titre : garde la flèche


def titre_carte(cle, texte):
    st.markdown(f'<div class="titre-carte">{I.ico_html(I.CARTES[cle])}{texte}</div>', unsafe_allow_html=True)


def changement_usage():
    """Maison : un logement par défaut (Smoylgt = Sref), comme dans le classeur."""
    if etat["usage_id"] == USAGE_MAISON:
        etat["nb_logements"] = 1


# ─── Menu latéral en étapes ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="titre-menu">{I.ico_html(I.MENU)}{TITRE_MENU}</div>', unsafe_allow_html=True)

    with etape("batiment", ouverte=True):
        st.selectbox(I.ico_libelle("usage", "Usage"), list(donnees.usages()), format_func=libelle_usage, key="usage_id", help=aide("usage"),
                     on_change=changement_usage)
        usage = etat["usage_id"]
        st.selectbox(I.ico_libelle("departement", "Département"), DEPARTEMENTS, key="departement", help=aide("departement"),
                     format_func=libelle_departement)
        st.markdown(f'<div class="lien-zones">{I.ico_html(I.LIENS["zones"])}<a href="{URL_ZONES}" target="_blank">'
                    'Carte des zones climatiques</a></div>', unsafe_allow_html=True)
        st.selectbox(I.ico_libelle("altitude", "Altitude du terrain"), ALTITUDES, key="altitude", format_func=lambda a: LIBELLES_ALTITUDE[a][len("altitude "):],
                     help=aide("altitude"))
        unite = "m² SHAB" if usage in USAGES_LOGEMENT else "m² SU"
        st.number_input(I.ico_libelle("sref", f"Surface de référence Sref ({unite})"), min_value=1.0, step=10.0, key="sref",
                        help=aide("sref"))
        if etat["sref"] < SREF_RENVOI_TRAVAUX:
            st.markdown(f'<div class="renvoi-onglet">{I.ico_html(I.DIVERS["alerte"])}{RENVOI_TRAVAUX}</div>',
                        unsafe_allow_html=True)
        if usage in USAGES_LOGEMENT:
            st.number_input(I.ico_libelle("nb_logements", "Nombre de logements (NL)"), min_value=1, step=1, format="%d", key="nb_logements",
                            help=aide("nb_logements"))
            st.caption(f"Smoylgt = {nombre_fr(etat['sref'] / etat['nb_logements'], 1)} m²")
        if usage == USAGE_MAISON:
            st.number_input(I.ico_libelle("scombles", "Combles aménagés de moins de 1,8 m (m²)"), min_value=0.0, key="scombles",
                            help=aide("scombles"))
        if usage in USAGES_LOGEMENT:
            st.number_input(I.ico_libelle("hsp", "Hauteur sous plafond moyenne (m)"), min_value=2.0, step=0.05, key="hsp",
                            help=aide("hsp"))
        if usage == USAGE_LOGEMENT_COLLECTIF:
            st.number_input(I.ico_libelle("sagrement", "Surface cumulée d'agrément extérieur (m²)"), min_value=0.0, key="sagrement",
                            help=aide("sagrement"))
            taux = etat["sagrement"] / etat["sref"]
            st.caption(f"Soit {nombre_fr(100 * taux, 1)} % de la SHAB (Sref) — Miagrément_ext s'applique "
                       f"au-delà de {nombre_fr(100 * SEUIL_AGREMENT, 0)} %")
        if usage != USAGE_MAISON:
            # case IGH active seulement si le décret 2026-200 s'applique (PC déposé à partir du 1er juillet 2026)
            igh_possible = decret_2026_applicable(SimpleNamespace(periode_pc=etat["periode_pc"],
                                                                  pc_apres_juillet_2026=etat["pc_apres_juillet_2026"]))
            if not igh_possible:
                etat["igh"] = False
            st.checkbox(I.ico_libelle("igh", "Immeuble de grande hauteur (IGH)"), key="igh", disabled=not igh_possible,
                        help=aide("igh") if igh_possible else AIDE_IGH_GRISE)

    with etape("permis"):
        st.selectbox(I.ico_libelle("periode_pc", "Période de dépôt du permis de construire (PC)"), PERIODES_PC, key="periode_pc",
                     help=aide("periode_pc"))
        if etat["periode_pc"] == "2025 à 2027":
            st.radio(I.ico_libelle("pc_apres_juillet_2026", "Permis de construire (PC) déposé à partir du 1er juillet 2026 ?"), [True, False],
                     format_func=lambda b: "Oui" if b else "Non", horizontal=True, key="pc_apres_juillet_2026",
                     help=aide("pc_apres_juillet_2026"))

    with etape("contraintes"):
        categories = [1, 2, 3] if donnees.usages()[usage]["categorie3_possible"] else [1, 2]
        if etat["categorie"] not in categories:
            etat["categorie"] = 1
        st.selectbox(I.ico_libelle("categorie", "Catégorie de contraintes extérieures"), categories, key="categorie",
                     format_func=lambda c: f"Catégorie {c}", help=aide("categorie"))
        st.selectbox(I.ico_libelle("exposition_bruit", "Exposition au bruit"), EXPOSITIONS_BRUIT, key="exposition_bruit", help=aide("exposition_bruit"))
        st.checkbox(I.ico_libelle("climatise", "Partie de bâtiment climatisée"), key="climatise", help=aide("climatise"))

    with etape("carbone"):
        st.caption("kg éq. CO₂/m² — laisser à 0 pour une première estimation")
        st.number_input(I.ico_libelle("iclot1", "Lot 1 – VRD"), min_value=0.0, key="iclot1", help=aide("iclot1"))
        st.number_input(I.ico_libelle("iclot2", "Lot 2 – fondations et infrastructure"), min_value=0.0, key="iclot2", help=aide("iclot2"))
        st.number_input(I.ico_libelle("iclot13", "Lot 13 – production locale d'électricité"), min_value=0.0, key="iclot13", help=aide("iclot13"))
        st.number_input(I.ico_libelle("icded", "Données par défaut et forfaits (Icded)"), min_value=0.0, key="icded", help=aide("icded"))

    with etape("reseau"):
        st.checkbox(I.ico_libelle("rcu", "Raccordé à un réseau de chaleur urbain"), key="rcu", help=aide("rcu"))
        if not etat["rcu"]:
            etat["rcu_classe"] = False
        st.checkbox(I.ico_libelle("rcu_classe", "Réseau classé (art. L. 712-1 du code de l'énergie)"), key="rcu_classe",
                    disabled=not etat["rcu"], help=aide("rcu_classe"))
        if usage in USAGES_EFFINERGIE:
            st.selectbox(I.ico_libelle("classe_inertie", "Classe d'inertie (label Effinergie)"), CLASSES_INERTIE, key="classe_inertie",
                         help=aide("classe_inertie"))

# ─── Calcul ──────────────────────────────────────────────────────────────────
# les champs masqués pour cet usage reprennent leur valeur neutre (sans effet sur les seuils)
saisies = {champ: etat[champ] for champ in lien.CHAMPS}
NEUTRES = champs_visibles(usage, saisies["periode_pc"])
for champ, visible in NEUTRES.items():
    if not visible:
        saisies[champ] = lien.DEFAUTS[champ] if champ != "nb_logements" else 1
projet = Projet(**{k: v for k, v in saisies.items() if k != "departement" and k not in lien.CHAMPS_TRAVAUX},
                zone=ZONES_PAR_DEPT[saisies["departement"]])
resultats = calculer(projet)
evol = evolution(projet)

# lien de sauvegarde : l'adresse de la page suit les saisies
parametres = lien.parametres({k: v for k, v in saisies.items() if NEUTRES.get(k, True)})   # champs visibles seulement
st.query_params.from_dict(parametres)
adresse = lien.adresse(st.context.url, parametres)
export = texte_export(projet, resultats, evol, departement=etat["departement"], lien=adresse)


def ligne_evolution(cle, decimales):
    """(« 2028 : 545,5 · 2031 : 460,8 » ou « identique en 2028 et 2031 », icône du sens d'évolution)."""
    actuel = resultats[cle].valeur
    if not evol or not isinstance(actuel, (int, float)):
        return "", None
    valeurs = {jalon: v[cle] for jalon, v in evol.items()}
    if all(v == actuel for v in valeurs.values()):
        return "identique en " + " et ".join(valeurs), I.DIVERS["stable"]
    dernier = list(valeurs.values())[-1]
    sens = I.DIVERS["baisse"] if isinstance(dernier, (int, float)) and dernier < actuel else I.DIVERS["hausse"]
    return " · ".join(f"{jalon} : {nombre_fr(v, decimales)}" for jalon, v in valeurs.items()), sens


# ─── Page ────────────────────────────────────────────────────────────────────
entete, version = st.columns([4, 1])
entete.markdown(f'<div class="titre-page">{TITRE}</div>', unsafe_allow_html=True)
version.markdown(f'<div style="text-align:right"><span class="version">v{VERSION} · non officiel</span></div>',
                 unsafe_allow_html=True)
onglet_neuf, onglet_extension = st.tabs([f"{I.ico(I.ONGLETS['neuf'])} {ONGLETS['neuf']}",
                                        f"{I.ico(I.ONGLETS['extension'])} {ONGLETS['extension']}"])

with onglet_neuf:
    st.markdown(f'<div class="barre-recap">{I.ico_html(I.DIVERS["recap"], "#c75000")}{recapitulatif(projet, etat["departement"])}'
                f'<div class="details-saisies">{details(projet)}</div></div>', unsafe_allow_html=True)

    principal, cote = st.columns([2.6, 1], gap="large")

    with principal:
        depot = libelle_depot(projet)
        st.markdown(f'<div class="bandeau"><b>{I.ico_html(I.DIVERS["bandeau"])}{depot[0].upper() + depot[1:]}</b></div>',
                    unsafe_allow_html=True)
        for message in alertes(projet):
            st.warning(message, icon=I.ico(I.DIVERS["alerte"]))

        for rangee in (INDICATEURS[:3], INDICATEURS[3:]):
            for colonne, (cle, nom, unite, dec, famille) in zip(st.columns(3), rangee):
                texte_evol, sens = ligne_evolution(cle, dec)
                colonne.markdown(carte_seuil(nom, nombre_fr(resultats[cle].valeur, dec), unite, famille, texte_evol,
                                             icone=I.SEUILS[cle], icone_evolution=sens), unsafe_allow_html=True)

        with st.container(key="carte_detail"):
            titre_carte("detail", "Détail des modulations")
            for cle, nom, unite, dec, _famille in INDICATEURS:
                r = resultats[cle]
                symbolique, chiffres = formules(cle, nom, r)
                with st.expander(f"{I.ico(I.SEUILS[cle])} {nom} = {nombre_fr(r.valeur, dec)} {unite}"):
                    st.markdown(f'<div class="formule">{escape(symbolique)}</div>'
                                f'<div class="formule chiffres">{escape(chiffres)}</div>', unsafe_allow_html=True)
                    if r.moyen is not None:
                        st.write(f"{NOMS_MOYENS[cle]} : {nombre_fr(r.moyen, 2)}")
                    if cle == "dh_max" and explication_dh(projet, r.valeur):
                        st.info(explication_dh(projet, r.valeur), icon=I.ico(I.DIVERS["info"]))
                    if r.coefficients:
                        st.table({"modulation": list(r.coefficients),
                                  "valeur": [nombre_fr(v, 4) for v in r.coefficients.values()]})

    with cote:
        with st.container(key="carte_partage"):
            titre_carte("partage", "Sauvegarder par lien")
            st.code(adresse, language=None, wrap_lines=True)
            st.caption("Le lien garde les saisies, pas les résultats : rouvert, il recalcule le projet "
                       "avec la version de l'outil en ligne.")

        with st.container(key="carte_export"):
            titre_carte("export", "Exporter les valeurs")
            st.download_button("Télécharger (.txt)", data=export, file_name=f"seuils_re2020_{date.today():%Y%m%d}.txt",
                               mime="text/plain", use_container_width=True, icon=I.ico(I.DIVERS["telecharger"]))
            with st.expander(f"{I.ico(I.DIVERS['copier'])} Copier le texte"):
                st.code(export, language=None)

        if usage in USAGES_EFFINERGIE:
            with st.container(key="carte_effinergie"):
                titre_carte("effinergie", "Label Effinergie")
                st.write(f"DH Effinergie : **{nombre_fr(resultats['dh_effinergie'].valeur, 0)}** °C.h")
                st.caption("Hors réglementation.")

        with st.container(key="carte_liens"):
            titre_carte("liens", "Pour aller plus loin")
            st.markdown(f"- [{I.ico(I.LIENS['officiel'])} Site officiel de la RE2020]({URL_OFFICIEL})\n"
                        f"- [{I.ico(I.LIENS['wikipedia'])} La RE2020 sur Wikipédia]({URL_WIKIPEDIA})\n"
                        f"- [{I.ico(I.LIENS['zones'])} Carte des zones climatiques]({URL_ZONES})\n"
                        f"- [{I.ico(I.LIENS['depot'])} Code source et données]({URL_DEPOT})")

with onglet_extension:
    # ── Saisies propres à l'onglet ; usage, Sref, zone et climatisation viennent du menu ──
    unite_sref = "m² SHAB" if usage in USAGES_LOGEMENT else "m² SU"
    with st.container(key="carte_extension"):
        # titre, suivi de l'usage et de la zone choisis dans le menu
        st.markdown(f'<div class="titre-carte">{I.ico_html(I.CARTES["extension"])}Le projet de travaux'
                    f'<span class="titre-complement">{escape(libelle_usage(usage))} · zone {projet.zone}</span></div>',
                    unsafe_allow_html=True)
        # type de travaux, centré
        _gauche, milieu, _droite = st.columns([1, 2, 1])
        milieu.radio(I.ico_libelle("typologie", "Type de travaux"), list(TYPOLOGIES_TRAVAUX), key="typologie",
                     format_func=TYPOLOGIES_TRAVAUX.get, horizontal=True, help=aide("typologie"))
        # deux encadrés : surface existante (saisie) et surface des travaux (rappel du menu)
        _m1, case_existant, _m2, case_travaux, _m3 = st.columns(LARGEURS_ENCADRES)
        with case_existant.container(key="encadre_existant"):
            st.number_input(I.ico_libelle("sexistant", f"Sref des locaux existants ({unite_sref})"), min_value=1.0,
                            step=10.0, key="sexistant", help=aide("sexistant"))
        regime = regime_travaux(usage, etat["typologie"], projet.sref, etat["sexistant"], projet.zone,
                                projet.climatise)
        with case_travaux.container(key="encadre_travaux"):
            st.markdown(f'<div class="rappel-travaux">Surface des travaux (Sref du menu) :<br>'
                        f'<span class="valeur-travaux">{nombre_fr(projet.sref, 0)} {unite_sref}</span>'
                        f'<div class="part-existant">Part de l\'existant : <b>{nombre_fr(100 * regime.part, 1)} %</b>'
                        f'</div></div>', unsafe_allow_html=True)

    # ── Régime retenu : bandeau de la couleur du régime, avec une flèche dans la marge ──
    st.markdown(f'<div class="bandeau bandeau-regime regime-{regime.cle}"><b>{I.ico_html(I.CARTES["regime"])}'
                f'{escape(regime.libelle)}</b><div class="sous-bandeau">{escape(regime.cas)}</div></div>',
                unsafe_allow_html=True)
    st.write(regime.texte)
    st.caption(f"{regime.source} · cas : {regime.source_cas}")

    # ── Seuils exigés : mêmes valeurs que l'onglet Construction neuve, calculées sur la Sref des travaux ──
    exiges = [ind for ind in INDICATEURS if ind[0] in regime.indicateurs]
    for debut in range(0, len(exiges), 3):
        for colonne, (cle, nom, unite_ind, dec, famille) in zip(st.columns(3), exiges[debut:debut + 3]):
            valeur = regime.dh_max if cle == "dh_max" and regime.dh_max is not None else resultats[cle].valeur
            colonne.markdown(carte_seuil(nom, nombre_fr(valeur, dec), unite_ind, famille, icone=I.SEUILS[cle]),
                             unsafe_allow_html=True)
    if regime.texte_dh:
        st.info(regime.texte_dh, icon=I.ico(I.DIVERS["info"]))
    if exiges:
        st.caption("Seuils calculés avec les paramètres du menu, sur la Sref des travaux. "
                   "Le détail des modulations est dans l'onglet Construction neuve.")

    # ── Justification : cas testés dans l'ordre, lecture des bornes, textes ──
    with st.container(key="carte_cas"):
        titre_carte("cas", "Cas testés, dans l'ordre (le premier vrai l'emporte)")
        st.table({"cas": [c for _o, c, _r, _v in regime.cas_testes],
                  "régime": [r for _o, _c, r, _v in regime.cas_testes],
                  "retenu": ["oui" if v else "" for _o, _c, _r, v in regime.cas_testes]})
        with st.expander(f"{I.ico(I.DIVERS['alerte'])} Lecture des bornes (50 m², 80 m², 150 m², 30 %)"):
            st.write(NOTE_BORNES)
        st.markdown(f"- [{I.ico(I.LIENS['officiel'])} Article 50-3 de l'arrêté du 4 août 2021]({URL_ARTICLE_50_3})\n"
                    f"- [{I.ico(I.LIENS['officiel'])} Fiche d'application DHUP « extension et construction "
                    f"< 50 m² »]({URL_FICHE_EXTENSION})")

st.caption("Document non officiel, à utiliser avec toutes les vérifications nécessaires · licence GNU GPL v3 · "
           "Guillaume Meunier.")
