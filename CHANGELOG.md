# Journal des versions

Numérotation : 0.8.x tant que l'outil n'est pas validé, puis 0.9.
Chiffre pair = évolution importante, chiffre impair = correction.

## 0.8.2 — 28 octobre 2026

Interface (évolution importante).

- Mise en page en cartes arrondies sur fond clair, palette Ash Grey, Muted Teal, Wisteria Blue,
  Gunmetal et Bronze Spice ; police Work Sans.
- Menu ouvert par défaut, en 5 étapes repliables, plus contrasté (étape ouverte en Gunmetal) ;
  seuls les champs utiles à l'usage s'affichent ; catégorie 3 proposée seulement si l'usage le permet.
- Infobulle sur chaque champ : colonne I de l'onglet de saisie du classeur, complétée par les
  définitions de l'annexe (`donnees/aides_complements.csv`).
- Département affiché avec sa zone, par exemple « Paris (H1a) » ; lien vers la carte des zones.
- « Catégorie 1 » au lieu de « 1 » ; « permis de construire (PC) » au lieu de « PC ».
- Date de dépôt du permis de construire affichée à la place du message sur le décret 2026-200.
- Évolution de chaque seuil aux jalons 2028 et 2031, en petit sous la valeur.
- Sauvegarde par lien (saisies dans l'adresse de la page) et export texte (fichier ou copie),
  seuils puis modulations.
- Liens vers le site officiel de la RE2020 et la page Wikipédia.
- Mention « référence : calcul_seuils_RE2020_NU v2.2 » retirée de l'en-tête.
- README réécrit : commandes Windows sans activation de l'environnement.

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

## À faire

- Surélévations et extensions (méthode applicable selon les surfaces : solution à venir).
- Valeurs OPEE : situer le projet par rapport aux bâtiments réels pour montrer la difficulté à
  atteindre chaque seuil.
- Écriture simplifiée des conditions de `regles.csv` ; découpage des tables par texte réglementaire.
- Calcul multi-usages au prorata des Sref.
- Confirmer l'interprétation IGH 2031.
