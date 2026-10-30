"""
Tables de donnees/ : chaque ligne a autant de champs que l'en-tête
(un « ; » sans guillemets dans un texte décalerait les colonnes et tronquerait la source).
"""
import csv
from pathlib import Path

import pytest

# ─── Paramètres ──────────────────────────────────────────────────────────────
DOSSIER = Path(__file__).resolve().parent.parent / "donnees"
SEPARATEUR = ";"


@pytest.mark.parametrize("fichier", sorted(DOSSIER.glob("*.csv")), ids=lambda f: f.name)
def test_nombre_de_champs(fichier):
    with open(fichier, encoding="utf-8", newline="") as f:
        lignes = list(csv.reader(f, delimiter=SEPARATEUR))   # lecture identique à seuils_re2020/donnees.py
    attendu = len(lignes[0])
    fautives = [n for n, l in enumerate(lignes[1:], start=2) if l and len(l) != attendu]
    assert not fautives, f"{fichier.name} : lignes {fautives}"
