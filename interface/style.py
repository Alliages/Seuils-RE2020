"""
Palette et feuille de style de l'interface (maquette du 29/10/2026).

Les couleurs de base sont aussi déclarées dans .streamlit/config.toml (thème Streamlit) :
garder les deux fichiers cohérents.
"""
from html import escape

# ─── Palette ─────────────────────────────────────────────────────────────────
ASH_GREY = "#bdbea9"         # bordures, survol des étapes
MUTED_TEAL = "#8db38b"       # famille énergie
WISTERIA_BLUE = "#86a5d9"    # famille bioclimatique
GUNMETAL = "#3f4045"         # texte courant, étape ouverte, titre du menu
BRONZE_SPICE = "#c75000"     # couleur principale, famille carbone, survol des champs
BLEU_NUIT = "#1f2238"        # titre, bandeau, dégradé du menu (maquette)
JAUNE_ETE = "#ddd486"        # famille confort d'été (DH), ajoutée par la maquette
FOND = "#efefea"             # Ash Grey éclairci : fond de page
FOND_DETAIL = "#dcdcd5"      # carte « Détail des modulations »
BLANC = "#ffffff"

# famille -> (fond clair de la carte, bande foncée et liseré, texte de la bande)
COULEURS_FAMILLE = {
    "bioclimatique": ("#b9cdf6", WISTERIA_BLUE, BLEU_NUIT),
    "energie": ("#c9eec8", MUTED_TEAL, BLEU_NUIT),
    "carbone": ("#ff9a57", BRONZE_SPICE, BLANC),
    "confort": ("#fbf39c", JAUNE_ETE, BLEU_NUIT),
}
RAYON_CARTE = "20px"
OMBRE = "0 2px 14px rgba(31, 34, 56, 0.10)"
OMBRE_SURVOL = "0 8px 24px rgba(31, 34, 56, 0.22)"
DEGRADE_MENU = f"linear-gradient(100deg, {BRONZE_SPICE} 0%, #8a3d1c 22%, {BLEU_NUIT} 62%)"

# Champs de saisie (listes déroulantes, nombres, texte) : survol et focus bien visibles
CHAMPS_SAISIE = ['[data-testid="stSelectbox"] div[data-rac][role="group"]', '[data-testid="stNumberInputContainer"]',
                 '[data-baseweb="select"] > div', '[data-baseweb="input"]']     # 2 derniers : anciennes versions
SURVOL_CHAMPS = ", ".join(f"{c}:hover, {c}:focus-within" for c in CHAMPS_SAISIE)

