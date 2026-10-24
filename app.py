"""
Calculateur de seuils RE2020 — interface Streamlit.

Lancement : streamlit run app.py
Le calcul est fait par le paquet seuils_re2020 ; ce fichier ne gère que la saisie et l'affichage.
"""
import streamlit as st

from seuils_re2020 import Projet, alertes, calculer, decret_2026_applicable
from seuils_re2020 import donnees
from seuils_re2020.variables import (ALTITUDES, CLASSES_INERTIE, EXCEL_REFERENCE, EXPOSITIONS_BRUIT,
                                     PERIODES_PC, VERSION)

# ─── Paramètres d'affichage ──────────────────────────────────────────────────
TITRE = "Calculateur des seuils RE2020"
URL_DEPOT = "https://github.com/Alliages/Seuils-RE2020"
USAGES_LOGEMENT = {1, 2}
USAGE_MAISON = 1
INDICATEURS = [  # (clé, libellé, unité, décimales)
    ("bbio_max", "Bbio_max", "points", 1),
    ("cepnr_max", "Cep,nr_max", "kWhep/m².an", 1),
    ("cep_max", "Cep_max", "kWhep/m².an", 1),
    ("icenergie_max", "Icénergie_max", "kg éq. CO₂/m²", 1),
    ("icconstruction_max", "Icconstruction_max", "kg éq. CO₂/m² (50 ans)", 1),
    ("dh_max", "DH_max", "°C.h", 0),
]
LIBELLES_USAGES = {i: u["detaille"].replace("_", " ").replace("\xa0", " ").strip()
                   for i, u in donnees.usages().items()}
DEPARTEMENTS = sorted(donnees.zones_par_departement())

st.set_page_config(page_title=TITRE, layout="wide")


def afficher(valeur, decimales):
    if isinstance(valeur, (int, float)):
        return f"{valeur:,.{decimales}f}".replace(",", " ")
    return str(valeur)


# ─── Saisie ──────────────────────────────────────────────────────────────────
st.title(TITRE)
st.caption(f"Version {VERSION} · référence : {EXCEL_REFERENCE} · document non officiel, "
           f"à utiliser avec toutes les vérifications nécessaires")

with st.sidebar:
    st.header("Projet")
    usage_id = st.selectbox("Usage", list(LIBELLES_USAGES), format_func=LIBELLES_USAGES.get, index=1)
    departement = st.selectbox("Département", DEPARTEMENTS, index=DEPARTEMENTS.index("Paris"))
    zone = donnees.zones_par_departement()[departement]
    st.write(f"Zone climatique : **{zone}**")
    altitude = st.selectbox("Altitude", ALTITUDES)
    sref = st.number_input("Surface de référence Sref (m²)", min_value=1.0, value=3000.0, step=10.0)
    nb_logements = 1.0
    if usage_id in USAGES_LOGEMENT:
        nb_logements = st.number_input("Nombre de logements (NL)", min_value=1.0, value=50.0, step=1.0)
        st.caption(f"Smoylgt = {sref / nb_logements:.1f} m²")
    scombles = 0.0
    if usage_id == USAGE_MAISON:
        scombles = st.number_input("Combles aménagés < 1,8 m (m²)", min_value=0.0, value=0.0)

    st.header("Dépôt du permis")
    periode = st.selectbox("Période de dépôt", PERIODES_PC, index=1)
    apres_juillet = True
    if periode == "2025 à 2027":
        apres_juillet = st.radio("PC déposé à partir du 01/07/2026 ?", ["Oui", "Non"]) == "Oui"

    st.header("Contraintes")
    categorie = st.selectbox("Catégorie de contraintes extérieures", [1, 2, 3])
    bruit = st.selectbox("Exposition au bruit", EXPOSITIONS_BRUIT)
    climatise = st.checkbox("Climatisé")
    igh = st.checkbox("Immeuble de grande hauteur (IGH)")
    hsp = st.number_input("Hauteur sous plafond moyenne (m)", min_value=2.0, value=2.5, step=0.05)

    st.header("Énergie et réseau de chaleur")
    rcu = st.checkbox("Raccordé à un réseau de chaleur urbain")
    rcu_classe = st.checkbox("Réseau classé", disabled=not rcu) and rcu

    st.header("Carbone")
    iclot1 = st.number_input("Ic lot 1 – VRD (kg éq. CO₂/m²)", min_value=0.0, value=0.0)
    iclot2 = st.number_input("Ic lot 2 – fondations, infrastructure", min_value=0.0, value=0.0)
    iclot13 = st.number_input("Ic lot 13 – photovoltaïque", min_value=0.0, value=0.0)
    icded = st.number_input("Ic données par défaut et forfaits", min_value=0.0, value=0.0)
    sagrement = st.number_input("Surface d'agrément extérieur (m²)", min_value=0.0, value=0.0)

    st.header("Label Effinergie")
    inertie = st.selectbox("Classe d'inertie", CLASSES_INERTIE, index=1)

projet = Projet(usage_id=usage_id, zone=zone, altitude=altitude, sref=sref, periode_pc=periode,
                pc_apres_juillet_2026=apres_juillet, nb_logements=nb_logements, scombles=scombles,
                exposition_bruit=bruit, categorie=categorie, climatise=climatise, rcu=rcu,
                rcu_classe=rcu_classe, igh=igh, sagrement=sagrement, hsp=hsp, iclot1=iclot1,
                iclot2=iclot2, iclot13=iclot13, icded=icded, classe_inertie=inertie)

# ─── Résultats ───────────────────────────────────────────────────────────────
resultats = calculer(projet)
for message in alertes(projet):
    st.warning(message)
st.info("Décret n° 2026-200 (HSP, agrément, Miclim_RCU, IGH) : "
        + ("appliqué." if decret_2026_applicable(projet) else "non appliqué (PC antérieur au 01/07/2026)."))

colonnes = st.columns(3)
for n, (cle, libelle, unite, dec) in enumerate(INDICATEURS):
    colonnes[n % 3].metric(f"{libelle} ({unite})", afficher(resultats[cle].valeur, dec))
st.caption(f"DH Effinergie (label, hors réglementation) : {afficher(resultats['dh_effinergie'].valeur, 0)}")

st.subheader("Détail des coefficients")
for cle, libelle, _unite, _dec in INDICATEURS[:5]:
    r = resultats[cle]
    with st.expander(f"{libelle} = {afficher(r.valeur, 2)}"):
        if r.moyen is not None:
            st.write(f"Valeur moyenne : {afficher(r.moyen, 2)}")
        st.table({"coefficient": list(r.coefficients),
                  "valeur": [afficher(v, 4) for v in r.coefficients.values()]})

st.divider()
st.caption(f"Code source et données : [{URL_DEPOT}]({URL_DEPOT}) · licence GNU GPL v3 · "
           "Guillaume Meunier, d'après l'annexe à l'article R. 172-4 du CCH et ses décrets modificatifs.")
