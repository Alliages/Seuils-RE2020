"""
Sûreté de l'évaluation des expressions de donnees/ : refus des constructions dangereuses.
"""
import pytest

from seuils_re2020.expressions import compiler

# ─── Paramètres ──────────────────────────────────────────────────────────────
INTERDITES = ["9**9**9", "2**100", "x.real", "__import__('os')", "open('f')", "[1, 2]"]


@pytest.mark.parametrize("expression", INTERDITES)
def test_constructions_refusees(expression):
    with pytest.raises(ValueError):
        compiler(expression)


def test_expressions_du_projet_acceptees():
    assert compiler("min(smoylgt, 100) / 2 if oui else 0")
