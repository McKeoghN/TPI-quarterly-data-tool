# Script made for making visualisation for different datasets

import pandas as pd
import plotly_express as px
# import sys
# sys.path.append("../") # So I can import functions from the streamlit script, makes the bargraphs black and white though?
# from Streamlit_application import quarter_to_numeric, numeric_to_quarter

# TPI_colours = ["#eb5e5e", "#03979d", "#9c4f8b"] # peachy colour, greeny blue, lighter purple
TPI_colours = ["#6C2283", "#39A7DF"] # dark purple, blue

def rebase_chain_linked_quarters(df, new_base_year):
    df = df.copy()
    
    # Extract year from Quarter (e.g., 1997.25 -> 1997)
    df["Year"] = df["Quarter"].astype(int)

    def rebase_group(group):
        # Get the mean of the base year for this group
        base_year_values = group[group["Year"] == new_base_year]["Value"]
        if base_year_values.empty or base_year_values.mean() == 0:
            return group  # Skip group if base year is missing or zero
        base_mean = base_year_values.mean()
        group["Value"] = (group["Value"] / base_mean) * 100
        return group

    # Apply rebase per group
    df = df.groupby(["Country", "Industry", "Variable"], group_keys=False).apply(rebase_group)

    # Drop temporary year column
    df = df.drop(columns="Year")

    return df

def quarter_to_numeric(q):
    year, qtr = q.split(" ")
    return int(year) + (int(qtr[1]) - 1) / 4  # Converts "1997 Q3" → 1997.5

def numeric_to_quarter(n):
    year = int(n)
    qtr = int((n - year) * 4) + 1
    return f"{year} Q{qtr}"

def line_graph(data, year, title, yAxisTitle, legendTitle):
        # base = data.loc[data["Quarter"] == f"{year} Q1", ["GVA", "Hours Worked", "OPH"]].iloc[0].to_numpy()
        # cols = ["GVA", "Hours Worked", "OPH"]
        # data[cols] = (data[cols] / base) * 100

        # data["quarter_numeric"] = data["Quarter"].apply(quarter_to_numeric)
        # data = data[(data["quarter_numeric"] >= year) & (data["quarter_numeric"] <= 2024.75)]
        # data = data.drop(["quarter_numeric"], axis=1)

        fig = px.line(
        data, 
        x="Quarter", 
        y=data.columns.drop("Quarter").tolist(), 
        title=f"{title} ({year} = 100)",
        labels={"value": f"{yAxisTitle}", "variable": f"{legendTitle}"},
        color_discrete_sequence=TPI_colours)
        return fig

def qoq(data):
        # data = data[['Quarter', 'OPH']]
        data["quarter_numeric"] = data["Quarter"].apply(quarter_to_numeric)
        # data = data[(data["quarter_numeric"] >= 2022 - 0.25) & (data["quarter_numeric"] <= 2024.75)]
        data = data.drop('quarter_numeric', axis=1)
        data = data.melt(id_vars = "Quarter", var_name = "Measure")
        data["QoQ Growth (%)"] = data.groupby("Measure")["value"].pct_change().mul(100).round(2)

        data = data.dropna()
        fig = px.bar(data, 
                     x="Quarter", 
                     y="QoQ Growth (%)", 
                     color="Measure",
                     color_discrete_sequence=TPI_colours,
                     barmode="group", 
                     title="Q1 2022 - Q4 2024 QoQ Growth")
        fig.update_layout(showlegend=False)
        return fig

def yoy(data):
        data = data[['Quarter', 'OPH']]
        data["Quarter"] = data["Quarter"].apply(quarter_to_numeric)
        data = data[(data["Quarter"] >= 2020.75 - 1) & (data["Quarter"] <= 2024.75)]
        data = data.melt(id_vars = "Quarter", var_name = "Measure")
        quarter_map = {1: 0, 2: 0.25, 3: 0.5, 4: 0.75}
        data['decimal_part'] = data['Quarter'] % 1
        data = data[data['decimal_part'].isin([quarter_map[4]])]
        data.drop('decimal_part', axis=1, inplace=True)
        data["YoY Growth (%)"] = data.groupby("Measure")["value"].pct_change().mul(100).round(2)
        data["Quarter"] = data["Quarter"].apply(numeric_to_quarter)

        data = data.dropna()
        fig = px.bar(data, x="Quarter", y="YoY Growth (%)", color="Measure",
                barmode="group", title="Q4 YOY Growth")
        fig.update_layout(showlegend=False)
        return fig

