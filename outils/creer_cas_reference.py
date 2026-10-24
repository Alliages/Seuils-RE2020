"""
Convertit les cas calculés par l'Excel (banc LibreOffice) en tests/cas_reference.csv.

Usage : python outils/creer_cas_reference.py <sortie.csv> <cas1.json> <resultats1.json> [<cas2.json> <resultats2.json> …]
Chaque cas = cellules saisies dans Input_resultats ; chaque résultat = seuils lus par le banc.
"""
import csv, json, sys

# ─── Paramètres ──────────────────────────────────────────────────────────────
SORTIE = sys.argv[1]
PAIRES = list(zip(sys.argv[2::2], sys.argv[3::2]))
ZONE_PAR_DEPT = {}   # rempli depuis donnees/zones_departements.csv
SORTIES_EXCEL = {"bbio_max": "bbiomax", "cepnr_max": "cepnrmax", "cep_max": "cepmax",
                 "icenergie_max": "icenergiemax", "icconstruction_max": "icconstructionmax",
                 "dh_max": "dhmax", "dh_effinergie": "dh_effinergie"}
DEFAUT = {"E28": "OUI", "E29": "Lourde ou très lourde"}   # valeurs du classeur si non saisies

with open("donnees/zones_departements.csv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter=";"):
        ZONE_PAR_DEPT[l["departement"]] = l["zone"]

USAGE_PAR_DETAIL = {}
with open("donnees/usages.csv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter=";"):
        USAGE_PAR_DETAIL[l["usage_detaille"].replace("\xa0", " ").strip().lower()] = int(l["id"])


def usage_id(e):
    detail = e["E4"] if e["E5"] == "-" else f"{e['E4']} - {e['E5']}"
    return USAGE_PAR_DETAIL[detail.replace("\xa0", " ").strip().lower()]


def resultat(v):
    if isinstance(v, (int, float)):
        return repr(float(v))
    if v is None or str(v).startswith("#ERR"):
        return "ERREUR"
    return str(v)


lignes = []
for f_cas, f_res in PAIRES:
    for c, r in zip(json.load(open(f_cas)), json.load(open(f_res))):
        e = {**DEFAUT, **c["excel"]}
        lignes.append({
            "groupe": c["meta"]["groupe"], "usage_id": usage_id(e), "zone": ZONE_PAR_DEPT[e["E6"]],
            "altitude": e["E9"], "sref": e["E10"], "periode_pc": e["E15"],
            "pc_apres_juillet_2026": int(e["E28"] == "OUI"), "nb_logements": e["E12"],
            "scombles": e["E11"], "exposition_bruit": e["E14"],
            "categorie": int(e["E22"][-1]), "climatise": int(e["E23"] == "OUI"),
            "rcu": int(e["E20"] == "OUI"), "rcu_classe": int(e["E21"] == "OUI"), "igh": int(e["E25"] == "OUI"),
            "sagrement": e["E26"], "hsp": e["E27"], "iclot1": e["E16"], "iclot2": e["E17"],
            "iclot13": e["E18"], "icded": e["E19"], "classe_inertie": e["E29"],
            **{k: resultat(r[v]) for k, v in SORTIES_EXCEL.items()},
        })

with open(SORTIE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0]), delimiter=";")
    w.writeheader()
    w.writerows(lignes)
print(len(lignes), "cas ->", SORTIE)
