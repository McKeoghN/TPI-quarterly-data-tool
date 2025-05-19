import pandas as pd
import plotly.express as px

def rebase_chain_linked_years(df, new_base_year):
    df = df.copy()
    
    def rebase_group(group):
        base_year_values = group[group["Year"] == new_base_year]["Value"]
        if base_year_values.empty or base_year_values.mean() == 0:
            return group  # Skip group if base year is missing or zero
        base_mean = base_year_values.mean()
        group["Value"] = (group["Value"] / base_mean) * 100
        return group

    # Apply rebase per group
    df = df.groupby(["Country", "Variable"], group_keys=False).apply(rebase_group)

    return df

df = pd.read_csv('../out/OPH_Processed.csv')
# df = df.query("Country not in ['OECD Total', 'Euro Area', 'European Union', 'Russia', 'G7'] and Year >= 2010")
countries = ['Denmark', 'Finland','France', 'Germany', 'Ireland', 'Italy', "Belgium",
             'Netherlands', 'Norway', 'Poland', 'Portugal',  'Spain', 'Sweden', 'Switzerland', 'UK', 'US']
df = df.query(f"Country in {countries}")
print(df['Country'].unique())
# df = df[~df['Country'].isin(['OECD Total', 'Euro Area', 'European Union', 'Russia'])]

# df = df[df['Year'] == 2022]

df['Country'] = df['Country'].replace({
    'US': 'United States',
    'UK': 'United Kingdom',
})

df = rebase_chain_linked_years(df, 1999)
print(df)

df["YoY Growth (%)"] = df.groupby("Country")["Value"].pct_change().mul(100).round(2)
df = df.query("Year >= 2000")
print(df)

# fig = px.choropleth(
#     df,
#     locations="Country",
#     locationmode="country names",
#     color="Value",
#     scope="europe",  # Shows Europe only — remove or set to 'world' to show the US
#     color_continuous_scale="Viridis"
# )

# Eastern Europe on top map
# fig = px.choropleth(
#     df,
#     locations="Country",
#     locationmode="country names",
#     color="Value",
#     animation_frame="Year",
#     scope="world",  # Keep the world scope to show both US and Europe
#     color_continuous_scale="Plasma",
#     range_color=[100, 300],  # Adjust the color range for better visibility
#     title="Output per hour worked in the US and Europe (2000-2022), CLV 2000=100",
# )

# # Adjust the map to focus on the US and Europe
# fig.update_geos(
#     projection_type="natural earth",
#     visible=True,
#     resolution=50,
#     showcountries=True,
#     lataxis_range=[20, 70],  # Latitude range to focus on US and Europe
#     lonaxis_range=[-130, 40],  # Longitude range to focus on US and Europe
# )

# Yoy growth map
fig = px.choropleth(
    df,
    locations="Country",
    locationmode="country names",
    color="YoY Growth (%)",
    animation_frame="Year",
    scope="world",  # Keep the world scope to show both US and Europe
    color_continuous_scale="Plasma",
    range_color=[1, 4],  # Adjust the color range for better visibility
    title="OECD GDP per hour worked year on year growth in the US and Europe (2000-2022)",
)

# Adjust the map to focus on the US and Europe
fig.update_geos(
    projection_type="natural earth",
    visible=True,
    resolution=50,
    showcountries=True,
    lataxis_range=[20, 70],  # Latitude range to focus on US and Europe
    lonaxis_range=[-130, 40],  # Longitude range to focus on US and Europe
)

fig.show()
fig.write_html('../out/Europe+US Choropeth.html')