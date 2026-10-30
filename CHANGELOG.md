# Journal des versions

Numérotation : 0.8.x et 0.9.x tant que l'outil n'était pas validé, puis 1.0.0 (version initiale).
Chiffre pair = évolution importante, chiffre impair = correction.

## 1.0.0 — 30 octobre 2026

Version initiale : calcul des six seuils en construction neuve et onglet « Extension et surélévation ».
Réunit les versions de travail 0.9.0-beta à 0.9.9, jamais publiées séparément.

- DH_max porté à 1 400 °C.h pour les seules surélévations climatisées de maison de 50 à 80 m² en
  zone H2d ou H3 (bornes comprises, régime RE2020 complète) ; les autres surélévations gardent le
  DH_max calculé (remplace la règle de 0.9.8).
- IGH : case active seulement pour un permis de construire déposé à partir du 1er juillet 2026
  (décret n° 2026-200), sinon grisée et décochée ; à partir de 2031, Icconstruction_maxmoyen =
  95 % de la valeur 2028 standard (lecture du classeur, validée).
- README repris de la version relue par l'auteur ; adresse du dépôt en minuscules
  (github.com/alliages/seuils-re2020).
- Tests : 72. Correctif : les tests GitHub Actions échouaient depuis 0.8.5 (`pytest` ne trouvait pas
  `seuils_re2020`) ; `pytest.ini` ajoute le dossier du projet au chemin de Python.

## 0.9.9 — 30 octobre 2026

Retouches d'interface.

- Menu : renvoi « Si c'est une extension ou une surélévation… » affiché seulement pour une Sref de
  moins de 200 m² ; lien « Carte des zones climatiques » en plus petit, sur une ligne.
- Infobulle de l'altitude : « Afficher les coordonnées : cartes.gouv.fr » (remplace le lien
  Géoportail du classeur).
- Détail des modulations : « (exigence pour un bâtiment moyen) » retiré ; pour DH_max au-dessus de
  1 250 °C.h, explication (catégorie 2, partie climatisée en zone H2d ou H3, Smoylgt du collectif).
- Onglet Extension et surélévation : champ « Sref des locaux existants » sur le même fond que les
  champs du menu ; libellé à la taille de « Surface des travaux » ; infobulles simplifiées.
- Pied de page : mention « d'après l'annexe à l'article R. 172-4 du CCH… » retirée.
- Tests : 71.

## 0.9.8 — 30 octobre 2026

Règles « Extension et surélévation » validées par l'auteur (remplacent la lecture des bornes de 0.9.0-beta).

- Ordre des cas (le premier vrai l'emporte) :
  1. tertiaire spécifique, industrie ou artisanat (usages 6 à 28), moins de 50 m² : RT2012 ;
  2. idem, de 50 à 150 m² et moins de 30 % de l'existant, extension ou surélévation : RT2012 ;
  3. moins de 50 m² : exigences de moyens ;
  4. extension de maison de 50 à 80 m² : RE2020 light ;
  5. hors maison, de 50 à 150 m² et moins de 30 %, extension ou surélévation : exigences de moyens ;
  6. surélévation hors maison, de 50 à 150 m² et 30 % ou plus : RE2020 light ;
  7. surélévation hors maison, plus de 150 m² et moins de 30 % : RE2020 light ;
  8. tous les autres cas : RE2020 complète (dont toute surélévation de maison de 50 m² ou plus
     et toute extension de maison de plus de 80 m²).
- Bornes comprises (50, 80, 150 m²) ; « moins de 50 m² » strict ; 30 % pile = « 30 % ou plus ».
- Nouveau régime RT2012 (bandeau Gunmetal, aucun seuil RE2020 affiché), d'après le guide RE2020
  du CEREMA, version septembre 2026.
- DH_max porté à 1 400 °C.h pour les surélévations climatisées en RE2020 light, en zone H2d ou H3
  (toutes typologies hors maison).
- Alerte « petite surface » de l'onglet Construction neuve : moins de 50 m² (et non 50 m² ou
  moins), message RT2012 pour le tertiaire spécifique, l'industrie et l'artisanat.
- README : organigramme de l'outil aux couleurs de l'application (Mermaid), tableau des règles
  dans la partie utilisateurs, remerciements.
- Correctif : sources contenant un « ; » non protégé (séparateur CSV), tronquées à la lecture, dans
  `surfaces_minimales.csv`, `travaux_*.csv` et `aides_complements.csv` ; nouveau test du nombre de
  champs de chaque table (`tests/test_donnees.py`).
- Infobulle « Type de travaux » alignée sur les règles validées.
- Tests : 69 (dont 27 sur les extensions et surélévations et 19 sur le format des tables).

## 0.9.1 — 30 octobre 2026

Mise en page de l'onglet « Extension et surélévation » d'après la maquette du 30 octobre 2026.

- Titre de la carte suivi de l'usage et de la zone (« Logement collectif · zone H1a »).
- Type de travaux centré, en plus grand.
- Deux encadrés côte à côte : Sref des locaux existants (saisie) ; surface des travaux (Sref du
  menu) en pastille, avec la part de l'existant en dessous.
- Bandeau du régime coloré : exigences de moyens en Bronze Spice, RE2020 light en Muted Teal,
  RE2020 complète en bleu nuit ; flèche dans la marge pour le désigner.
