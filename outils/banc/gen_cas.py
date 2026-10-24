"""
Génère la matrice de cas de test : chaque cas porte les entrées Excel (cellules de
Input_resultats). Le champ « js » a servi à l'audit du calculateur tiers mon-calculateur-RE2020.
Chaîne complète : banc/dump.py -> banc/gen_cas.py -> banc/excel_driver.py (LibreOffice)
-> creer_cas_reference.py -> tests/cas_reference.csv
Usage : python3 gen_cas.py <dossier_dump> <sortie.json>
"""
import itertools, json, re, sys, collections

# ─── Paramètres ──────────────────────────────────────────────────────────────
DUMP, SORTIE = sys.argv[1:3]
ZONES = ["H1a", "H1b", "H1c", "H2a", "H2b", "H2c", "H2d", "H3"]
PERIODES = [  # (libellé Excel, année JS, apresJuillet2026)
    ("2022 à 2024", 2023, False),
    ("2025 à 2027", 2026, True),
    ("2028 à 2030", 2029, True),
    ("à partir de 2031", 2032, True),
]
ALTITUDES = [("<400m", 200), ("400m-800m", 600), (">800m", 1000)]
SREF_DEFAUT = {1: 120, 2: 3000}           # sinon 2000 m²
SMOY_LC = 60                               # m² par logement (LC)
SREFS_BALAYAGE = [40, 80, 100, 120, 150, 200, 300, 600, 1000, 2000, 4000, 8000, 15000]


def lire_dump(fichier):
    cellules = {}
    for ligne in open(fichier, encoding="utf-8"):
        morceaux = ligne.rstrip("\n").split("\t")
        if len(morceaux) >= 2:
            cellules[morceaux[0]] = morceaux[1]
    return cellules


# ─── Usages détaillés (1..28) → (usage Excel, usage secondaire) ─────────────
enum = lire_dump(f"{DUMP}/Enumération.txt")
detail = [eval(enum[f"E{r}"]) for r in range(4, 32)]
listes_sec = [eval(enum[f"{col}{r}"]) for col in "FGHIJK" for r in range(4, 8) if f"{col}{r}" in enum]
USAGES = {}
for i, d in enumerate(detail, start=1):
    if " - " in d:
        principal, sec = d.split(" - ", 1)
        assert sec in listes_sec, (d, sec)
        USAGES[i] = (principal, sec)
    else:
        USAGES[i] = (d, "-")

# ─── Zone → un département représentatif (feuille « zone climatique ») ───────
zc = lire_dump(f"{DUMP}/zone_climatique.txt")
lignes = collections.defaultdict(dict)
for adr, v in zc.items():
    m = re.match(r"([A-Z]+)(\d+)$", adr)
    lignes[int(m[2])][m[1]] = eval(v)
DEPT = {}
for r in sorted(lignes):
    l = lignes[r]
    if r > 2 and l.get("D") in ZONES and l["D"] not in DEPT:
        DEPT[l["D"]] = l["C"]
assert len(DEPT) == 8, DEPT


