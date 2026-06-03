import pandas as pd

# Unemployment_URL = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/une_rt_m/1.0/*.*.*.*.*.*?c[freq]=M&c[s_adj]=NSA,SA&c[age]=TOTAL&c[unit]=THS_PER,PC_ACT&c[sex]=T&c[geo]=EU27_2020,EA21,BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,NO,CH,UK,BA,MK,TR,US,JP&c[TIME_PERIOD]=2026-04,2026-03,2026-02,2026-01,2025-12,2025-11,2025-10,2025-09,2025-08,2025-07,2025-06,2025-05,2025-04,2025-03,2025-02,2025-01,2024-12,2024-11,2024-10,2024-09,2024-08,2024-07,2024-06,2024-05,2024-04,2024-03,2024-02,2024-01,2023-12,2023-11,2023-10,2023-09,2023-08,2023-07,2023-06,2023-05,2023-04,2023-03,2023-02,2023-01,2022-12,2022-11,2022-10,2022-09,2022-08,2022-07,2022-06,2022-05,2022-04,2022-03,2022-02,2022-01&compress=false&format=csvdata&formatVersion=1.0&lang=en&labels=label_only'

key_countries = [
    'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Poland', 'Ireland', 'Euro Zone', 'European Union'
]

key_industries = [
    'Total - all NACE activities', 'Manufacturing', 
]

