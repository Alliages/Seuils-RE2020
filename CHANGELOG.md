# Journal des versions

Numérotation : 0.8.x tant que l'outil n'est pas validé, puis 0.9.
Chiffre pair = évolution importante, chiffre impair = correction.

## 0.8.0 — 24 octobre 2026

Refonte complète du dépôt (l'ancienne application reste dans l'historique Git).

- Moteur `seuils_re2020` séparé de l'interface : 28 usages, six seuils et DH Effinergie.
- Toutes les valeurs dans `donnees/`, extraites automatiquement du classeur
  `calcul_seuils_RE2020_NU` v2.2, avec la cellule source de chaque valeur.
- Décret n° 2026-200 appliqué selon la date du PC (avant ou après le 01/07/2026).
- Dérogation RCU classé pour Icénergie_maxmoyen (PC déposés avant fin 2027).
- 10 670 cas de référence calculés par le classeur : écart nul.
- Interface Streamlit : saisie, six seuils, détail des coefficients, alertes.
- Licence GNU GPL v3, intégration continue GitHub Actions.

À faire en 0.8.x : écriture simplifiée des conditions de `regles.csv`, découpage des tables par
texte réglementaire, multi-usages, surélévations, confirmation de l'interprétation IGH 2031.