def cas(usage, zone="H2b", alt=ALTITUDES[0], periode=PERIODES[2], sref=None, smoy=None,
        bruit="BR1", cat=1, clim=False, rcu=False, rcu_classe=False, igh=False,
        sagr=0.0, hsp=2.5, lot1=0, lot2=0, lot13=0, ded=0, scombles=0, groupe=""):
    """Construit un cas en double représentation Excel / JS."""
    sref = sref or SREF_DEFAUT.get(usage, 2000)
    if usage == 1:
        nl, smoy = 1, sref                      # l'UI JS force smoylgt = Sref pour une maison
    elif usage == 2:
        smoy = smoy or SMOY_LC
        nl = sref / smoy
    else:
        nl, smoy = 1, 0
    principal, sec = USAGES[usage]
    oui = lambda b: "OUI" if b else "NON"
    excel = {
        "E4": principal, "E5": sec, "E6": DEPT[zone], "E7": "-", "E9": alt[0],
        "E10": sref, "E11": scombles, "E12": nl, "E14": bruit, "E15": periode[0],
        "E16": lot1, "E17": lot2, "E18": lot13, "E19": ded,
        "E20": oui(rcu), "E21": oui(rcu_classe), "E22": f"Catégorie {cat}",
        "E23": oui(clim), "E25": oui(igh), "E26": sagr * sref, "E27": hsp,
        "E29": "Lourde ou très lourde",
    }
    js = {
        "usage": usage, "anneePC": periode[1], "apresJuillet2026": periode[2],
        "zone": zone, "altitude": alt[1], "sref": sref, "smoylgt": smoy,
        "bruit": "BR1" if bruit == "BR1" else "BR2BR3",   # comme l'UI (case à cocher)
        "categorie": f"cat{cat}", "climatise": clim, "rcu": rcu, "hsp": hsp, "igh": igh,
        "sagrementExt": sagr * sref, "icLot1": lot1, "icLot2": lot2, "icLot13": lot13,
        "icDed": ded, "scombles": scombles,
    }
    meta = dict(groupe=groupe, usage=usage, zone=zone, alt=alt[0], periode=periode[0],
                sref=sref, smoy=smoy, bruit=bruit, cat=cat, clim=clim, rcu=rcu,
                rcu_classe=rcu_classe, igh=igh, sagr=sagr, hsp=hsp, lot1=lot1, lot2=lot2,
                lot13=lot13, ded=ded, scombles=scombles)
    return {"excel": excel, "js": js, "meta": meta}


liste = []
# A — géographie : usages × zones × altitudes × périodes
for u, z, a, p in itertools.product(USAGES, ZONES, ALTITUDES, PERIODES):
    liste.append(cas(u, z, a, p, groupe="A_geo"))
# B — surfaces de référence
for u, s, p in itertools.product(USAGES, SREFS_BALAYAGE, PERIODES):
    liste.append(cas(u, sref=s, periode=p, groupe="B_sref"))
# C — surface moyenne des logements (LC)
for smoy, p in itertools.product([25, 35, 45, 55, 65, 75, 85, 100, 120, 150], PERIODES):
    liste.append(cas(2, sref=3000, smoy=smoy, periode=p, groupe="C_smoy"))
# C2 — combles aménagés (MI) — non saisissable dans l'UI JS mais testé au niveau moteur
for sc, p in itertools.product([10, 30], PERIODES):
    liste.append(cas(1, sref=120, scombles=sc, periode=p, groupe="C_combles"))
# D — bruit, catégorie, climatisation
for u, b, c, cl, z in itertools.product(USAGES, ["BR1", "BR2", "BR3"], [1, 2, 3], [False, True], ["H1a", "H2d", "H3"]):
    liste.append(cas(u, zone=z, bruit=b, cat=c, clim=cl, groupe="D_bruit_cat"))
# E — lots carbone et DED, une variable à la fois
variations = [dict(lot1=v) for v in (5, 40, 100)] + [dict(lot2=v) for v in (20, 60, 150)] \
    + [dict(lot13=v) for v in (10, 40)] + [dict(ded=v) for v in (100, 250, 350, 450, 700)]
for u, var, p in itertools.product(USAGES, variations, PERIODES):
    liste.append(cas(u, periode=p, groupe="E_lots", **var))
# F — modulations du décret 2026-200 (HSP, agrément, RCU/clim, IGH)
for u, h, sa, (r, rc, cl), ig, p in itertools.product(
        [1, 2, 3, 4, 6, 13, 21, 25], [2.5, 2.7, 3.0], [0.0, 0.15, 0.3],
        [(False, False, False), (True, True, True), (True, False, True), (True, True, False)],
        [False, True], PERIODES):
    for s in ([120, 200] if u == 1 else [None]):
        liste.append(cas(u, sref=s, hsp=h, sagr=sa, rcu=r, rcu_classe=rc, clim=cl, igh=ig,
                         periode=p, groupe="F_decret2026"))

json.dump(liste, open(SORTIE, "w"), ensure_ascii=False)
print(len(liste), "cas ;", collections.Counter(c["meta"]["groupe"] for c in liste))