# Flash_Estimate = pd.read_csv('../src/New-release/OPH Q1 2025.csv', skiprows=7, usecols=[0,1,2,3], names=["Quarter", "GVA", "Hours Worked", "OPH"])
# # Change from Q4 1997 to 1997 Q4
# Flash_Estimate["Quarter"] = Flash_Estimate["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)

# fig = line_graph(Flash_Estimate, 1997)
# # fig = qoq(Flash_Estimate)
# # fig = yoy(Flash_Estimate)

# fig.update_layout(template="plotly_white")

# fig.show()

# Flash_Estimate_OPH = pd.read_csv('../src/New-release/OPH Q1 2025.csv', skiprows=7, usecols=[0,1,2,3], names=["Quarter", "Gross Value Added", "Hours Worked", "Output Per Hour"])
# Flash_Estimate_OPH["Quarter"] = Flash_Estimate_OPH["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# Flash_Estimate_OPH["Quarter"] = Flash_Estimate_OPH["Quarter"].apply(quarter_to_numeric)
# Flash_Estimate_OPH = pd.melt(Flash_Estimate_OPH, id_vars=['Quarter'], var_name='Variable', value_name='Value')
# Flash_Estimate_OPH['Country'] = 'UK Flash Estimate'
# Flash_Estimate_OPH['Industry'] = 'Total'
# # Flash_Estimate_OPH['Variable'] = 'Flash Estimate Output per Hour'
# Flash_Estimate_OPH = rebase_chain_linked_quarters(Flash_Estimate_OPH, 2020)
# print(Flash_Estimate_OPH)

# Dataset = pd.read_csv('../out/Long_Dataset.csv')
# Dataset = pd.concat([Dataset, Flash_Estimate_OPH])
# Dataset.to_csv("../out/Long_Dataset.csv", index=False)

# OPH_Comparison = pd.read_csv('../src/New-release/OPH LFS vs RTI.csv', skiprows=7, usecols=[0,1,2], names=["Quarter", "LFS Output per hour worked", "RTI + SE (exc working proprietors) Output per hour worked"])
# OPH_Comparison["Quarter"] = OPH_Comparison["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# OPH_Comparison["Quarter"] = OPH_Comparison["Quarter"].apply(quarter_to_numeric)
# OPH_Comparison = pd.melt(OPH_Comparison, id_vars=['Quarter'], var_name='Variable', value_name='Value')
# OPH_Comparison['Country'] = 'UK Flash Estimate'
# OPH_Comparison['Industry'] = 'Total'
# print(OPH_Comparison)
# Dataset = pd.read_csv('../out/Long_Dataset.csv')
# Dataset = pd.concat([Dataset, OPH_Comparison])
# Dataset.to_csv("../out/Long_Dataset.csv", index=False)

# Flash_Estimate_OPH['Variable'] = 'Flash Estimate Output per Hour'
# OPH_Comparison = rebase_chain_linked_quarters(OPH_Comparison, 2020)
# # fig = qoq(Flash_Estimate)
# # fig = yoy(Flash_Estimate)
OPH_Comparison = pd.read_csv('../src/New-release/OPH LFS vs RTI.csv', skiprows=7, usecols=[0,1,2], names=["Quarter", "LFS Output per hour worked", "RTI + SE (exc working proprietors) Output per hour worked"])
OPH_Comparison["Quarter"] = OPH_Comparison["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
print(OPH_Comparison)
# fig = line_graph(OPH_Comparison, 2022, "OPH using LFS vs RTI", "Output per hour worked", "OPH ...")
# fig.update_layout(template="plotly_white")
# fig.show()

OPW_Comparison = pd.read_csv('../src/New-release/OPW LFS vs RTI.csv', skiprows=7, usecols=[0,1,2], names=["Quarter", "LFS Output per hour worked", "RTI + SE (exc working proprietors) Output per hour worked"])
OPW_Comparison["Quarter"] = OPW_Comparison["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# fig = line_graph(OPW_Comparison, 2022, "OPW using LFS vs RTI", "Output per worker", "OPW ...")
# fig.update_layout(template="plotly_white")
# fig.show()

fig = qoq(OPH_Comparison)
fig.show()
fig = qoq(OPW_Comparison)
fig.show()