- Menu : sous la Sref, renvoi « Si c'est une extension ou une surélévation, voir l'onglet
  « Extension et surélévation » ».
- README : onglet décrit dans le mode d'emploi, paramètres `travaux` et `sexist` dans la table
  des liens.

## 0.9.0-beta — 29 octobre 2026

Onglet « Extension et surélévation » (évolution importante, passage en 0.9 bêta).

- Régime applicable selon l'arrêté du 4 août 2021, art. 50-3, dans sa version au 1er juillet 2026
  (arrêté du 18 mars 2026) : RE2020 complète, RE2020 light (Bbio_max, Icconstruction_max, DH_max)
  ou exigences de moyens.
- Saisies de l'onglet : type de travaux et Sref des locaux existants. Usage, Sref des travaux, zone
  et climatisation viennent du menu. Les deux saisies sont gardées dans le lien de sauvegarde
  (`travaux`, `sexist`).
- Seuils exigés affichés en cartes, calculés sur la Sref des travaux ; DH_max porté à 1 400 °C.h
  pour une surélévation climatisée de maison en H2d ou H3.
- Tableau des cas testés (le premier vrai l'emporte), sources de chaque cas, liens vers l'article
  50-3 et la fiche DHUP.
- Règles dans `donnees/travaux_cas.csv`, `travaux_regimes.csv` et `travaux_dh.csv` (conditions
  évaluées comme `regles.csv`) ; moteur `seuils_re2020/travaux.py` ; 19 tests (`tests/test_travaux.py`).
- Lecture des bornes, différente du classeur v2.2 (à valider) :
  - 50, 80 et 150 m² exclus des intervalles (« strictement entre » dans l'arrêté) ;
  - 50 m² pile et 30 % pile en exigences de moyens, comme la fiche DHUP du 15/04/2025
    (« SREF ≤ 50 m² », « ≤ 30 % ») ; le classeur met 30 % pile en RE2020 light ;
  - surélévation de maison de plus de 50 et moins de 80 m² en RE2020 light (la fiche DHUP range la
    surélévation parmi les extensions) ; le classeur la met en RE2020 complète ;
  - DH_max à 1 400 °C.h réservé aux maisons (arrêté du 18 mars 2026).
- Correctif d'affichage : pastille de version sur une seule ligne.

## 0.8.7 — 29 octobre 2026

- README : section « Faire un lien vers l'outil (usage externe) » (paramètres de l'adresse, valeurs admises, défauts).

## 0.8.6 — 29 octobre 2026

- README réécrit en deux parties : une première partie pour tout public (lien, capture d'écran, mode d'emploi
  en quatre étapes, sauvegarde et export), une seconde pour le code, sa vérification et les fichiers à relire.
- Capture d'écran de l'outil dans `docs/capture-accueil.png`.

## 0.8.5 — 29 octobre 2026

- Icônes Material Symbols (fournies avec Streamlit) : étapes du menu, champs (en Bronze Spice), cartes de
  seuils, sens de l'évolution 2028/2031, cartes de droite, liens, bandeau. Liste dans `interface/icones.py`.
- Deux onglets : « Construction neuve » et « Extension et surélévation » (en préparation).
- Alerte « petite surface » : construction de 50 m² ou moins = exigences de moyens et non RE2020 complète
  (arrêté du 4 août 2021, art. 50-3, I pour les maisons, III pour les autres usages) ; seuils dans
  `donnees/surfaces_minimales.csv`.
- Accord « 1 logement » dans le récapitulatif.

## 0.8.4 — 29 octobre 2026

Interface d'après la maquette (évolution importante).

- Titre « Les 6 seuils de la RE2020 » en Archivo Black ; bandeau de date de dépôt en bleu nuit.
- Menu sur fond dégradé Bronze Spice → bleu nuit, titre « Les paramètres du projet ».
- Cartes de seuils sur fond pastel par famille, bande foncée pour l'évolution 2028/2031 ;
  DH_max en jaune (confort d'été).
- Survol plus marqué : liseré Bronze Spice sur les champs, Ash Grey sur les étapes, cartes surélevées,
  boutons en Bronze Spice.
- Département précédé de son numéro, par exemple « 75 – Paris (H1a) », liste triée par numéro.
- Détail : formule avec les noms des modulations, puis la même formule chiffrée ; DH_max ajouté.
- « Valeur moyenne » remplacé par le nom réglementaire (Bbio_maxmoyen…, exigence pour un bâtiment moyen).
- Sous la surface d'agrément, son pourcentage de la SHAB (Sref).
- Nombre de logements en entier.
- Toutes les saisies utiles affichées en petit sous la ligne de récapitulatif ; même ligne dans l'export.
- Export : formules, puis valeurs des modulations.
- Polices incluses dans le dépôt (static/polices, licence SIL OFL) : l'outil fonctionne hors connexion.
- Alerte « surface d'agrément » retirée (le pourcentage est affiché sous le champ).

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

- Extension et surélévation : régime dans l'export texte.
- Valeurs OPEE : situer le projet par rapport aux bâtiments réels pour montrer la difficulté à
  atteindre chaque seuil.
- Écriture simplifiée des conditions de `regles.csv` ; découpage des tables par texte réglementaire.
- Calcul multi-usages au prorata des Sref.
