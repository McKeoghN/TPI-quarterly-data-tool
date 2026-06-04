import pandas as pd
import scripts.EU_Scripts.Euro_Blog_Processing as Euro_Blog_Processing
import scripts.EU_Scripts.Ireland_Adj as Ireland_Adj
import scripts.EU_Scripts.EU_Vis as EU_Vis

current_quarter = "2025Q4"
Euro_Blog_Processing.generate(current_quarter)
Ireland_Adj.generate(current_quarter)
EU_Vis.generate(current_quarter)

out_path = 'scripts/EU_Figures/'
with pd.ExcelWriter(f"{out_path}/{current_quarter}_EU_Figures.xlsx", engine="openpyxl") as writer:

    for file in [f"{out_path}/EU_Figures.xlsx", f"{out_path}/OPH_Figures.xlsx"]:
        sheets = pd.read_excel(file, sheet_name=None)

        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
