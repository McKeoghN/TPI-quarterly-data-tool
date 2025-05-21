# Script made for making visualisation for different datasets

import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import sys
# sys.path.append("../") # So I can import functions from the streamlit script, makes the bargraphs black and white though?
# from Streamlit_application import quarter_to_numeric, numeric_to_quarter

TPI_colours = ["#eb5e5e", "#03979d", "#9c4f8b"] # peachy colour, greeny blue, lighter purple
# TPI_colours = ["#6C2283", "#39A7DF"] # dark purple, blue
TPI_One = "#03979d"
TPI_Two = "#eb5e5e"

def rebase_chain_linked_quarters(data, new_base_year):
    data = data.copy()
    
    # Extract year from Quarter (e.g., 1997.25 -> 1997)
    data["Year"] = data["Quarter"].astype(int)

    def rebase_group(group):
        # Get the mean of the base year for this group
        base_year_values = group[group["Year"] == new_base_year]["Value"]
        if base_year_values.empty or base_year_values.mean() == 0:
            return group  # Skip group if base year is missing or zero
        base_mean = base_year_values.mean()
        group["Value"] = (group["Value"] / base_mean) * 100
        return group

    # Apply rebase per group
    data = data.groupby(["Country", "Industry", "Variable"], group_keys=False).apply(rebase_group)

    # Drop temporary year column
    data = data.drop(columns="Year")

    return data

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
        title="",
        labels={"value": f"{yAxisTitle}", "variable": f"{legendTitle}"},
        color_discrete_sequence=TPI_colours)

        tickvals = [q for q in data['Quarter'] if q.endswith("Q1")]

        fig.update_xaxes(tickvals=tickvals)

        return fig

def qoq(data, title, legendTitle):
        # data = data[['Quarter', 'OPH']]
        # data["quarter_numeric"] = data["Quarter"].apply(quarter_to_numeric)
        # data = data[(data["quarter_numeric"] >= 2022 - 0.25) & (data["quarter_numeric"] <= 2024.75)]
        # data = data.drop('quarter_numeric', axis=1)
        data = data.melt(id_vars = "Quarter", var_name = f"{legendTitle}")
        data["QoQ Growth (%)"] = data.groupby(f"{legendTitle}")["value"].pct_change().mul(100).round(2)

        data = data.dropna()
        fig = px.bar(data, 
                     x="Quarter", 
                     y="QoQ Growth (%)", 
                     color=f"{legendTitle}",
                     color_discrete_sequence=TPI_colours,
                     barmode="group", 
                     title=f"{title}")
        # fig.update_layout(showlegend=False)
        fig.update_xaxes(title=None)
        return fig

def double_qoq(data, data_two, title, legendTitle, leftTitle, rightTitle):
        # data = data[['Quarter', 'OPH']]
        # data["quarter_numeric"] = data["Quarter"].apply(quarter_to_numeric)
        # data = data[(data["quarter_numeric"] >= 2022 - 0.25) & (data["quarter_numeric"] <= 2024.75)]
        # data = data.drop('quarter_numeric', axis=1)
        data = data.melt(id_vars = "Quarter", var_name = f"{legendTitle}")
        data["QoQ Growth (%)"] = data.groupby(f"{legendTitle}")["value"].pct_change().mul(100).round(2)
        data = data.dropna()

        data_two = data_two.melt(id_vars = "Quarter", var_name = f"{legendTitle}")
        data_two["QoQ Growth (%)"] = data_two.groupby(f"{legendTitle}")["value"].pct_change().mul(100).round(2)
        data_two = data_two.dropna()

        # Create subplots with 1 row and 2 columns
        fig = make_subplots(
            rows=1, cols=2, 
            subplot_titles=[f"{leftTitle}", f"{rightTitle}"]
        )

        # Add the first bar chart to the first subplot
        fig1 = px.bar(data, 
                     x="Quarter", 
                     y="QoQ Growth (%)", 
                     color=f"{legendTitle}",
                     color_discrete_sequence=TPI_colours,
                     barmode="group", 
                     title=f"{title}")

        # Add the second bar chart to the second subplot
        fig2 = px.bar(data_two, 
                     x="Quarter", 
                     y="QoQ Growth (%)", 
                     color=f"{legendTitle}",
                     color_discrete_sequence=TPI_colours,
                     barmode="group", 
                     title=f"{title}")
        
        for trace in fig1.data:
            fig.add_trace(trace, row=1, col=1)
        legend_labels = set(trace.name for trace in fig1.data)
        for trace in fig2.data:
            if trace.name in legend_labels:
                trace.showlegend = False  # Hide from legend
            else:
                legend_labels.add(trace.name)
            fig.add_trace(trace, row=1, col=2)

        # Update layout for the subplots
        fig.update_layout(
            title=title,
            # xaxis_title="Quarter",
            yaxis_title="QoQ Growth (%)",
            legend_title="Method",
            barmode="group",  # Group bars within each subplot
        )

        # Update x-axis titles for each subplot
        fig.update_xaxes(title_text="", row=1, col=1)
        fig.update_xaxes(title_text="", row=1, col=2)

        # Update y-axis titles for each subplot
        fig.update_yaxes(title_text="QoQ Growth (%)", row=1, col=1)
        fig.update_yaxes(title_text="QoQ Growth (%)", row=1, col=2)

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
        fig.update_xaxes(showtitle=False)
        return fig

