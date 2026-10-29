"""
Récapitulatif du projet, évolution des seuils aux jalons 2028 et 2031, export en texte.

Module sans dépendance à Streamlit : utilisable en ligne de commande ou par une autre interface.
"""
from dataclasses import replace
from datetime import date

from . import donnees
from .calculs import calculer
from .variables import (INDICATEURS, JALONS_FUTURS, LIBELLES_ALTITUDE, NOMS_MOYENS, PERIODES_PC, SEUIL_AGREMENT,
                        TERMES_ADDITIFS, USAGE_LOGEMENT_COLLECTIF, USAGE_MAISON, USAGES_EFFINERGIE,
                        USAGES_LOGEMENT, VERSION)

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


def libelle_departement(nom):
    """« 75 – Paris (H1a) » : numéro, nom, zone climatique."""
    numero, zone = donnees.departements()[nom]
    return f"{numero} – {nom} ({zone})"


def coef_fr(valeur, decimales=4):
    """Coefficient compact et signé pour une formule : « + 0,1 », « − 0,0595 », « + 0 »."""
    absolu = f"{abs(valeur):.{decimales}f}".rstrip("0").rstrip(".").replace(".", ",") or "0"
    return f"{'−' if valeur < 0 and absolu != '0' else '+'} {absolu}"


def libelle_depot(projet):
    """Date de dépôt du permis de construire, en clair."""
    texte = f"permis de construire (PC) déposé : {projet.periode_pc}"
    if projet.periode_pc == "2025 à 2027":
        texte += ", à partir du 1er juillet 2026" if projet.pc_apres_juillet_2026 else ", avant le 1er juillet 2026"
    return texte


def champs_visibles(usage_id, periode_pc):
    """Champs de saisie utiles pour cet usage (les autres sont sans effet sur les seuils)."""
    return {"nb_logements": usage_id in USAGES_LOGEMENT, "scombles": usage_id == USAGE_MAISON,
            "hsp": usage_id in USAGES_LOGEMENT, "sagrement": usage_id == USAGE_LOGEMENT_COLLECTIF,
            "igh": usage_id != USAGE_MAISON, "classe_inertie": usage_id in USAGES_EFFINERGIE,
            "pc_apres_juillet_2026": periode_pc == "2025 à 2027"}


def taux_agrement(projet):
    return projet.sagrement / projet.sref if projet.sref else 0.0


def recapitulatif(projet, departement=None):
    """Une ligne qui résume les saisies principales."""
    morceaux = [libelle_usage(projet.usage_id),
                libelle_departement(departement) if departement else projet.zone,
                LIBELLES_ALTITUDE[projet.altitude], f"Sref {nombre_fr(projet.sref, 0)} m²"]
    if projet.usage_id in USAGES_LOGEMENT:
        morceaux.append(f"{nombre_fr(projet.nb_logements, 0)} logements "
                        f"(Smoylgt {nombre_fr(projet.sref / projet.nb_logements, 1)} m²)")
    morceaux.append(f"Catégorie {projet.categorie}")
    return " · ".join(morceaux)


def details(projet):
    """Toutes les autres saisies utiles, sur une ligne (affichée en petit sous le récapitulatif)."""
    visible = champs_visibles(projet.usage_id, projet.periode_pc)
    oui_non = lambda b: "oui" if b else "non"
    morceaux = [libelle_depot(projet)[0].upper() + libelle_depot(projet)[1:],
                f"bruit {projet.exposition_bruit}", f"climatisé : {oui_non(projet.climatise)}"]
    if visible["igh"]:
        morceaux.append(f"IGH : {oui_non(projet.igh)}")
    if visible["scombles"]:
        morceaux.append(f"combles {nombre_fr(projet.scombles, 0)} m²")
    if visible["hsp"]:
        morceaux.append(f"HSP {nombre_fr(projet.hsp, 2)} m")
    if visible["sagrement"]:
        morceaux.append(f"agrément {nombre_fr(projet.sagrement, 0)} m² ({nombre_fr(100 * taux_agrement(projet), 1)} % de la SHAB)")
    reseau = "non" if not projet.rcu else ("oui, classé" if projet.rcu_classe else "oui, non classé")
    morceaux.append(f"réseau de chaleur : {reseau}")
    morceaux.append(f"carbone (kg éq. CO₂/m²) : lot 1 = {nombre_fr(projet.iclot1, 0)}, lot 2 = {nombre_fr(projet.iclot2, 0)}, "
                    f"lot 13 = {nombre_fr(projet.iclot13, 0)}, données par défaut = {nombre_fr(projet.icded, 0)}")
    if visible["classe_inertie"]:
        morceaux.append(f"inertie {projet.classe_inertie.lower()}")
    return " · ".join(morceaux)


# ─── Formules ────────────────────────────────────────────────────────────────
def formules(cle, nom, resultat):
    """(formule avec les noms des modulations, même formule avec les valeurs)."""
    moyen = NOMS_MOYENS[cle]
    if not resultat.coefficients:                              # DH_max = DH_maxcat
        return f"{nom} = {moyen}", f"{nom} = {nombre_fr(resultat.valeur, 0)}"
    mult = [k for k in resultat.coefficients if k not in TERMES_ADDITIFS]
    add = [k for k in resultat.coefficients if k in TERMES_ADDITIFS]
    symbolique = f"{nom} = {moyen} × (1 + " + " + ".join(mult) + ")" + "".join(f" + {k}" for k in add)
    if not isinstance(resultat.valeur, (int, float)):
        return symbolique, f"{nom} : {resultat.valeur}"
    chiffres = (f"{nom} = {nombre_fr(resultat.moyen, 2)} × (1 "
                + " ".join(coef_fr(resultat.coefficients[k]) for k in mult) + ")"
                + "".join(f" {coef_fr(resultat.coefficients[k], 2)}" for k in add)
                + f" = {nombre_fr(resultat.valeur, 2)}   (coefficients arrondis)")
    return symbolique, chiffres


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
    lignes = [
        f"Seuils RE2020 — outil Seuils-RE2020 v{VERSION} — {jour:%d/%m/%Y}",
        "",
        "PROJET",
        recapitulatif(projet, departement),
        details(projet),
        "",
        "SEUILS",
    ]
    for cle, libelle, unite, dec, _famille in INDICATEURS:
        ligne = f"{libelle:<{LARGEUR_LIBELLE}}{nombre_fr(resultats[cle].valeur, dec)} {unite}"
        if evol:
            ligne += "   (" + " ; ".join(f"{j} : {nombre_fr(v[cle], dec)}" for j, v in evol.items()) + ")"
        lignes.append(ligne)
    lignes.append(f"{'DH Effinergie':<{LARGEUR_LIBELLE}}{nombre_fr(resultats['dh_effinergie'].valeur, 0)} °C.h (label)")
    lignes += ["", "FORMULES ET MODULATIONS"]
    for cle, libelle, _unite, _dec, _famille in INDICATEURS:
        r = resultats[cle]
        lignes += [""] + list(formules(cle, libelle, r))
        if r.coefficients:
            lignes.append(f"    {NOMS_MOYENS[cle]:<24}{nombre_fr(r.moyen, 2)}")
            lignes += [f"    {nom:<24}{nombre_fr(v, 4)}" for nom, v in r.coefficients.items()]
    lignes += ["", AVERTISSEMENT]
    if lien:
        lignes.append(f"Lien du projet : {lien}")
    return "\n".join(lignes) + "\n"