GVA_Chained_URL = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/namq_10_a10/1.0/*.*.*.*.*.*?c[freq]=Q&c[unit]=CLV_I20&c[s_adj]=SCA&c[nace_r2]=TOTAL,A,B-E,C,F,G-I,J,K,L,M_N,O-Q,R-U&c[na_item]=B1G&c[geo]=EU27_2020,EA,EA21,EA20,EA19,EA12,BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,NO,CH,UK,BA,ME,MK,AL,RS,TR,XK&c[TIME_PERIOD]=2026-Q1,2025-Q4,2025-Q3,2025-Q2,2025-Q1,2024-Q4,2024-Q3,2024-Q2,2024-Q1,2023-Q4,2023-Q3,2023-Q2,2023-Q1,2022-Q4,2022-Q3,2022-Q2,2022-Q1,2021-Q4,2021-Q3,2021-Q2,2021-Q1,2020-Q4,2020-Q3,2020-Q2,2020-Q1&compress=false&format=csvdata&formatVersion=1.0&lang=en&labels=label_only'

GVA_Chained = pd.read_csv(GVA_Chained_URL, usecols=['unit', 'nace_r2', 'geo', 'TIME_PERIOD', 'OBS_VALUE']).rename(columns={
        "nace_r2": "Industry",
        "geo": "Country",
        "TIME_PERIOD": "Quarter",
        "OBS_VALUE": "Value"
    })

GVA_Chained['Country'] = GVA_Chained['Country'].replace({
    'Euro area (EA11-1999, EA12-2001, EA13-2007, EA15-2008, EA16-2009, EA17-2011, EA18-2014, EA19-2015, EA20-2023, EA21-2026)': 'Euro Zone',
    'European Union - 27 countries (from 2020)': 'European Union'                                           
})

Hours_Jobs_URL = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/namq_10_a10_e/1.0/*.*.*.*.*.*?c[freq]=Q&c[unit]=THS_HW,THS_JOB&c[nace_r2]=TOTAL,A,B-E,C,F,G-I,J,K,L,M_N,O-Q,R-U&c[s_adj]=SCA&c[na_item]=EMP_DC&c[geo]=EU27_2020,EA,EA21,EA20,EA19,EA12,BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,NO,CH,UK,ME,MK,RS&c[TIME_PERIOD]=2026-Q1,2025-Q4,2025-Q3,2025-Q2,2025-Q1,2024-Q4,2024-Q3,2024-Q2,2024-Q1,2023-Q4,2023-Q3,2023-Q2,2023-Q1,2022-Q4,2022-Q3,2022-Q2,2022-Q1,2021-Q4,2021-Q3,2021-Q2,2021-Q1,2020-Q4,2020-Q3,2020-Q2,2020-Q1&compress=false&format=csvdata&formatVersion=1.0&lang=en&labels=label_only'

Hours_Jobs = pd.read_csv(Hours_Jobs_URL, usecols=['unit', 'nace_r2', 'geo', 'TIME_PERIOD', 'OBS_VALUE']).rename(columns={
        "nace_r2": "Industry",
        "geo": "Country",
        "TIME_PERIOD": "Quarter",
        "OBS_VALUE": "Value"
    })

Hours_Jobs['Country'] = Hours_Jobs['Country'].replace({
    'Euro area (EA11-1999, EA12-2001, EA13-2007, EA15-2008, EA16-2009, EA17-2011, EA18-2014, EA19-2015, EA20-2023, EA21-2026)': 'Euro Zone',
    'European Union - 27 countries (from 2020)': 'European Union'                                           
})

Hours = Hours_Jobs[Hours_Jobs['unit'] == 'Thousand hours worked'].drop(['unit'], axis=1)
Jobs = Hours_Jobs[Hours_Jobs['unit'] == 'Thousand jobs'].drop(['unit'], axis=1)

GVA_per_Hour = GVA_Chained.merge(
    Hours,
    on=['Country', 'Industry', 'Quarter'],
    suffixes=('_GVA', '_Hours')
).assign(GVA_per_Hour=lambda df: (df['Value_GVA'] / df['Value_Hours']) * 1000)[['Country', 'Industry', 'Quarter', 'GVA_per_Hour']]

GVA_per_Job = GVA_Chained.merge(
    Jobs,
    on=['Country', 'Industry', 'Quarter'],
    suffixes=('_GVA', '_Jobs')
).assign(GVA_per_Job=lambda df: (df['Value_GVA'] / df['Value_Jobs']) * 1000)[['Country', 'Industry', 'Quarter', 'GVA_per_Job']]


def rebase_to_2020(df, value_col):
    base = (
        df[df['Quarter'].str.startswith('2020')]
        .groupby(['Country', 'Industry'])[value_col]
        .mean()
        .rename('base')
    )
    return (
        df.join(base, on=['Country', 'Industry'])
        .assign(**{value_col: lambda d: (d[value_col] / d['base']) * 100})
        .drop(columns='base')
    )

def add_growth(df, value_col):
    filtered = (
        df[df['Country'].isin(key_countries) & df['Industry'].isin(key_industries)]
        .copy()
        .sort_values(['Country', 'Industry', 'Quarter'])
    )
    filtered['QoQ'] = filtered.groupby(['Country', 'Industry'])[value_col].pct_change(1) * 100
    filtered['YoY'] = filtered.groupby(['Country', 'Industry'])[value_col].pct_change(4) * 100
    return filtered


GVA_per_Hour_idx = rebase_to_2020(GVA_per_Hour, 'GVA_per_Hour')
GVA_per_Job_idx = rebase_to_2020(GVA_per_Job, 'GVA_per_Job')

with pd.ExcelWriter('EU_Figures/Sectoral_Productivity.xlsx', engine='openpyxl') as writer:
    add_growth(GVA_per_Hour_idx, 'GVA_per_Hour').to_excel(writer, sheet_name='Condensed - GVA per Hour', index=False)
    add_growth(GVA_per_Job_idx, 'GVA_per_Job').to_excel(writer, sheet_name='Condensed - GVA per Job', index=False)
    GVA_Chained.to_excel(writer, sheet_name='GVA_Chained', index=False)
    Hours.to_excel(writer, sheet_name='Thousand hours worked', index=False)
    Jobs.to_excel(writer, sheet_name='Thousand jobs', index=False)
    GVA_per_Hour.to_excel(writer, sheet_name='Sectoral GVA per Hour', index=False)
    GVA_per_Job.to_excel(writer, sheet_name='Sectoral GVA per Job', index=False)
    GVA_per_Hour_idx.to_excel(writer, sheet_name='GVA per Hour (2020=100)', index=False)
    GVA_per_Job_idx.to_excel(writer, sheet_name='GVA per Job (2020=100)', index=False)

print(GVA_per_Hour_idx)
print(GVA_per_Job_idx)