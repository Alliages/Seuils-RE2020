"""
Palette et feuille de style de l'interface (cartes arrondies sur fond clair).

Les couleurs de base sont aussi déclarées dans .streamlit/config.toml (thème Streamlit) :
garder les deux fichiers cohérents.
"""
from html import escape

# ─── Palette ─────────────────────────────────────────────────────────────────
ASH_GREY = "#bdbea9"         # bordures, séparateurs
MUTED_TEAL = "#8db38b"       # famille énergie
WISTERIA_BLUE = "#86a5d9"    # familles bioclimatique et confort d'été
GUNMETAL = "#3f4045"         # texte, étape ouverte du menu
BRONZE_SPICE = "#c75000"     # couleur principale, famille carbone, bandeau
FOND = "#efefea"             # Ash Grey éclairci à 25 % : fond de page
BLANC = "#ffffff"

COULEUR_FAMILLE = {"bioclimatique": WISTERIA_BLUE, "confort": WISTERIA_BLUE,
                   "energie": MUTED_TEAL, "carbone": BRONZE_SPICE}
RAYON_CARTE = "20px"
OMBRE = "0 2px 14px rgba(63, 64, 69, 0.08)"
POLICE = "https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600;700&display=swap"

CSS = f"""
<style>
@import url('{POLICE}');
.block-container {{ padding-top: 2.2rem; max-width: 1320px; }}

/* Menu latéral : panneau blanc bien détaché du fond, étape ouverte en Gunmetal */
section[data-testid="stSidebar"] {{ background: {BLANC}; border-right: 2px solid {ASH_GREY}; }}
section[data-testid="stSidebar"] h2 {{ color: {GUNMETAL}; font-weight: 700; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] details {{
    border: 1px solid {ASH_GREY}; border-radius: 16px; background: {BLANC}; overflow: hidden; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
    font-weight: 600; color: {GUNMETAL}; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary {{
    background: {GUNMETAL}; color: {BLANC}; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary * {{ color: {BLANC}; fill: {BLANC}; }}
section[data-testid="stSidebar"] label p {{ color: {GUNMETAL}; font-weight: 500; }}

/* Cartes (conteneurs Streamlit dont la clé commence par « carte ») */
[class*="st-key-carte"] {{ background: {BLANC}; border-radius: {RAYON_CARTE}; padding: 1.2rem 1.4rem;
    box-shadow: {OMBRE}; }}
.titre-carte {{ font-weight: 600; font-size: 1.05rem; color: {GUNMETAL}; margin-bottom: .4rem; }}

/* En-tête */
.titre-page {{ font-size: 2rem; font-weight: 700; color: {GUNMETAL}; line-height: 1.1; }}
.version {{ display: inline-block; background: {BLANC}; border: 1px solid {ASH_GREY}; border-radius: 999px;
    padding: .35rem .9rem; font-size: .85rem; color: {GUNMETAL}; }}
.barre-recap {{ background: {BLANC}; border-radius: 999px; padding: .75rem 1.4rem; box-shadow: {OMBRE};
    color: {GUNMETAL}; margin: .8rem 0 1.2rem 0; }}
.bandeau {{ background: {BRONZE_SPICE}; color: {BLANC}; border-radius: {RAYON_CARTE}; padding: 1.1rem 1.4rem;
    margin-bottom: 1rem; }}
.bandeau b {{ font-size: 1.1rem; }}

/* Cartes de seuils */
.carte-seuil {{ background: {BLANC}; border-radius: {RAYON_CARTE}; padding: 1.1rem 1.3rem 1rem 1.3rem;
    box-shadow: {OMBRE}; margin-bottom: 1rem; border-top: 6px solid var(--famille); min-height: 196px; }}
.carte-seuil .nom {{ font-weight: 600; font-size: .92rem; color: {GUNMETAL}; display: flex;
    align-items: baseline; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.carte-seuil .valeur {{ font-size: 2.1rem; font-weight: 700; color: {GUNMETAL}; margin-top: .3rem; }}
.carte-seuil .unite {{ font-size: .82rem; color: {GUNMETAL}; opacity: .75; }}
.carte-seuil .evol {{ font-size: .8rem; color: {GUNMETAL}; margin-top: .5rem; padding-top: .45rem;
    border-top: 1px solid {FOND}; }}
.pastille {{ display: inline-block; width: .7rem; height: .7rem; border-radius: 50%; background: var(--famille);
    margin-right: .45rem; flex-shrink: 0; }}
</style>
"""


def carte_seuil(nom, valeur, unite, famille, evolution=""):
    """Carte HTML d'un seuil ; le texte est échappé."""
    couleur = COULEUR_FAMILLE[famille]
    evol = f'<div class="evol">{escape(evolution)}</div>' if evolution else ""
    return (f'<div class="carte-seuil" style="--famille:{couleur}">'
            f'<div class="nom"><span class="pastille"></span>{escape(nom)}</div>'
            f'<div class="valeur">{escape(valeur)}</div><div class="unite">{escape(unite)}</div>{evol}</div>')
