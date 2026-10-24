"""
Pilote LibreOffice (UNO) : recalcule l'Excel de référence pour une liste de cas.
Usage : python3 excel_driver.py <classeur.xlsx> <cas.json> <sortie.json>
Chaque cas = dict {cellule_Input_resultats: valeur}. Retourne les seuils + coefficients.
"""
import json, os, subprocess, sys, time
import uno
from com.sun.star.beans import PropertyValue

# ─── Paramètres ──────────────────────────────────────────────────────────────
CLASSEUR, FICHIER_CAS, FICHIER_SORTIE = sys.argv[1:4]
PORT = int(os.environ.get("LO_PORT", "2002"))
FEUILLE_ENTREES = "Input_resultats"
# Cellules lues en sortie (feuille Input_resultats)
SORTIES = {
    "bbiomax": "E37", "cepnrmax": "E39", "cepmax": "E41", "icenergiemax": "E43",
    "icconstructionmax": "E45", "dhmax": "E48", "dh_effinergie": "F48",
    # coefficients Bbio
    "bbiomoy": "F37", "mbgeo": "H37", "mbcombles": "J37", "mbsurfmoy": "L37",
    "mbsurftot": "N37", "mbbruit": "P37", "mbhsp": "R37",
    # coefficients énergie
    "cepnrmoy": "F39", "cepmoy": "F41", "icenmoy": "F43", "mcgeo": "H39",
    "mccombles": "J39", "mcsurfmoy": "L39", "mcsurftot": "N39", "mccat": "P39", "mchsp": "R39",
    # coefficients matière
    "iccmoy": "F45", "micombles": "H45", "misurfmoy": "J45", "misurftot": "L45",
    "migeo": "N45", "miinfra": "P45", "mivrd": "R45", "mipv": "T45", "mided": "V45",
    "miagrement": "X45", "mihsp": "Z45", "miclimrcu": "AB45",
}


def propriete(nom, valeur):
    p = PropertyValue(); p.Name = nom; p.Value = valeur
    return p


def connecter():
    """Démarre soffice headless puis s'y connecte."""
    subprocess.Popen(["soffice", "--headless", "--norestore", "--nologo",
                      f"-env:UserInstallation=file:///tmp/claude-0/lo_profil_{PORT}",
                      f"--accept=socket,host=localhost,port={PORT};urp;"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    local = uno.getComponentContext()
    resolveur = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            ctx = resolveur.resolve(
                f"uno:socket,host=localhost,port={PORT};urp;StarOffice.ComponentContext")
            return ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("LibreOffice injoignable")


def lire(cellule):
    """Valeur numérique, texte, ou message d'erreur Excel."""
    if cellule.getError():
        return f"#ERR{cellule.getError()}"
    t = cellule.getType().value
    if t == "TEXT":
        return cellule.getString()
    if t == "EMPTY":
        return None
    # formule : 2 = résultat texte (com.sun.star.sheet.FormulaResult.STRING)
    if t == "FORMULA" and cellule.FormulaResultType2 == 2:
        return cellule.getString()
    return cellule.getValue()


def _est_nombre(s):
    try:
        float(s.replace(",", ".").replace(" ", "").replace(" ", "")); return True
    except ValueError:
        return False


def main():
    bureau = connecter()
    url = uno.systemPathToFileUrl(os.path.abspath(CLASSEUR))
    doc = bureau.loadComponentFromURL(url, "_blank", 0, (propriete("Hidden", True),))
    feuille = doc.Sheets.getByName(FEUILLE_ENTREES)
    cas_liste = json.load(open(FICHIER_CAS))
    resultats = []
    for cas in cas_liste:
        for adr, val in cas["excel"].items():
            c = feuille.getCellRangeByName(adr)
            if isinstance(val, str):
                c.setString(val)
            else:
                c.setValue(val)
        doc.calculateAll()
        resultats.append({k: lire(feuille.getCellRangeByName(a)) for k, a in SORTIES.items()})
    json.dump(resultats, open(FICHIER_SORTIE, "w"), ensure_ascii=False)
    doc.close(True)
    try:
        bureau.terminate()
    except Exception:
        pass


if __name__ == "__main__":
    main()
