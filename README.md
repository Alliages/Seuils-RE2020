# Seuils RE2020

Calculateur des six seuils réglementaires de la RE2020 — Bbio_max, Cep,nr_max, Cep_max,
Icénergie_max, Icconstruction_max et DH_max — pour les 28 usages de l'annexe à l'article R. 172-4
du code de la construction et de l'habitation (France métropolitaine).

> Document non officiel, à utiliser avec toutes les vérifications nécessaires.

**Version 0.8.4** (version de travail). Le moteur redonne à l'identique le classeur Excel de
référence sur 10 670 cas de test ; l'outil passera en 0.9 après validation en usage réel.

Pour en savoir plus sur la réglementation :
[site officiel de la RE2020](https://rt-re-batiment.developpement-durable.gouv.fr/re2020-r320.html) ·
[la RE2020 sur Wikipédia](https://fr.wikipedia.org/wiki/R%C3%A9glementation_environnementale_2020) ·
[carte des zones climatiques](https://alliages.github.io/zones-climatiques-re2020/)

## Installer et lancer

Il faut Python 3.10 ou plus récent ([python.org](https://www.python.org/downloads/)).
Ouvrir un terminal **dans le dossier `Seuils-RE2020`**, puis :

### Windows (PowerShell ou invite de commandes)

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Si `python` n'est pas reconnu, remplacer le premier `python` par `py`.
Ces commandes n'ont pas besoin d'« activer » l'environnement : `source` n'existe pas sous Windows.

### macOS et Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

L'application s'ouvre dans le navigateur, à l'adresse http://localhost:8501.
Pour l'arrêter : `Ctrl + C` dans le terminal.

## Utiliser l'application

- **Menu en 5 étapes**, à gauche : bâtiment, permis de construire (PC), contraintes extérieures,
  carbone, réseau de chaleur et label. Seuls les champs utiles à l'usage choisi s'affichent.
  Le point d'interrogation à côté de chaque champ donne sa définition.
- **Résultats** : les six seuils, avec leur évolution aux jalons 2028 et 2031, puis le détail :
  formule avec les noms des modulations, même formule chiffrée, valeur de chaque modulation.
  Sous le récapitulatif, en petit, toutes les saisies utiles au calcul.
- **Sauvegarder par lien** : l'adresse de la page contient toutes les saisies. La copier suffit
  à retrouver le projet. Le lien garde les saisies, pas les résultats : rouvert, il recalcule le
  projet avec la version de l'outil en ligne. Rien n'est stocké sur un serveur.
- **Exporter** : un fichier `.txt` ou un texte à copier, avec les seuils puis les formules et les
  modulations.

## Utiliser le moteur sans interface

```python
from seuils_re2020 import Projet, calculer

projet = Projet(usage_id=2, zone="H1a", altitude="<400m", sref=3000,
                periode_pc="2028 à 2030", nb_logements=50)
resultats = calculer(projet)
print(resultats["bbio_max"].valeur, resultats["bbio_max"].coefficients)
```

Les numéros d'usage sont dans `donnees/usages.csv`.

## Organisation

```
app.py                  interface Streamlit
interface/              style (palette) et sauvegarde par lien
seuils_re2020/          moteur de calcul, sans dépendance à Streamlit
  variables.py          paramètres et listes de choix, regroupés en tête
  regles.py             description du projet, date du décret 2026-200, choix des règles
  calculs.py            assemblage des six seuils
  export.py             récapitulatif, évolution 2028/2031, export texte
  controles.py          alertes de cohérence des saisies
  expressions.py        évaluation sûre des formules de donnees/regles.csv
  donnees.py            lecture des tables
donnees/                toutes les valeurs réglementaires et les infobulles (CSV, séparateur « ; »)
tests/                  10 670 cas de référence calculés par le classeur Excel + tests
outils/                 extraction depuis le classeur, banc de test LibreOffice, diagnostic
.streamlit/config.toml  thème (couleurs, polices)
static/polices/         polices Work Sans et Archivo Black (licence SIL OFL)
```

## Données et sources

Aucune valeur réglementaire n'est écrite dans le code : tout est dans `donnees/`, et chaque ligne
indique la cellule du classeur d'où elle vient (colonne `source`).

- Tables simples : valeurs moyennes, Mbgéo, Mcgéo, Migéo, Mccat, Mbbruit, seuils des lots…
- `regles.csv` : modulations qui dépendent de la surface, de la date ou d'autres saisies,
  écrites comme des formules lisibles, par exemple `(47.5 - (0.095 * sref)) / bbiomaxmoyen`.
- `aides.csv` : infobulles reprises de la colonne I de l'onglet de saisie du classeur ;
  `aides_complements.csv` : définitions de l'annexe pour les autres champs.

Textes de référence : annexe à l'article R. 172-4 du CCH consolidée (décrets 2021-1004, 2022-305,
2024-1258, 2026-16) et décret n° 2026-200 du 18 mars 2026, applicable aux permis de construire
déposés à partir du 1er juillet 2026.

Après une mise à jour du classeur, régénérer les données puis relancer les tests :

```
python outils/extraire_excel.py outils/calcul_seuils_RE2020_NU_v2.2.xlsx <classeur_recalculé.xlsx> donnees
python -m pytest
```

## Tests

```
.venv\Scripts\python -m pip install pytest      (Windows)
.venv\Scripts\python -m pytest
```

`tests/test_cas_reference.py` compare le moteur au classeur Excel v2.2 sur 10 670 cas
(28 usages × zones, altitudes, périodes, surfaces, bruit, catégories, lots carbone, HSP, agrément,
réseau de chaleur, IGH, date du PC). Écart toléré : 10⁻⁶. Les autres tests vérifient l'export,
l'évolution 2028/2031 et l'interface (affichage, lien de sauvegarde). Ils tournent aussi à chaque
envoi sur GitHub (`.github/workflows/tests.yml`).

## Limites connues

- Surélévations et extensions : pas encore traitées.
- IGH en 2031 : le classeur prend 95 % de la valeur 2028 standard ; une lecture littérale du décret
  donnerait 95 % de la valeur IGH 2028. Interprétation à confirmer.
- DH Effinergie : le bonus « exposition au bruit » du classeur ne se déclenche jamais ; reproduit
  tel quel, à corriger dans le classeur puis ici.
- Pas de calcul multi-usages au prorata des Sref.
- Sur téléphone, le menu s'ouvre par défaut et recouvre la page : le refermer avec « « ».

## Versions

0.8.x tant que l'outil n'est pas validé, puis 0.9. Chiffre pair = évolution importante, chiffre
impair = correction. Détail dans `CHANGELOG.md`.

## Licence et crédits

GNU GPL v3, comme le classeur d'origine. Polices Work Sans et Archivo Black : SIL Open Font License 1.1
(`static/polices/`).

Guillaume Meunier, d'après son classeur `calcul_seuils_RE2020_NU`. Le passage du classeur à la
version 2.0 (indicateurs carbone et énergie des nouveaux usages) est dû à Félix Dubois (CSTB) ;
corrections signalées par Cédrick Gbegnon, Léonard Forissier et Félix Dubois.
