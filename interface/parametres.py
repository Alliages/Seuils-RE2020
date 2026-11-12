"""
Paramètres de l'interface : titres, adresses, libellés des champs, textes affichés, mise en page.
Changer un texte ou un libellé de l'interface se fait ici, sans toucher à la logique.

Palette et feuille de style : style.py · icônes : icones.py · paramètres du lien : lien.py
Valeurs réglementaires et paramètres du calcul : seuils_re2020/variables.py et donnees/
"""
from seuils_re2020.variables import VERSION

# ─── En-tête et pied de page ─────────────────────────────────────────────────
TITRE = "Les 6 seuils de la RE2020"
TITRE_MENU = "Les paramètres du projet"
LIBELLE_VERSION = f"v{VERSION}"
DATE_VERSION = "12 novembre 2026"                  # date de publication (celle de CHANGELOG.md)
INFOBULLE_VERSION = f"Version {VERSION} publiée le {DATE_VERSION}"     # affichée au survol de la version
PIED_DE_PAGE = ("Document non officiel, à utiliser avec toutes les vérifications nécessaires · licence GNU GPL v3 · "
                "Guillaume Meunier.")

# ─── Adresses ────────────────────────────────────────────────────────────────
URL_DEPOT = "https://github.com/alliages/seuils-re2020"
URL_ZONES = "https://alliages.github.io/zones-climatiques-re2020/"
URL_METEO = "https://vulgarisateurdh.streamlit.app/"
URL_RSEE = "https://alliages.github.io/lecteur_RSEE/"
URL_OFFICIEL = "https://rt-re-batiment.developpement-durable.gouv.fr/re2020-r320.html"
URL_WIKIPEDIA = "https://fr.wikipedia.org/wiki/R%C3%A9glementation_environnementale_2020"
URL_ARTICLE_50_3 = "https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000050146201/2026-07-02"
URL_FICHE_EXTENSION = ("https://rt-re-batiment.developpement-durable.gouv.fr/IMG/pdf/"
                       "20250415_fiche_application_extension_batiment_et_const_inf_50.pdf")

# ─── Menu : étapes et champs ─────────────────────────────────────────────────
ETAPES = {"batiment": "1 · Bâtiment", "permis": "2 · Permis de construire (PC)",
          "contraintes": "3 · Contraintes extérieures", "carbone": "4 · Carbone",
          "reseau": "5 · Réseau de chaleur et label"}
# Libellé de chaque champ ; {unite} est remplacé par l'unité de la Sref (m² SHAB ou m² SU)
LIBELLES = {
    "usage_id": "Usage", "departement": "Département", "altitude": "Altitude du terrain",
    "sref": "Surface de référence Sref ({unite})", "nb_logements": "Nombre de logements (NL)",
    "scombles": "Combles aménagés de moins de 1,8 m (m²)", "hsp": "Hauteur sous plafond moyenne (m)",
    "sagrement": "Surface cumulée d'agrément extérieur (m²)", "igh": "Immeuble de grande hauteur (IGH)",
    "periode_pc": "Période de dépôt du permis de construire (PC)",
    "pc_apres_juillet_2026": "Permis de construire (PC) déposé à partir du 1er juillet 2026 ?",
    "pc_apres_mai_2026": "Permis de construire (PC) déposé à partir du 1er mai 2026 ?",
    "emprise_sup_1000": "Emprise au sol supérieure à 1 000 m²",
    "derogation_gaz": "Dérogation gaz : PC avant le 31/12/2023, gaz prévu par un permis d'aménager ou une ZAC",
    "categorie": "Catégorie de contraintes extérieures", "exposition_bruit": "Exposition au bruit",
    "climatise": "Partie de bâtiment climatisée",
    "iclot1": "Lot 1 – VRD", "iclot2": "Lot 2 – fondations et infrastructure",
    "iclot13": "Lot 13 – production locale d'électricité", "icded": "Données par défaut et forfaits (Icded)",
    "rcu": "Raccordé à un réseau de chaleur urbain", "rcu_classe": "Réseau classé (art. L. 712-1 du code de l'énergie)",
    "classe_inertie": "Classe d'inertie (label Effinergie)",
    # onglet Extension et surélévation
    "typologie": "Type de travaux", "sexistant": "Sref des locaux existants ({unite})",
}
# Infobulles qui remplacent celles du classeur (donnees/aides.csv)
AIDES_REMPLACEES = {"altitude": "Afficher les coordonnées : [cartes.gouv.fr](https://cartes.gouv.fr/explorer-les-cartes/)"}
AIDE_IGH_GRISE = ("Les règles IGH (décret n° 2026-200) ne s'appliquent qu'aux permis de construire déposés "
                  "à partir du 1er juillet 2026 : choisir la date de dépôt à l'étape 2.")
# Usage soumis à la RE2020 seulement depuis le 1er mai 2026 (décret 2026-16) : message rouge, aucun seuil
MESSAGE_HORS_CHAMP = (
    "**Cet usage n'est pas soumis à la RE2020 pour cette date de dépôt.** Le décret n° 2026-16 l'y soumet pour "
    "les permis de construire déposés à partir du 1er mai 2026 : avant, c'est la réglementation antérieure "
    "(RT2012 le plus souvent) qui s'applique. Aucun seuil RE2020 n'est donné.")
