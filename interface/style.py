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
# régime des travaux -> (fond du bandeau, texte) ; exigences de moyens en Bronze Spice (maquette)
COULEURS_REGIME = {"complete": (BLEU_NUIT, BLANC), "light": (MUTED_TEAL, BLEU_NUIT), "moyens": (BRONZE_SPICE, BLANC),
                   "rt2012": (GUNMETAL, BLANC)}
RAYON_CARTE = "20px"
OMBRE = "0 2px 14px rgba(31, 34, 56, 0.10)"
OMBRE_SURVOL = "0 8px 24px rgba(31, 34, 56, 0.22)"
DEGRADE_MENU = f"linear-gradient(100deg, {BRONZE_SPICE} 0%, #8a3d1c 22%, {BLEU_NUIT} 62%)"
CSS_REGIMES = "\n".join(f".bandeau.regime-{cle} {{ background: {fond}; color: {texte}; }}"
                         for cle, (fond, texte) in COULEURS_REGIME.items())

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
.ico {{ font-family: 'Material Symbols Rounded'; font-weight: 400; font-style: normal; font-size: 1.25em;
    line-height: 1; vertical-align: -0.22em; margin-right: .4rem; letter-spacing: normal; display: inline-block; }}
.titre-carte .ico {{ color: {BRONZE_SPICE}; }}
.titre-carte {{ font-weight: 600; font-size: 1.1rem; color: {BLEU_NUIT}; margin-bottom: .4rem; }}
.formule {{ font-family: monospace; font-size: .85rem; color: {BLEU_NUIT}; line-height: 1.5; }}
.formule.chiffres {{ color: {BRONZE_SPICE}; margin-bottom: .6rem; }}

/* ── Onglets ── */
[data-testid="stTabs"] button[role="tab"] p {{ font-size: 1.02rem; font-weight: 600; }}
[data-testid="stTabs"] button[role="tab"]:hover p {{ color: {BRONZE_SPICE}; }}

/* ── En-tête ── */
.titre-page {{ font-family: 'Archivo Black', 'Work Sans', sans-serif; font-size: 3.1rem; color: {BLEU_NUIT};
    line-height: 1.05; letter-spacing: .02em; }}
.version {{ display: inline-block; background: {BLANC}; border: 1px solid {ASH_GREY}; border-radius: 999px;
    padding: .4rem 1rem; font-size: .9rem; color: {GUNMETAL}; white-space: nowrap; }}
.barre-recap {{ background: {BLANC}; border-radius: 28px; padding: .8rem 1.6rem; box-shadow: {OMBRE};
    color: {GUNMETAL}; margin: .8rem 0 1.3rem 0; font-size: 1.05rem; }}
.barre-recap .details-saisies {{ font-size: .8rem; opacity: .8; margin-top: .3rem; line-height: 1.45; }}
.bandeau {{ background: {BLEU_NUIT}; color: {BLANC}; border-radius: {RAYON_CARTE}; padding: 1.2rem 1.6rem;
    margin-bottom: 1rem; font-size: 1.15rem; }}
.bandeau .sous-bandeau {{ font-size: .9rem; opacity: .85; margin-top: .3rem; }}

/* ── Onglet Extension et surélévation (maquette du 30/10/2026) ── */
[class*="st-key-carte_extension"] .titre-carte {{ margin-bottom: 1rem; }}
.titre-complement {{ font-weight: 400; font-size: 1rem; color: {GUNMETAL}; margin-left: 1.2rem; }}
.st-key-typologie [data-testid="stWidgetLabel"], .st-key-typologie [role="radiogroup"] {{
    justify-content: center; }}
.st-key-typologie [data-testid="stWidgetLabel"] p {{ font-size: 1.15rem; }}
.st-key-typologie [role="radiogroup"] p {{ font-size: 1.2rem; }}
.st-key-typologie [role="radiogroup"] {{ gap: 1.5rem; }}
[class*="st-key-encadre"] {{ border: 2.5px solid {BLEU_NUIT}; border-radius: 16px; padding: .8rem 1rem 1rem 1rem;
    min-height: 7.2rem; justify-content: center; overflow: visible; }}
