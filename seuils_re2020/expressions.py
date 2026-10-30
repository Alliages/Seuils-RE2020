"""
Évaluation sûre des expressions stockées dans donnees/regles.csv.

Les expressions sont du Python restreint : nombres, textes, variables du projet,
opérations arithmétiques (sans puissance : « ** » peut bloquer l'application), comparaisons, and / or / not, « a if c else b », min et max.
Tout autre élément (appel de fonction, attribut, import…) est refusé.
"""
import ast
from functools import lru_cache

# ─── Paramètres ──────────────────────────────────────────────────────────────
NOEUDS_AUTORISES = (
    ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare, ast.IfExp,
    ast.Call, ast.Name, ast.Load, ast.Constant,
    ast.And, ast.Or, ast.Not, ast.USub, ast.UAdd,
    ast.Add, ast.Sub, ast.Mult, ast.Div,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
)
FONCTIONS_AUTORISEES = {"min": min, "max": max}


class NonApplicable(Exception):
    """Seuil sans objet pour cette combinaison (équivalent d'une erreur Excel)."""


@lru_cache(maxsize=None)
def compiler(expression):
    """Vérifie puis compile une expression ; résultat mis en cache."""
    arbre = ast.parse(expression, mode="eval")
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, NOEUDS_AUTORISES):
            raise ValueError(f"élément interdit {type(noeud).__name__} dans : {expression}")
        if isinstance(noeud, ast.Call) and (
                not isinstance(noeud.func, ast.Name) or noeud.func.id not in FONCTIONS_AUTORISEES):
            raise ValueError(f"fonction interdite dans : {expression}")
    return compile(arbre, "<regle>", "eval")


def evaluer(expression, variables):
    """Évalue une expression ; une erreur de calcul rend le seuil non applicable."""
    try:
        return eval(compiler(expression), {"__builtins__": {}, **FONCTIONS_AUTORISEES}, variables)
    except (ZeroDivisionError, TypeError) as erreur:
        raise NonApplicable(f"{expression} : {erreur}") from erreur
