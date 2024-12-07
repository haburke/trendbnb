# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import sqlalchemy as sa

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import pandas as pd

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import db_query, engine


# -- helper functions --------------------------------------------------------------------------------------------------
def get_review_countries():
    df = db_query(engine, """
                  WITH ReviewData AS (
            SELECT 
                L.Country AS Country
            FROM 
                Listing L
                INNER JOIN Review R ON L.ListingID = R.ListingID
                INNER JOIN DetailedReview DR ON R.ListingID = DR.ListingID
        )
        SELECT Country, COUNT(Country) AS Count
        FROM ReviewData
        GROUP BY Country
        ORDER BY COUNT(Country) DESC
                  """)
    return df

# -- register page -----------------------------------------------------------------------------------------------------
page_name = "cleanliness"
register_page(__name__, path=page_info[page_name]["href"])

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        dbc.Card([
            navbar_main,

            html.Div(
                [
                    html.H5("Summary"),
                    html.P(

                        "By utilizing an extensive database with over 400,000 Airbnb listing records"
                    ),
                ], className="summary"
            ),

            # Graph
            dcc.Loading(
                dcc.Graph(id="cleanliness_graph"),
            ),

            # Country Select
            html.Div("Select Countries"),
            dcc.Dropdown(id='country-select',
                         options=get_review_countries().country,
                         multi=True,
                         clearable=True,
                         value=["France", "United States"]),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid",
                             'border-width': "1px", 'border-radius': 0}),
    ], className="dbc", fluid=True)

@callback(Output("cleanliness_graph", "figure"),
        [Input("country-select", "value")],
          )
def update_graph(countries):
    query = sa.text(""" WITH CleanYears AS(
                    SELECT EXTRACT(YEAR FROM l.FirstReview) AS Year, AVG(d.Cleanliness) AS CleanAvg
                    FROM "ANDREW.GOLDSTEIN".Listing l
                    JOIN "ANDREW.GOLDSTEIN".DetailedReview d ON l.ListingID=d.ListingID
                    WHERE Country=:CountryName AND d.Cleanliness IS NOT NULL AND l.LastReview IS NOT NULL
                    GROUP BY EXTRACT(YEAR FROM l.FirstReview)),
                    
                    CleanChange AS(
                    SELECT Year, CleanAvg, 
                    LAG(CleanAvg) OVER (ORDER BY Year) AS PrevYearCleanAvg
                    FROM CleanYears)
                    
                    SELECT Year, ROUND(CleanAvg, 2) AS CleanAvg, 
                    CASE
                        WHEN PrevYearCleanAvg IS NOT NULL THEN
                            ROUND((CleanAvg - PrevYearCleanAvg) / PrevYearCleanAvg * 100, 2)
                        ELSE
                            0
                        END AS PercentageChange
                    FROM CleanChange
                    ORDER BY Year
                    """)

    dfs = []
    for country in countries:
        params = {"CountryName": country}
        df_country = db_query(engine, query, params)
        df_country["country"] = country
        dfs.append(df_country)
    df_merged = pd.concat(dfs)

    fig = px.bar(data_frame=df_merged,
                 x=df_merged['year'],
                 y=df_merged['cleanavg'],
                 color=df_merged['country'],
                 barmode='group',
                 title="Cleanliness Change Over Time",
                 labels={'year': 'Year', 'cleanavg': 'Average Cleanliness'})
    for country in countries:
        fig.add_scatter(x=df_merged[df_merged.country == country]['year'],
                        y=df_merged[df_merged.country == country]['percentagechange'],
                        mode='lines+markers',
                        name=f'{country} % Change',
                        yaxis='y2')

    fig.update_layout(
        yaxis2=dict(
            title='Percentage Change',
            overlaying='y',
            side='right'
        ),
        yaxis=dict(tickmode='linear', tick0=df_merged['cleanavg'].min(), dtick=0.5)
    )

    fig.update_layout(template="plotly_dark")
    return fig