[class*="st-key-encadre_existant"] [data-testid="stWidgetLabel"] {{ justify-content: center; }}
/* même taille de libellé que « Surface des travaux » ; champ sur le fond des champs du menu (à remplir) */
[class*="st-key-encadre_existant"] [data-testid="stWidgetLabel"] p {{ font-size: 1.05rem; color: {GUNMETAL};
    white-space: nowrap; }}
[class*="st-key-encadre_existant"] [data-testid="stNumberInputContainer"],
[class*="st-key-encadre_existant"] [data-testid="stNumberInputContainer"] input,
[class*="st-key-encadre_existant"] [data-testid="stNumberInputContainer"] button {{ background: {FOND}; }}
.rappel-travaux {{ text-align: center; color: {GUNMETAL}; font-size: 1.05rem; line-height: 1.6; }}
.valeur-travaux {{ display: inline-block; background: {FOND}; border-radius: 10px; padding: .1rem .9rem;
    font-weight: 700; font-size: 1.15rem; color: {BLEU_NUIT}; margin-top: .2rem; }}
.part-existant {{ font-size: .9rem; opacity: .85; margin-top: .4rem; }}
.bandeau-regime {{ position: relative; }}
.bandeau-regime::before {{ content: ""; position: absolute; left: -4.2rem; top: 50%; transform: translateY(-50%);
    border-style: solid; border-width: 1.6rem 0 1.6rem 2.4rem;
    border-color: transparent transparent transparent {BLEU_NUIT}; }}
@media (max-width: 900px) {{ .bandeau-regime::before {{ display: none; }} }}
{CSS_REGIMES}

/* ── Menu : lien vers la carte des zones, sur une ligne ── */
.lien-zones {{ font-size: .82rem; white-space: nowrap; margin: -.4rem 0 .6rem 0; }}
.lien-zones .ico {{ color: {BRONZE_SPICE}; margin-right: .3rem; }}

/* ── Menu : renvoi vers l'onglet Extension et surélévation, sous la Sref ── */
.renvoi-onglet {{ font-weight: 600; font-size: .9rem; color: {BLEU_NUIT}; line-height: 1.35; margin: -.3rem 0 .9rem 0; }}
.renvoi-onglet .ico {{ color: {BRONZE_SPICE}; }}

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
.carte-seuil .evol {{ background: var(--fonce); color: var(--texte-bande); font-size: .78rem; font-weight: 500;
    padding: .55rem 1.3rem; min-height: 2.2rem; }}
.pastille {{ display: inline-block; width: .7rem; height: .7rem; border-radius: 50%; background: var(--fonce);
    margin-right: .45rem; flex-shrink: 0; }}
</style>
"""


def carte_seuil(nom, valeur, unite, famille, evolution="", icone=None, icone_evolution=None):
    """Carte HTML d'un seuil ; le texte est échappé. Sans icône : pastille de couleur."""
    clair, fonce, texte = COULEURS_FAMILLE[famille]
    couleur_icone = BRONZE_SPICE if famille == "carbone" else BLEU_NUIT
    marque = (f'<span class="ico" style="color:{couleur_icone}">{escape(icone)}</span>' if icone
              else '<span class="pastille"></span>')
    fleche = f'<span class="ico">{escape(icone_evolution)}</span>' if icone_evolution and evolution else ""
    return (f'<div class="carte-seuil" style="--clair:{clair};--fonce:{fonce};--texte-bande:{texte}">'
            f'<div class="haut"><div class="nom">{marque}{escape(nom)}</div>'
            f'<div class="valeur">{escape(valeur)}</div><div class="unite">{escape(unite)}</div></div>'
            f'<div class="evol">{fleche}{escape(evolution) or "&nbsp;"}</div></div>')
