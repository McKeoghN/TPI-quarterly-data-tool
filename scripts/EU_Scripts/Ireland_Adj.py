import pandas as pd

def generate():
    # Ireland_GVA = pd.read_csv('../src/Ireland_Data.csv') # Replaced with API call
    Ireland_GVA = pd.read_csv('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/NAQ06/CSV/1.0/en', usecols=["STATISTIC","Statistic Label","TLIST(Q1)","Quarter","C02937V03552","Sector","UNIT","VALUE"])

    Ireland_GVA = Ireland_GVA[
        Ireland_GVA['Sector'] == 'Other sectors excluding the foreign-owned multinational enterprise dominated sector'
    ]

    Ireland_GVA = Ireland_GVA[
        Ireland_GVA['Statistic Label'] == 'GVA at Constant Basic Prices (Seasonally Adjusted)'
    ]

    Ireland_GVA = Ireland_GVA[['Quarter', 'VALUE']]

    Ireland_GVA = Ireland_GVA.rename(columns={
        'VALUE': 'Value'
    })

    Ireland_GVA["Quarter"] = pd.PeriodIndex(Ireland_GVA["Quarter"], freq="Q")

    Ireland_GVA = Ireland_GVA.sort_values("Quarter").reset_index(drop=True)

    base_2020 = Ireland_GVA[
        Ireland_GVA["Quarter"].dt.year == 2020
    ]["Value"].mean()

    base_2023 = Ireland_GVA[
        Ireland_GVA["Quarter"].dt.year == 2023
    ]["Value"].mean()

    scale_factor = base_2020 / base_2023

    Ireland_GVA["Value"] = Ireland_GVA["Value"] * scale_factor

    Ireland_GVA = Ireland_GVA[
        (Ireland_GVA["Quarter"] >= "2023Q1") &
        (Ireland_GVA["Quarter"] <= "2025Q4")
    ]

    Ireland_GVA['Country'] = 'Ireland'
    Ireland_GVA = Ireland_GVA[['Country', 'Quarter', 'Value']]

    print(Ireland_GVA)

    # EuroZone = pd.read_csv('../src/EuroZoneGVA.csv')
    EuroZone_URL = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/namq_10_gdp/1.0/*.*.*.*.*?c[freq]=Q&c[unit]=CP_MEUR,PD20_EUR&c[s_adj]=SCA&c[na_item]=B1G&c[geo]=BE,DE,EE,EL,ES,FR,HR,IT,CY,LV,LT,LU,MT,NL,AT,PT,SI,SK,FI&c[TIME_PERIOD]=2025-Q4,2025-Q3,2025-Q2,2025-Q1,2024-Q4,2024-Q3,2024-Q2,2024-Q1,2023-Q4,2023-Q3,2023-Q2,2023-Q1&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name'
    EuroZone = pd.read_csv(EuroZone_URL)
    EuroZone = EuroZone[['Unit of measure', 'Geopolitical entity (reporting)', 'TIME_PERIOD', 'OBS_VALUE']]
    EuroZone = EuroZone.rename(columns={
        'Geopolitical entity (reporting)': "Country",
        'TIME_PERIOD': 'Quarter',
        'OBS_VALUE': 'Value'
    })
    EuroZone["Quarter"] = pd.PeriodIndex(EuroZone["Quarter"], freq="Q")
    nominal = EuroZone[
        EuroZone["Unit of measure"] == "Current prices, million euro"
    ].rename(columns={"Value": "nominal_gva"})

    deflator = EuroZone[
        EuroZone["Unit of measure"] == "Price index (implicit deflator), 2020=100, euro"
    ].rename(columns={"Value": "deflator"})

    merged = pd.merge(
        nominal[["Country", "Quarter", "nominal_gva"]],
        deflator[["Country", "Quarter", "deflator"]],
        on=["Country", "Quarter"],
        how="inner"
    )

    merged["Value"] = (merged["nominal_gva"] / merged["deflator"]) * 100
    merged = merged[['Country', 'Quarter', 'Value']]
    EuroZone_GVA = pd.concat([Ireland_GVA, merged])
    EuroZone_GVA = EuroZone_GVA.groupby("Quarter")["Value"].sum().reset_index().rename(columns={"Value": "GVA"})

    Hours_URL = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/namq_10_a10_e/1.0/*.*.*.*.*.*?c[freq]=Q&c[unit]=THS_HW&c[nace_r2]=TOTAL&c[s_adj]=SCA&c[na_item]=EMP_DC&c[geo]=BE,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,MT,NL,AT,PT,SI,SK,FI&c[TIME_PERIOD]=2025-Q4,2025-Q3,2025-Q2,2025-Q1,2024-Q4,2024-Q3,2024-Q2,2024-Q1,2023-Q4,2023-Q3,2023-Q2,2023-Q1&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name'
    EuroZone_Hours = pd.read_csv(Hours_URL)
    # EuroZone_Hours = pd.read_csv('../src/EuroZone_Hours.csv')
    EuroZone_Hours = EuroZone_Hours[['Geopolitical entity (reporting)', 'TIME_PERIOD', 'OBS_VALUE']]
    EuroZone_Hours = EuroZone_Hours.rename(columns={
        'Geopolitical entity (reporting)': "Country",
        'TIME_PERIOD': 'Quarter',
        'OBS_VALUE': 'Hours'
    })
    EuroZone_Hours["Quarter"] = pd.PeriodIndex(EuroZone_Hours["Quarter"], freq="Q")

    print("Before:")
    print(EuroZone_Hours.groupby("Quarter")["Country"].nunique())
    # Add Belgium if it's missing
    # belgium_q3 = EuroZone_Hours[
    #     (EuroZone_Hours["Country"] == "Belgium") &
    #     (EuroZone_Hours["Quarter"] == "2025Q3")
    # ]["Hours"].values[0]
    # new_row = pd.DataFrame({
    #     "Country": ["Belgium"],
    #     "Quarter": [pd.Period("2025Q4", freq="Q")],
    #     "Hours": [belgium_q3]
    # })
    # EuroZone_Hours = pd.concat([EuroZone_Hours, new_row])

    print("After:")
    print(EuroZone_Hours.groupby("Quarter")["Country"].nunique())
    EuroZone_Hours = EuroZone_Hours.groupby("Quarter")["Hours"].sum().reset_index()
    EuroZone_Productivity = pd.merge(EuroZone_GVA, EuroZone_Hours, on="Quarter")
    EuroZone_Productivity["productivity"] = (EuroZone_Productivity["GVA"] / EuroZone_Productivity["Hours"]) * 1000
    print("Ireland adjusted")
    print(EuroZone_Productivity["GVA"])
    print(EuroZone_Productivity["Hours"])

    EuroZone_Productivity = EuroZone_Productivity.sort_values("Quarter").reset_index(drop=True)

    EuroZone_Productivity["QoQ"] = EuroZone_Productivity["productivity"].pct_change() * 100
    EuroZone_Productivity["YoY"] = EuroZone_Productivity["productivity"].pct_change(4) * 100

    EuroZone_Productivity = EuroZone_Productivity.round(2)

    # EuroZone_Productivity.to_excel("EU_Figures/EuroZone_Productivity_Adjusted.xlsx", index=False)

    EuroZone_URL_IE = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/namq_10_gdp/1.0/*.*.*.*.*?c[freq]=Q&c[unit]=CP_MEUR,PD20_EUR&c[s_adj]=SCA&c[na_item]=B1G&c[geo]=BE,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,MT,NL,AT,PT,SI,SK,FI&c[TIME_PERIOD]=2025-Q4,2025-Q3,2025-Q2,2025-Q1,2024-Q4,2024-Q3,2024-Q2,2024-Q1,2023-Q4,2023-Q3,2023-Q2,2023-Q1&compress=false&format=csvdata&formatVersion=2.0&lang=en&labels=name'
    EuroZone_IE = pd.read_csv(EuroZone_URL_IE)
    # EuroZone_IE.to_csv('IRELAND.csv')
    EuroZone_IE = EuroZone_IE[['Unit of measure', 'Geopolitical entity (reporting)', 'TIME_PERIOD', 'OBS_VALUE']]
    EuroZone_IE = EuroZone_IE.rename(columns={
        'Geopolitical entity (reporting)': "Country",
        'TIME_PERIOD': 'Quarter',
        'OBS_VALUE': 'Value'
    })
    EuroZone_IE["Quarter"] = pd.PeriodIndex(EuroZone_IE["Quarter"], freq="Q")
    nominal_IE = EuroZone_IE[
        EuroZone_IE["Unit of measure"] == "Current prices, million euro"
    ].rename(columns={"Value": "nominal_gva"})
    deflator_IE = EuroZone_IE[
        EuroZone_IE["Unit of measure"] == "Price index (implicit deflator), 2020=100, euro"
    ].rename(columns={"Value": "deflator"})
    merged_IE = pd.merge(
        nominal_IE[["Country", "Quarter", "nominal_gva"]],
        deflator_IE[["Country", "Quarter", "deflator"]],
        on=["Country", "Quarter"],
        how="inner"
    )
    merged_IE["Value"] = (merged_IE["nominal_gva"] / merged_IE["deflator"]) * 100
    merged_IE = merged_IE[['Country', 'Quarter', 'Value']]
    EuroZone_GVA_IE = merged_IE.groupby("Quarter")["Value"].sum().reset_index().rename(columns={"Value": "GVA"})
    EuroZone_Productivity_IE = pd.merge(EuroZone_GVA_IE, EuroZone_Hours, on="Quarter")
    EuroZone_Productivity_IE["productivity"] = (EuroZone_Productivity_IE["GVA"] / EuroZone_Productivity_IE["Hours"]) * 1000
    EuroZone_Productivity_IE = EuroZone_Productivity_IE.sort_values("Quarter").reset_index(drop=True)
    EuroZone_Productivity_IE["QoQ"] = EuroZone_Productivity_IE["productivity"].pct_change() * 100
    EuroZone_Productivity_IE["YoY"] = EuroZone_Productivity_IE["productivity"].pct_change(4) * 100
    EuroZone_Productivity_IE = EuroZone_Productivity_IE.round(2)

    with pd.ExcelWriter(
        "scripts/EU_Figures/OPH_Figures.xlsx",
        engine="openpyxl"
    ) as writer:

        EuroZone_Productivity.to_excel(
            writer,
            sheet_name="Adjusted Eurozone GVAH",
            index=False
        )

        EuroZone_Productivity_IE.to_excel(
            writer,
            sheet_name="Unadjusted Eurozone GVAH",
            index=False
        )

    # EuroZone_Productivity_IE.to_excel("EU_Figures/EuroZone_Productivity_Eurostat.xlsx", index=False)
    print("Original")
    print(EuroZone_Productivity_IE["GVA"])
    print(EuroZone_Productivity_IE["Hours"])
