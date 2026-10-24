# Seuils RE2020

Calcul des six seuils réglementaires de la RE2020 (Bbio_max, Cep,nr_max, Cep_max, Icénergie_max,
Icconstruction_max, DH_max) pour les 28 usages de l'annexe à l'article R. 172-4 du code de la
construction et de l'habitation, en France métropolitaine.

> Document non officiel, à utiliser avec toutes les vérifications nécessaires.

Version **0.8.0** — version de travail : le moteur reproduit à l'identique le classeur
`calcul_seuils_RE2020_NU` v2.2 sur 10 670 cas de test ; l'outil passera en 0.9 quand il aura été
validé en usage réel.

## Lancer l'application

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre dans le navigateur (http://localhost:8501).

## Utiliser le moteur sans interface

```python
from seuils_re2020 import Projet, calculer

projet = Projet(usage_id=2, zone="H1a", altitude="<400m", sref=3000,
                periode_pc="2028 à 2030", nb_logements=50)
resultats = calculer(projet)
print(resultats["bbio_max"].valeur, resultats["bbio_max"].coefficients)
```

La liste des usages et leurs numéros est dans `donnees/usages.csv`.

## Organisation

```
app.py                  interface Streamlit (saisie et affichage seulement)
seuils_re2020/          moteur de calcul, sans dépendance à Streamlit
  variables.py          paramètres et listes de choix, regroupés en tête
  regles.py             description du projet, date du décret 2026-200, choix des règles
  calculs.py            assemblage des six seuils
  controles.py          alertes de cohérence des saisies
  expressions.py        évaluation sûre des formules de donnees/regles.csv
  donnees.py            lecture des tables
donnees/                toutes les valeurs réglementaires (CSV, séparateur « ; »)
tests/                  10 670 cas de référence calculés par le classeur Excel + tests
outils/                 extraction depuis le classeur, banc de test LibreOffice, diagnostic
```

## Données et sources

Aucune valeur réglementaire n'est écrite dans le code : tout est dans `donnees/`.
Chaque ligne indique la cellule du classeur d'où elle vient (colonne `source`).

- Tables simples (valeurs moyennes, Mbgéo, Mcgéo, Migéo, Mccat, Mbbruit, seuils des lots…)
- `regles.csv` : modulations qui dépendent de la surface, de la date ou d'autres saisies,
  écrites comme des formules lisibles, par exemple
  `(47.5 - (0.095 * sref)) / bbiomaxmoyen` pour Mbsurf_tot des commerces.

Textes de référence : annexe à l'article R. 172-4 du CCH consolidée (décrets 2021-1004,
2022-305, 2024-1258, 2026-16) et décret n° 2026-200 du 18 mars 2026, applicable aux permis
déposés à partir du 1er juillet 2026.

Pour régénérer les données après une mise à jour du classeur :

```bash
python outils/extraire_excel.py outils/calcul_seuils_RE2020_NU_v2.2.xlsx <classeur_recalculé.xlsx> donnees
pytest
```

## Tests

```bash
pip install pytest
pytest
```

`tests/test_cas_reference.py` compare le moteur au classeur Excel v2.2 sur 10 670 cas
(28 usages × zones, altitudes, périodes, surfaces, bruit, catégories, lots carbone, HSP,
agrément, RCU, IGH, date du PC). Écart toléré : 10⁻⁶. Les tests tournent à chaque envoi sur
GitHub (`.github/workflows/tests.yml`).

## Limites connues (0.8.0)

- IGH en 2031 : le classeur prend 95 % de la valeur 2028 standard ; une lecture littérale du
  décret donnerait 95 % de la valeur IGH 2028. Interprétation à confirmer.
- DH Effinergie : le bonus « exposition au bruit » du classeur ne se déclenche jamais
  (comparaison à « BR2,BR3 ») ; reproduit tel quel, à corriger dans le classeur puis ici.
- Pas encore de calcul multi-usages au prorata des Sref, ni d'onglet surélévations et extensions.
- Les conditions de `regles.csv` sont encore écrites de façon verbeuse (traduction automatique).

## Versions

Numérotation : on reste en 0.8.x tant que l'outil n'est pas validé, puis 0.9.
Chiffre pair = évolution importante, chiffre impair = correction. Voir `CHANGELOG.md`.

## Licence et crédits

GNU GPL v3, comme le classeur d'origine.

Guillaume Meunier, d'après son classeur `calcul_seuils_RE2020_NU`. Le passage du classeur à la
version 2.0 (indicateurs carbone et énergie des nouveaux usages) est dû à Félix Dubois (CSTB) ;
corrections signalées par Cédrick Gbegnon, Léonard Forissier et Félix Dubois.