# PC 2022-2024 : définition d'Icded de l'annexe avant le décret 2024-1258 (le lot 13 est compté)
AIDE_ICDED_AVANT_RETEX = (
    "PC 2022-2024 (annexe avant le décret n° 2024-1258) : impact des composants évalués avec des données par "
    "défaut ou des valeurs forfaitaires, hors lots 1 et 2 — le lot 13 est compté, sauf pour les bureaux de plus "
    "de 1 000 m² d'emprise au sol (hors lots 1, 2 et 13).")
LIEN_ZONES = "Carte des zones climatiques"
# Autres outils du même auteur, listés dans la carte « Pour aller plus loin » :
# (clé d'icône, libellé, adresse, info-bulle au survol)
TITRE_AUTRES_OUTILS = "Autres outils"
AUTRES_OUTILS = (("meteo", "Météo & Chaleur", URL_METEO, "DH et nuits tropicales d'un fichier météo"),
                 ("rsee", "Lecteur RSEE", URL_RSEE, "Lire un RSEE et le situer par rapport aux seuils"))
RENVOI_TRAVAUX = "Si c'est une extension ou une surélévation, voir l'onglet « Extension et surélévation »"
SREF_RENVOI_TRAVAUX = 200       # renvoi affiché sous la Sref seulement en dessous de cette surface (m²)
TEXTE_SMOYLGT = "Smoylgt = {smoylgt} m²"
TEXTE_AGREMENT = "Soit {taux} % de la SHAB (Sref) — Miagrément_ext s'applique au-delà de {seuil} %"
TEXTE_CARBONE = "kg éq. CO₂/m² — laisser à 0 pour une première estimation"

# ─── Calcul : valeur d'un champ masqué pour l'usage choisi ───────────────────
# Les autres champs masqués reprennent leur valeur par défaut (lien.DEFAUTS), sans effet sur les seuils.
VALEURS_NEUTRES = {"nb_logements": 1}

# ─── Onglet Construction neuve ───────────────────────────────────────────────
ONGLETS = {"neuf": "Construction neuve", "extension": "Extension et surélévation"}
COLONNES_ENTETE = [4, 1]                  # titre, version
COLONNES_NEUF = [2.6, 1]                  # résultats, cartes latérales
TITRES_CARTES = {"detail": "Détail des modulations", "partage": "Sauvegarder par lien",
                 "export": "Exporter les valeurs", "effinergie": "Label Effinergie", "liens": "Pour aller plus loin",
                 "extension": "Le projet de travaux", "cas": "Cas testés, dans l'ordre (le premier vrai l'emporte)"}
TEXTE_LIEN = ("Le lien garde les saisies, pas les résultats : rouvert, il recalcule le projet "
              "avec la version de l'outil en ligne.")
BOUTON_TELECHARGER = "Télécharger (.txt)"
NOM_FICHIER_EXPORT = "seuils_re2020_{jour:%Y%m%d}.txt"
COPIER_TEXTE = "Copier le texte"
TEXTE_EFFINERGIE = "Hors réglementation."
TEXTE_DETAIL_MODULATIONS = "Formules et coefficients de l'{texte}, selon la date de dépôt du PC."

# ─── Onglet Extension et surélévation ────────────────────────────────────────
COLONNES_TYPOLOGIE = [1, 2, 1]            # type de travaux centré
LARGEURS_ENCADRES = [0.4, 4, 0.8, 4, 0.4]  # marge, surface existante, écart, surface des travaux, marge
TEXTE_VALIDER = "Valider avec Entrée ou en touchant ailleurs."   # sur téléphone, la saisie part à la validation
TEXTE_SEUILS_TRAVAUX = ("Seuils calculés avec les paramètres du menu, sur la Sref des travaux. "
                        "Le détail des modulations est dans l'onglet Construction neuve.")
AVERTISSEMENT_TRAVAUX_AVANT_RETEX = (
    "PC déposé en 2022-2024 : les régimes ci-dessous suivent l'article 50-3 de l'arrêté du 4 août 2021 dans sa "
    "version applicable aux PC déposés à partir de 2025. Vérifier le régime en vigueur à la date de dépôt. "
    "Les seuils, eux, suivent l'annexe R.172-4 avant le décret n° 2024-1258.")
MENTION_EXPORT_TRAVAUX ="Cet onglet n'est pas repris dans l'export texte, qui ne couvre que la construction neuve."
TITRE_BORNES = "Lecture des bornes (50 m², 80 m², 150 m², 30 %)"
# Lecture des bornes retenue, validée le 30/10/2026
NOTE_BORNES = (
    "Bornes comprises : de 50 à 80 m² et de 50 à 150 m², 50, 80 et 150 m² inclus. « Moins de 50 m² » s'arrête "
    "avant 50 m². La part de l'existant se compare à 30 % : « moins de 30 % » d'un côté, « 30 % ou plus » de "
    "l'autre. Seule l'extension de maison de 50 à 80 m² est en RE2020 light : une surélévation de maison de "
    "50 m² ou plus, comme une extension de maison de plus de 80 m², relève de la RE2020 complète. "
    "L'arrêté écrit « strictement entre » : l'outil retient les bornes comprises (règles validées le 30/10/2026).")
