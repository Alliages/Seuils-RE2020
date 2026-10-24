"""
Diagnostic des écarts moteur / Excel : regroupe les écarts par indicateur et par cause.
Usage : python outils/diagnostic.py [nombre_d_exemples]
"""
import collections, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))
from test_cas_reference import INDICATEURS, identiques, lire_cas, projet_depuis  # noqa: E402

from seuils_re2020 import calculs, regles                    # noqa: E402
from seuils_re2020.expressions import NonApplicable          # noqa: E402

# ─── Paramètres ──────────────────────────────────────────────────────────────
NB_EXEMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def cause(projet, ind):
    """Rejoue l'indicateur sans protection pour récupérer le message d'erreur éventuel."""
    v = regles.variables(projet)
    fonctions = {"bbio_max": lambda: calculs.bbio_max(projet, v),
                 "icconstruction_max": lambda: calculs.icconstruction_max(projet, v),
                 "dh_max": lambda: calculs.dh_max(projet, v)}
    try:
        fonctions.get(ind, lambda: calculs.coefficients_mc(projet, v, 1))()
        return "valeur différente"
    except NonApplicable as e:
        return f"non applicable : {str(e)[:120]}"


compte, exemples = collections.Counter(), collections.defaultdict(list)
for l in lire_cas():
    p = projet_depuis(l)
    r = calculs.calculer(p)
    for ind in INDICATEURS:
        if not identiques(l[ind], r[ind].valeur):
            cle = (ind, l["usage_id"], cause(p, ind))
            compte[cle] += 1
            if len(exemples[cle]) < NB_EXEMPLES:
                exemples[cle].append(f"{l['groupe']} {l['periode_pc']} {l['zone']} sref={l['sref']} "
                                     f"Excel={l[ind]} moteur={r[ind].valeur}")
for cle, n in sorted(compte.items(), key=lambda x: -x[1]):
    print(n, cle)
    for e in exemples[cle]:
        print("     ", e)
