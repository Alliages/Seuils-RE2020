"""
Récapitulatif du projet, évolution des seuils aux jalons 2028 et 2031, export en texte.

Module sans dépendance à Streamlit : utilisable en ligne de commande ou par une autre interface.
"""
from dataclasses import replace
from datetime import date

from . import donnees
from .calculs import calculer
from .variables import INDICATEURS, JALONS_FUTURS, LIBELLES_ALTITUDE, PERIODES_PC, VERSION

# ─── Paramètres ──────────────────────────────────────────────────────────────
ESPACE_MILLIERS = " "          # espace fine insécable, typographie française
AVERTISSEMENT = "Document non officiel, à utiliser avec toutes les vérifications nécessaires."
LARGEUR_LIBELLE = 20


# ─── Mise en forme ───────────────────────────────────────────────────────────
def nombre_fr(valeur, decimales=1):
    """12345.678 -> '12 345,7' ; les textes (« non applicable »…) passent tels quels."""
    if not isinstance(valeur, (int, float)):
        return str(valeur)
    texte = f"{valeur:,.{decimales}f}"
    return texte.replace(",", ESPACE_MILLIERS).replace(".", ",")


def libelle_usage(usage_id):
    return donnees.usages()[usage_id]["detaille"].replace("_", " ").replace("\xa0", " ").strip()


def libelle_depot(projet):
    """Date de dépôt du permis de construire, en clair."""
    texte = f"permis de construire (PC) déposé : {projet.periode_pc}"
    if projet.periode_pc == "2025 à 2027":
        texte += ", à partir du 1er juillet 2026" if projet.pc_apres_juillet_2026 else ", avant le 1er juillet 2026"
    return texte


def recapitulatif(projet, departement=None):
    """Une ligne qui résume les saisies principales."""
    morceaux = [libelle_usage(projet.usage_id),
                f"{departement} ({projet.zone})" if departement else projet.zone,
                LIBELLES_ALTITUDE[projet.altitude], f"Sref {nombre_fr(projet.sref, 0)} m²"]
    if projet.usage_id == 2:
        morceaux.append(f"{nombre_fr(projet.nb_logements, 0)} logements "
                        f"(Smoylgt {nombre_fr(projet.sref / projet.nb_logements, 1)} m²)")
    morceaux.append(f"Catégorie {projet.categorie}")
    return " · ".join(morceaux)


# ─── Évolution aux jalons ────────────────────────────────────────────────────
def evolution(projet):
    """{'2028': {indicateur: valeur}, '2031': {…}} pour les jalons postérieurs à la période saisie."""
    rang = PERIODES_PC.index(projet.periode_pc)
    sortie = {}
    for jalon, periode in JALONS_FUTURS.items():
        if PERIODES_PC.index(periode) > rang:
            futur = calculer(replace(projet, periode_pc=periode, pc_apres_juillet_2026=True))
            sortie[jalon] = {cle: futur[cle].valeur for cle, *_ in INDICATEURS}
    return sortie


# ─── Export texte ────────────────────────────────────────────────────────────
def texte_export(projet, resultats, evol=None, departement=None, lien=None, jour=None):
    """Texte à copier ou à enregistrer : seuils, puis modulations, puis lien."""
    jour = jour or date.today()
    oui_non = lambda b: "oui" if b else "non"
    lignes = [
        f"Seuils RE2020 — outil Seuils-RE2020 v{VERSION} — {jour:%d/%m/%Y}",
        "",
        "PROJET",
        recapitulatif(projet, departement),
        libelle_depot(projet)[0].upper() + libelle_depot(projet)[1:],
        f"Bruit {projet.exposition_bruit} · climatisé : {oui_non(projet.climatise)} · IGH : {oui_non(projet.igh)}"
        f" · réseau de chaleur : {oui_non(projet.rcu)} (classé : {oui_non(projet.rcu_classe)})",
        f"Carbone (kg éq. CO₂/m²) : lot 1 = {nombre_fr(projet.iclot1)} ; lot 2 = {nombre_fr(projet.iclot2)} ; "
        f"lot 13 = {nombre_fr(projet.iclot13)} ; données par défaut = {nombre_fr(projet.icded)}",
        "",
        "SEUILS",
    ]
    for cle, libelle, unite, dec, _famille in INDICATEURS:
        ligne = f"{libelle:<{LARGEUR_LIBELLE}}{nombre_fr(resultats[cle].valeur, dec)} {unite}"
        if evol:
            ligne += "   (" + " ; ".join(f"{j} : {nombre_fr(v[cle], dec)}" for j, v in evol.items()) + ")"
        lignes.append(ligne)
    lignes.append(f"{'DH Effinergie':<{LARGEUR_LIBELLE}}{nombre_fr(resultats['dh_effinergie'].valeur, 0)} °C.h (label)")
    lignes += ["", "MODULATIONS"]
    for cle, libelle, _unite, dec, _famille in INDICATEURS:
        r = resultats[cle]
        if not r.coefficients:
            continue
        lignes.append(f"{libelle} = {nombre_fr(r.valeur, 2)} — valeur moyenne {nombre_fr(r.moyen, 2)}")
        lignes += [f"    {nom:<16}{nombre_fr(v, 4)}" for nom, v in r.coefficients.items()]
    lignes += ["", AVERTISSEMENT]
    if lien:
        lignes.append(f"Lien du projet : {lien}")
    return "\n".join(lignes) + "\n"