def horizontal_bar(data, title):
    data = data.dropna()
    data.drop(data.index[0], inplace=True)
    data = data.sort_values(by='Contribution')
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=data['Industry'],
        x=data['Contribution'],
        orientation='h',
        marker=dict(
            color=[TPI_One if x > 0 else TPI_Two for x in data['Contribution']],
            line=dict(color='black', width=0.5)
        ), 
        width=[w / max(data['Size']) * 0.9 for w in data['Size']],  # Normalise bar thickness
    ))

    pos_data = data[data['Contribution'] >= 0]
    neg_data = data[data['Contribution'] < 0]

    # Positive annotations
    for i, row in pos_data.iterrows():
        fig.add_annotation(
            x=row['Contribution'],
            y=row['Industry'],
            text=f"{row['Contribution']:.1%}",
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor="left",
            xshift=5,  # spacing from end of bar
            yshift=0
        )

    # Negative annotations
    for i, row in neg_data.iterrows():
        fig.add_annotation(
            x=row['Contribution'],
            y=row['Industry'],
            text=f"{row['Contribution']:.1%}",
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor="right",
            xshift=0,  # spacing from end of bar
            yshift=0
        )

    fig.update_layout(
        title=f'{title}',
        xaxis_title='Contribution to OPH, percentage point change',
        yaxis_title='',
        bargap=0.15,
        template='simple_white',
        height=400 + len(data) * 20,
        xaxis=dict(
            tickformat=".1%",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray'
        ),
        yaxis=dict(
            tickfont=dict(
                size=15,
            )
        )
    )
    return fig