CSS = f"""
<style>
.block-container {{ padding-top: 2.2rem; max-width: 1400px; }}

/* ── Menu latéral : dégradé Bronze → bleu nuit, étapes en cartes blanches ── */
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {{ background: {DEGRADE_MENU}; }}
.titre-menu {{ display: inline-block; background: {GUNMETAL}; color: {BLANC}; font-weight: 700; font-size: 1rem;
    white-space: nowrap;
    padding: .45rem 1rem; border-radius: 14px; margin: 0 0 1rem 0; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] details {{
    border: none; border-radius: 16px; background: {BLANC}; overflow: hidden; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{ font-weight: 600; color: {GUNMETAL};
    transition: background .15s; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{ background: {ASH_GREY}; color: {BLEU_NUIT}; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary {{ background: {GUNMETAL}; color: {BLANC}; }}
section[data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary * {{ color: {BLANC}; fill: {BLANC}; }}
section[data-testid="stSidebar"] label p {{ color: {GUNMETAL}; font-weight: 500; }}
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"] {{
    background: {ASH_GREY}; border-radius: 50%; color: {BLEU_NUIT}; }}

/* ── Survol : champs, étapes, boutons, cartes ── */
{SURVOL_CHAMPS} {{ border: 2px solid {BRONZE_SPICE} !important; background: {BLANC} !important; }}
[data-testid="stExpander"] summary:hover {{ background: {ASH_GREY}; }}
.stDownloadButton button:hover, .stButton button:hover {{ background: {BRONZE_SPICE}; color: {BLANC};
    border-color: {BRONZE_SPICE}; }}
a:hover {{ color: {BLEU_NUIT} !important; }}

/* ── Cartes (conteneurs Streamlit dont la clé commence par « carte ») ── */
[class*="st-key-carte"] {{ background: {BLANC}; border-radius: {RAYON_CARTE}; padding: 1.2rem 1.4rem;
    box-shadow: {OMBRE}; }}
[class*="st-key-carte_detail"] {{ background: {FOND_DETAIL}; }}
[class*="st-key-carte_detail"] [data-testid="stExpander"] details {{ background: {BLANC}; border-radius: 14px; }}
.titre-carte {{ font-weight: 600; font-size: 1.1rem; color: {BLEU_NUIT}; margin-bottom: .4rem; }}
.formule {{ font-family: monospace; font-size: .85rem; color: {BLEU_NUIT}; line-height: 1.5; }}
.formule.chiffres {{ color: {BRONZE_SPICE}; margin-bottom: .6rem; }}

/* ── En-tête ── */
.titre-page {{ font-family: 'Archivo Black', 'Work Sans', sans-serif; font-size: 3.1rem; color: {BLEU_NUIT};
    line-height: 1.05; letter-spacing: .02em; }}
.version {{ display: inline-block; background: {BLANC}; border: 1px solid {ASH_GREY}; border-radius: 999px;
    padding: .4rem 1rem; font-size: .9rem; color: {GUNMETAL}; }}
.barre-recap {{ background: {BLANC}; border-radius: 28px; padding: .8rem 1.6rem; box-shadow: {OMBRE};
    color: {GUNMETAL}; margin: .8rem 0 1.3rem 0; font-size: 1.05rem; }}
.barre-recap .details-saisies {{ font-size: .8rem; opacity: .8; margin-top: .3rem; line-height: 1.45; }}
.bandeau {{ background: {BLEU_NUIT}; color: {BLANC}; border-radius: {RAYON_CARTE}; padding: 1.2rem 1.6rem;
    margin-bottom: 1rem; font-size: 1.15rem; }}

/* ── Cartes de seuils : fond clair, liseré et bande d'évolution foncés ── */
.carte-seuil {{ background: var(--clair); border-radius: {RAYON_CARTE}; border-top: 7px solid var(--fonce);
    box-shadow: {OMBRE}; margin-bottom: 1rem; overflow: hidden; transition: transform .15s, box-shadow .15s; }}
.carte-seuil:hover {{ transform: translateY(-3px); box-shadow: {OMBRE_SURVOL}; }}
.carte-seuil .haut {{ padding: 1rem 1.3rem .7rem 1.3rem; }}
.carte-seuil .nom {{ font-weight: 600; font-size: .95rem; color: {BLEU_NUIT}; display: flex; align-items: baseline;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.carte-seuil .valeur {{ font-family: 'Archivo Black', 'Work Sans', sans-serif; font-size: 2.2rem; color: {BLEU_NUIT};
    margin-top: .25rem; }}
.carte-seuil .unite {{ font-size: .82rem; color: {BLEU_NUIT}; opacity: .8; }}
.carte-seuil .evol {{ background: var(--fonce); color: var(--texte-bande); font-size: .82rem; font-weight: 500;
    padding: .55rem 1.3rem; min-height: 2.2rem; }}
.pastille {{ display: inline-block; width: .7rem; height: .7rem; border-radius: 50%; background: var(--fonce);
    margin-right: .45rem; flex-shrink: 0; }}
</style>
"""


def carte_seuil(nom, valeur, unite, famille, evolution=""):
    """Carte HTML d'un seuil ; le texte est échappé."""
    clair, fonce, texte = COULEURS_FAMILLE[famille]
    return (f'<div class="carte-seuil" style="--clair:{clair};--fonce:{fonce};--texte-bande:{texte}">'
            f'<div class="haut"><div class="nom"><span class="pastille"></span>{escape(nom)}</div>'
            f'<div class="valeur">{escape(valeur)}</div><div class="unite">{escape(unite)}</div></div>'
            f'<div class="evol">{escape(evolution) or "&nbsp;"}</div></div>')
