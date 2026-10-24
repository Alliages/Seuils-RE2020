import sys, os, warnings, openpyxl
warnings.filterwarnings("ignore")
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
wf = openpyxl.load_workbook(src)                  # formules
wv = openpyxl.load_workbook(src, data_only=True)  # valeurs en cache
with open(f"{out}/_names.txt","w") as f:
    for n,d in wf.defined_names.items(): f.write(f"{n} = {d.attr_text}\n")
for ws in wf.worksheets:
    vs = wv[ws.title]
    with open(f"{out}/{ws.title.replace(' ','_')}.txt","w") as f:
        for row in ws.iter_rows():
            for c in row:
                if c.value is None: continue
                v = vs[c.coordinate].value
                if isinstance(c.value,str) and c.value.startswith('='):
                    f.write(f"{c.coordinate}\t{c.value}\t=> {v!r}\n")
                else:
                    f.write(f"{c.coordinate}\t{c.value!r}\n")
    # validations de données (listes déroulantes)
    with open(f"{out}/{ws.title.replace(' ','_')}_dv.txt","w") as f:
        for dv in ws.data_validations.dataValidation:
            f.write(f"{dv.sqref}\t{dv.type}\t{dv.formula1}\n")