def OPH(data, title):
    data['Output per hour worked'] *= 100
    data['GVA'] *= 100
    data['Hours worked'] *= 100
    # data.drop(data.index[0], inplace=True)
     # Create subplots with shared y-axis
    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.05,
        subplot_titles=(
            "Change in <b>output per hour worked</b>",
            "Change in <b>GVA</b> and <b>hours worked</b>"
        )
    )
    left_chart_data = data.sort_values(by='Output per hour worked', ascending=False)
    # Left chart: Productivity
    fig.add_trace(
        go.Bar(
            x=left_chart_data['Output per hour worked'],
            y=left_chart_data['Industry'],
            orientation='h',
            name='Productivity',
            marker_color=TPI_colours[0],
            text=left_chart_data['Output per hour worked'].map(lambda x: f"{x:.1f}%"),
            textposition='auto'
        ),
        row=1, col=1
    )

    # Right chart: GVA and Hours Worked
    fig.add_trace(
        go.Bar(
            x=data['GVA'],
            y=data['Industry'],
            orientation='h',
            name='GVA',
            marker_color=TPI_colours[1]
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            x=data['Hours worked'],
            y=data['Industry'],
            orientation='h',
            name='Hours Worked',
            marker_color=TPI_colours[2]
        ),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(
        height=1000,
        barmode='group',
        title_text=f'{title}',
        showlegend=True,
        legend=dict(x=0.65, y=1.1, orientation='h'),
        margin=dict(l=120, r=20, t=60, b=20),
    )

    # Center x-axes at zero
    fig.update_xaxes(title_text="", range=[-35, 35], row=1, col=1, zeroline=True)
    fig.update_xaxes(title_text="", range=[-35, 35], row=1, col=2, zeroline=True)

    # Reverse y-axis for top-to-bottom sorting (optional)
    fig.update_yaxes(autorange='reversed')
    return fig

def New_GDP(data):
    custom_colours = [TPI_One if g >= 0 else TPI_Two for g in data['Growth']]
    fig = go.Figure(go.Bar(
        x=data['Growth'],
        y=data['Country'],
        orientation='h',
        marker_color=custom_colours,
        text=data['Note'],
        hovertemplate='%{y}: %{x}%<br>%{text}<extra></extra>'
    ))

    fig.update_layout(
        title="",
        xaxis_title="Growth Rate (%)",
        yaxis_title="",
        template="plotly_white"
    )
    return fig

# # Flash_Estimate = pd.read_csv('../src/New-release/OPH Q1 2025.csv', skiprows=7, usecols=[0,1,2,3], names=["Quarter", "GVA", "Hours Worked", "OPH"])
# # # Change from Q4 1997 to 1997 Q4
# # Flash_Estimate["Quarter"] = Flash_Estimate["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)

# # fig = line_graph(Flash_Estimate, 1997)
# # # fig = qoq(Flash_Estimate)
# # # fig = yoy(Flash_Estimate)

# # fig.update_layout(template="plotly_white")

# # fig.show()

Flash_Estimate_OPH = pd.read_csv('../src/New-release/OPH Q1 2025.csv', skiprows=7, usecols=[0,1,2,3], names=["Quarter", "Gross Value Added", "Hours Worked", "Output Per Hour"])
Flash_Estimate_OPH["Quarter"] = Flash_Estimate_OPH["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# Flash_Estimate_OPH["Quarter"] = Flash_Estimate_OPH["Quarter"].apply(quarter_to_numeric)
# Flash_Estimate_OPH = pd.melt(Flash_Estimate_OPH, id_vars=['Quarter'], var_name='Variable', value_name='Value')
# Flash_Estimate_OPH['Country'] = 'UK Flash Estimate'
# Flash_Estimate_OPH['Industry'] = 'Total'
# Flash_Estimate_OPH['Variable'] = 'Flash Estimate Output per Hour'
# Flash_Estimate_OPH = rebase_chain_linked_quarters(Flash_Estimate_OPH, 2020)
base_value = Flash_Estimate_OPH.loc[Flash_Estimate_OPH["Quarter"] == "2007 Q1", "Gross Value Added"].iloc[0]
Flash_Estimate_OPH["Gross Value Added"] = (Flash_Estimate_OPH["Gross Value Added"] / base_value) * 100

base_value = Flash_Estimate_OPH.loc[Flash_Estimate_OPH["Quarter"] == "2007 Q1", "Hours Worked"].iloc[0]
Flash_Estimate_OPH["Hours Worked"] = (Flash_Estimate_OPH["Hours Worked"] / base_value) * 100

base_value = Flash_Estimate_OPH.loc[Flash_Estimate_OPH["Quarter"] == "2007 Q1", "Output Per Hour"].iloc[0]
Flash_Estimate_OPH["Output Per Hour"] = (Flash_Estimate_OPH["Output Per Hour"] / base_value) * 100

Flash_Estimate_OPH["Quarter"] = Flash_Estimate_OPH["Quarter"].apply(quarter_to_numeric)
Flash_Estimate_OPH = Flash_Estimate_OPH[(Flash_Estimate_OPH['Quarter'] >= 2007) & (Flash_Estimate_OPH['Quarter'] <= 2025)]
Flash_Estimate_OPH["Quarter"] = Flash_Estimate_OPH["Quarter"].apply(numeric_to_quarter)
fig = line_graph(Flash_Estimate_OPH, 2007, "", "", "")
fig.show()
fig.write_image("../out/visualisations/Q1 2025 Flash Estimate.png", width=1200, height=800, scale=2)

# # Dataset = pd.read_csv('../out/Long_Dataset.csv')
# # Dataset = pd.concat([Dataset, Flash_Estimate_OPH])
# # Dataset.to_csv("../out/Long_Dataset.csv", index=False)

# # OPH_Comparison = pd.read_csv('../src/New-release/OPH LFS vs RTI.csv', skiprows=7, usecols=[0,1,2], names=["Quarter", "LFS Output per hour worked", "RTI + SE (exc working proprietors) Output per hour worked"])
# # OPH_Comparison["Quarter"] = OPH_Comparison["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# # OPH_Comparison["Quarter"] = OPH_Comparison["Quarter"].apply(quarter_to_numeric)
# # OPH_Comparison = pd.melt(OPH_Comparison, id_vars=['Quarter'], var_name='Variable', value_name='Value')
# # OPH_Comparison['Country'] = 'UK Flash Estimate'
# # OPH_Comparison['Industry'] = 'Total'
# # print(OPH_Comparison)
# # Dataset = pd.read_csv('../out/Long_Dataset.csv')
# # Dataset = pd.concat([Dataset, OPH_Comparison])
# # Dataset.to_csv("../out/Long_Dataset.csv", index=False)

# # Flash_Estimate_OPH['Variable'] = 'Flash Estimate Output per Hour'
# # OPH_Comparison = rebase_chain_linked_quarters(OPH_Comparison, 2020)
# # # fig = qoq(Flash_Estimate)
# # # fig = yoy(Flash_Estimate)

# QOQ bar graphs:
# OPH_Comparison = pd.read_csv('../src/New-release/OPH LFS vs RTI.csv', skiprows=7, usecols=[0,1,2], names=["Quarter", "LFS Output per hour worked", "RTI + SE (exc working proprietors) Output per hour worked"])
# OPH_Comparison["Quarter"] = OPH_Comparison["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# OPH_Comparison['Quarter'] = OPH_Comparison['Quarter'].apply(quarter_to_numeric)

# preCovidOPH = OPH_Comparison.copy()
# preCovidOPH = preCovidOPH[(preCovidOPH['Quarter'] >= 2014.75) & (preCovidOPH['Quarter'] <= 2019)]
# preCovidOPH['Quarter'] = preCovidOPH['Quarter'].apply(numeric_to_quarter)

# postCovidOPH = OPH_Comparison.copy()
# postCovidOPH = postCovidOPH[(postCovidOPH['Quarter'] >= 2021) & (postCovidOPH['Quarter'] <= 2025)]
# postCovidOPH['Quarter'] = postCovidOPH['Quarter'].apply(numeric_to_quarter)

# fig = double_qoq(preCovidOPH, postCovidOPH, "", "legend", "Output per hour worked pre-COVID", "Output per hour worked post-COVID")
# fig.write_image("../out/visualisations/OPH - LFS vs RTI - double.png", width=1200, height=800, scale=2)
# fig.show()

# OPW_Comparison = pd.read_csv('../src/New-release/OPW LFS vs RTI.csv', skiprows=7, usecols=[0,1,2], names=["Quarter", "LFS Output per hour worked", "RTI + SE (exc working proprietors) Output per hour worked"])
# OPW_Comparison["Quarter"] = OPW_Comparison["Quarter"].str.replace(r"(Q\d) (\d{4})", r"\2 \1", regex=True)
# OPW_Comparison['Quarter'] = OPW_Comparison['Quarter'].apply(quarter_to_numeric)

# preCovidOPW = OPW_Comparison.copy()
# preCovidOPW = preCovidOPW[(preCovidOPW['Quarter'] >= 2014.75) & (preCovidOPW['Quarter'] <= 2019)]
# preCovidOPW['Quarter'] = preCovidOPW['Quarter'].apply(numeric_to_quarter)

# postCovidOPW = OPW_Comparison.copy()
# postCovidOPW = postCovidOPW[(postCovidOPW['Quarter'] >= 2021) & (postCovidOPW['Quarter'] <= 2025)]
# postCovidOPW['Quarter'] = postCovidOPW['Quarter'].apply(numeric_to_quarter)

# fig = double_qoq(preCovidOPW, postCovidOPW, "", "legend", "Output per worker pre-COVID", "Output per worker post-COVID")
# fig.write_image("../out/visualisations/OPW - LFS vs RTI - double.png", width=1200, height=800, scale=2)
# fig.show()

# fig = qoq(OPH_Comparison, "", "OPH Method")
# fig.show()
# fig.write_image("../out/visualisations/OPH - LFS vs RTI.png", width=1200, height=800, scale=2)
# fig = qoq(OPW_Comparison, "", "OPW Method")
# fig.show()
# # fig.write_image("../out/visualisations/OPW LFS vs RTI.png", width=1200, height=800, scale=2)
# fig = double_qoq(OPH_Comparison, OPW_Comparison, "OPH and OPW calculated using LFS vs RTI + SE QoQ growth (%)", "Method")
# # # fig.write_image("../out/visualisations/OPH and OPW LFS vs RTI.png", width=1200, height=800, scale=2)
# fig.show()

# OPH_Industries = pd.read_excel('../src/New-release/Contribution To OPH.xlsx', skiprows=11, usecols=[0,1, 2], names=["Industry", "Contribution", "Size"])
# fig = horizontal_bar(OPH_Industries, "")
# fig.write_image("../out/visualisations/Contribution to OPH by Industry.png", width=1200, height=800, scale=2)
# fig.show()

# OPH_Breakdown = pd.read_excel('../src/New-release/GVA OPH HW.xlsx', skiprows=6, usecols=[0,1,2,3])
# fig = OPH(OPH_Breakdown, "")
# fig.write_image("../out/visualisations/OPH GVA HW.png", width=1200, height=800, scale=2)
# fig.show()

# GDPdata = {
#     "Country": ["UK", "Canada", "Italy", "Germany", "France", "Japan", "US"],
#     "Growth": [0.7, 0.4, 0.3, 0.2, 0.1, -0.2, -0.3],
#     "Note": ["0.7%", "0.4%*", "0.3%", "0.2%", "0.1%", "-0.2%", "-0.3%"],
#     "Colour": ["green", "green", "green", "green", "green", "red", "red"]
# }

# GDPdata = pd.DataFrame(GDPdata)
# GDPdata = GDPdata.sort_values(by="Growth", ascending=True)
# fig = New_GDP(GDPdata)
# fig.write_image("../out/visualisations/Q1 GDP.png", width=1200, height=800, scale=2)
# fig.show()