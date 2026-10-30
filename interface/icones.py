"""
Icônes de l'interface : Material Symbols Rounded, fournies avec Streamlit (aucune dépendance).

Catalogue : https://fonts.google.com/icons — changer une icône = changer son nom ci-dessous.
Dans un libellé Streamlit : ":material/nom:" ; dans du HTML : span de classe « ico » (voir style.py).
"""
from html import escape

# ─── Icônes par zone de l'interface ──────────────────────────────────────────
MENU = "tune"
ONGLETS = {"neuf": "domain_add", "extension": "add_home_work"}
ETAPES = {"batiment": "apartment", "permis": "description", "contraintes": "noise_aware",
          "carbone": "co2", "reseau": "heat"}
CHAMPS = {"usage": "category", "departement": "location_on", "altitude": "landscape", "sref": "square_foot",
          "nb_logements": "door_front", "scombles": "roofing", "hsp": "height", "sagrement": "balcony",
          "igh": "domain", "periode_pc": "calendar_month", "pc_apres_juillet_2026": "event",
          "categorie": "warning", "exposition_bruit": "volume_up", "climatise": "ac_unit",
          "iclot1": "road", "iclot2": "foundation", "iclot13": "solar_power", "icded": "dataset",
          "rcu": "heat_pump", "rcu_classe": "verified", "classe_inertie": "layers",
          "typologie": "home_work", "sexistant": "home"}
SEUILS = {"bbio_max": "wb_sunny", "cepnr_max": "bolt", "cep_max": "electric_meter",
          "icenergie_max": "co2", "icconstruction_max": "construction", "dh_max": "device_thermostat"}
CARTES = {"detail": "functions", "partage": "link", "export": "download", "effinergie": "eco",
          "liens": "menu_book", "extension": "add_home_work", "regime": "gavel", "cas": "rule"}
LIENS = {"officiel": "account_balance", "wikipedia": "public", "zones": "map", "depot": "code"}
DIVERS = {"bandeau": "event", "recap": "summarize", "telecharger": "file_download", "copier": "content_copy",
          "stable": "trending_flat", "baisse": "trending_down", "hausse": "trending_up", "alerte": "warning",
          "en_cours": "construction", "info": "info"}
COULEUR_LIBELLE = "orange"        # couleur Streamlit « orange » = Bronze Spice (.streamlit/config.toml)


def ico(nom):
    """Icône dans un texte Streamlit (libellé, titre de repliable, onglet, markdown)."""
    return f":material/{nom}:"


def ico_libelle(champ, texte):
    """Libellé de champ précédé de son icône en Bronze Spice."""
    return f":{COULEUR_LIBELLE}[{ico(CHAMPS[champ])}] {texte}"


def ico_html(nom, couleur=None):
    """Icône dans du HTML (cartes, bandeau…) ; la taille suit le texte qui l'entoure."""
    style = f' style="color:{couleur}"' if couleur else ""
    return f'<span class="ico"{style}>{escape(nom)}</span>'
