"""
Contrôles de cohérence des saisies : messages d'alerte, sans bloquer le calcul
(mêmes avertissements que la feuille Input_resultats du classeur).
"""
from . import donnees
from .variables import ALTITUDES, PERIODES_PC, ZONES

# ─── Paramètres ──────────────────────────────────────────────────────────────
USAGES_RE2020_DES_2022 = {1, 2, 3, 4, 5}     # autres usages : PC à partir de 2026 (décret 2026-16)


def alertes(projet):
    """Liste de messages à afficher à côté des résultats."""
    messages = []
    usage = donnees.usages()[projet.usage_id]
    # petite construction : première règle qui vise l'usage (donnees/surfaces_minimales.csv)
    for usages, sref_max, texte in donnees.surfaces_minimales():
        if usages is None or projet.usage_id in usages:
            if projet.sref <= sref_max:
                messages.append(texte)
            break
    if projet.zone not in ZONES or projet.altitude not in ALTITUDES or projet.periode_pc not in PERIODES_PC:
        messages.append("Zone, altitude ou période de dépôt inconnue.")
    if projet.sref <= 0:
        messages.append("La surface de référence doit être positive.")
    if projet.usage_id not in USAGES_RE2020_DES_2022 and projet.periode_pc == "2022 à 2024":
        messages.append("Cet usage n'est soumis à la RE2020 que pour les PC déposés à partir de 2026.")
    if projet.categorie == 3 and not usage["categorie3_possible"]:
        messages.append("La catégorie 3 n'est pas possible pour cet usage.")
    if projet.categorie == 2 and not projet.climatise:
        messages.append("Une partie de bâtiment en catégorie 2 est forcément climatisée.")
    if projet.rcu_classe and not projet.rcu:
        messages.append("Réseau classé coché sans raccordement à un réseau de chaleur.")
    if projet.igh and projet.usage_id == 1:
        messages.append("Une maison individuelle ne peut pas être un IGH.")
    return messages
