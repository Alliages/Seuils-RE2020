"""
Traduction des formules Excel du classeur de référence en expressions Python lisibles.

Utilisé uniquement par outils/extraire_excel.py : le moteur n'importe jamais ce module.
Couvre le sous-ensemble de formules présent dans le classeur : nombres, textes,
références de cellules et noms définis, + - * / ^ &, comparaisons,
IF, AND, OR, NOT, MIN, MAX.
"""
import re

# ─── Paramètres ──────────────────────────────────────────────────────────────
# Noms Excel -> noms des variables du moteur (voir seuils_re2020/variables.py)
NOMS = {
    "sref": "sref", "smoylgt": "smoylgt", "scombles": "scombles", "hspmoy": "hspmoy",
    "sagrément": "sagrement", "expobruit": "expobruit", "depotpc": "depotpc",
    "depotpc_année": "depotpc_annee", "rcu": "rcu", "rcu_classe": "rcu_classe",
    "climatisé": "climatise", "est_igh": "est_igh", "decret2026": "decret2026",
    "categorie": "categorie", "zoneclim": "zoneclim", "elevation": "elevation",
    "icded": "icded", "iclot1": "iclot1", "iclot2": "iclot2", "iclot13": "iclot13",
    "bbiomaxmoyen": "bbiomaxmoyen", "cepnrmaxmoyen": "cepnrmaxmoyen",
    "icconstructionmaxmoyen": "icconstructionmaxmoyen",
    "usage": "usage", "usage_detaillé": "usage_detaille",
    "classe_inertie": "classe_inertie", "dh_max": "dh_max",
}
# Cellules de saisie désignées par adresse dans certaines formules
ADRESSES_SAISIE = {"Input_resultats!E4": "usage", "Input_resultats!E15": "depotpc"}
FONCTIONS = {"IF", "AND", "OR", "NOT", "MIN", "MAX", "ISNUMBER", "MATCH", "COUNTIF",
             "VLOOKUP", "HLOOKUP", "INDEX", "INDIRECT", "ADDRESS"}

_JETONS = re.compile(r"""
    (?P<nombre>\d+(?:\.\d+)?(?:E[+-]?\d+)?)
  | (?P<texte>"(?:[^"]|"")*")
  | (?P<ref>(?:'[^']+'|[A-Za-zÀ-ÿ_][\wÀ-ÿ]*)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?
           |\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?(?![\wÀ-ÿ(]))
  | (?P<nom>[A-Za-zÀ-ÿ_][\wÀ-ÿ.]*)
  | (?P<op><=|>=|<>|[-+*/^&=<>(),:])
  | (?P<espace>\s+)
""", re.X)


class FormuleNonGeree(Exception):
    pass


# ─── Analyse syntaxique (arbre en tuples) ────────────────────────────────────
def jetons(formule):
    pos, sortie = 0, []
    while pos < len(formule):
        m = _JETONS.match(formule, pos)
        if not m:
            raise FormuleNonGeree(f"jeton illisible à {formule[pos:pos+20]!r} dans {formule!r}")
        pos = m.end()
        if m.lastgroup != "espace":
            sortie.append((m.lastgroup, m.group(0)))
    return sortie


PRIORITES = {"=": 1, "<>": 1, "<": 1, ">": 1, "<=": 1, ">=": 1, "&": 2,
             "+": 3, "-": 3, "*": 4, "/": 4, "^": 5}


def analyser(formule):
    """Formule Excel (sans '=') -> arbre."""
    j = jetons(formule.lstrip("="))
    pos = [0]

    def voir():
        return j[pos[0]] if pos[0] < len(j) else (None, None)

    def prendre(attendu=None):
        t = voir()
        if attendu and t[1] != attendu:
            raise FormuleNonGeree(f"attendu {attendu} dans {formule!r}")
        pos[0] += 1
        return t

    def primaire():
        genre, val = prendre()
        if val == "-":
            return ("neg", primaire())
        if val == "+":
            return primaire()
        if val == "(":
            e = expr(0); prendre(")"); return e
        if genre == "nombre":
            return ("num", float(val))
        if genre == "texte":
            return ("txt", val[1:-1].replace('""', '"'))
        if genre == "ref":
            return ("ref", val)
        if genre == "nom":
            if voir()[1] == "(":
                prendre("(")
                args = []
                if voir()[1] != ")":
                    args.append(expr(0))
                    while voir()[1] == ",":
                        prendre(","); args.append(expr(0))
                prendre(")")
                nom = val.upper().replace("_XLFN.", "")
                if nom not in FONCTIONS:
                    raise FormuleNonGeree(f"fonction {nom} dans {formule!r}")
                return ("fn", nom, args)
            if val.upper() in ("TRUE", "FALSE"):
                return ("bool", val.upper() == "TRUE")
            return ("nom", val)
        raise FormuleNonGeree(f"jeton inattendu {val!r} dans {formule!r}")

    def expr(prio_min):
        gauche = primaire()
        while True:
            op = voir()[1]
            p = PRIORITES.get(op)
            if p is None or p < prio_min:
                return gauche
            prendre()
            droite = expr(p + (0 if op == "^" else 1))
            gauche = ("op", op, gauche, droite)

    arbre = expr(0)
    if pos[0] != len(j):
        raise FormuleNonGeree(f"reste non lu dans {formule!r}")
    return arbre


# ─── Traduction en Python ────────────────────────────────────────────────────
OPS_PY = {"=": "==", "<>": "!=", "&": "+", "^": "**"}


def nombre(x):
    return str(int(x)) if float(x).is_integer() else repr(x)


def en_python(arbre, resoudre):
    """Arbre -> texte Python. `resoudre(ref)` traduit une référence de cellule."""
    genre = arbre[0]
    if genre == "num":
        return nombre(arbre[1])
    if genre == "txt":
        return repr(arbre[1].strip().lower())
    if genre == "bool":
        return "True" if arbre[1] else "False"
    if genre == "nom":
        cle = arbre[1].lower()
        if cle not in NOMS:
            raise FormuleNonGeree(f"nom inconnu {arbre[1]}")
        return NOMS[cle]
    if genre == "ref":
        return resoudre(arbre[1])
    if genre == "neg":
        return f"-{en_python(arbre[1], resoudre)}"
    if genre == "op":
        _, op, g, d = arbre
        return f"({en_python(g, resoudre)} {OPS_PY.get(op, op)} {en_python(d, resoudre)})"
    if genre == "fn":
        _, nom, a = arbre
        t = [en_python(x, resoudre) for x in a] if nom not in ("ISNUMBER", "MATCH", "COUNTIF") else []
        if nom == "IF":
            sinon = t[2] if len(t) > 2 else "False"
            return f"({t[1]} if {t[0]} else {sinon})"
        if nom in ("AND", "OR"):
            return "(" + f" {nom.lower()} ".join(t) + ")"
        if nom == "NOT":
            return f"(not {t[0]})"
        if nom in ("MIN", "MAX"):
            return f"{nom.lower()}({', '.join(t)})"
    raise FormuleNonGeree(f"élément non traduisible {arbre!r}")


def simplifier(texte):
    """Retire les parenthèses extérieures superflues."""
    while texte.startswith("(") and texte.endswith(")"):
        niveau = 0
        for i, c in enumerate(texte):
            niveau += (c == "(") - (c == ")")
            if niveau == 0 and i < len(texte) - 1:
                return texte
        texte = texte[1:-1]
    return texte
