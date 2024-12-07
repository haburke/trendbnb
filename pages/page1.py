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

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import pandas as pd
import sqlalchemy as sa
import numpy as np

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import db_query, engine


# -- helper functions --------------------------------------------------------------------------------------------------
def get_listing_cities():
    df = db_query(engine, """
        SELECT City, COUNT(City) AS Count
        FROM Listing
        GROUP BY City
        ORDER BY COUNT(City) DESC
                  """)
    return df


# -- register page -----------------------------------------------------------------------------------------------------
page_name = "page1"
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
                        "This plot shows how many new users were added each month over the last several years."
                    ),
                ], className="summary"
            ),
            # Reviews
            dcc.Loading(
                dcc.Graph(id="num_host_graph"),
            ),

            # City Select
            html.Div("Select Cities"),
            dcc.Dropdown(id='city-select',
                         options=get_listing_cities().city,
                         multi=True,
                         clearable=True,
                         value=["London", "Paris"]),
        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid",
                             'border-width': "1px", 'border-radius': 0}),

    ], className="dbc", fluid=True)

@callback(Output("num_host_graph", "figure"),
        [Input("city-select", "value")]
          )
def update_graph(cities):
    query = sa.text("""
    WITH HostData AS (
        SELECT 
            H.HostID,
            EXTRACT(YEAR FROM H.HostSince) * 100 + EXTRACT(MONTH FROM H.HostSince) AS RegistrationDate,
            L.City
        FROM 
            Host H
            INNER JOIN Listing L ON H.HostID = L.HostID
        WHERE 
            L.City = :CityName
    )
    SELECT RegistrationDate, COUNT(DISTINCT HostID) AS NumberOfHosts
    FROM HostData
    WHERE RegistrationDate >= EXTRACT(YEAR FROM SYSDATE) * 100 + EXTRACT(MONTH FROM SYSDATE) - 10 * 100
    GROUP BY RegistrationDate
    ORDER BY RegistrationDate
    """)

    dfs = []
    for city in cities:
        params = {"CityName": city}
        df_city = db_query(engine, query, params)
        df_city = pd.DataFrame({"Date": df_city.registrationdate, city: df_city.numberofhosts})
        dfs.append(df_city)
    df_merged = dfs[0]
    for df_ in dfs[1:]:
        df_merged = df_merged.merge(df_, on="Date", how="outer")

    fig = px.line(data_frame=df_merged,
                      y=cities,
                      title="Number of New Hosts per Month")
    tick_locs = np.where(df_merged.Date.astype(str).str.endswith(("01", "04", "07")))[0]
    tick_text = [f"{v[0:4]}-{v[4:]}" for v in df_merged.Date.astype(str).values[tick_locs]]
    fig.update_layout(template="plotly_dark",
                      showlegend=True,
                      xaxis={'title': "Date",
                             'tickmode': 'array',
                             'tickvals': tick_locs,
                             'ticktext': tick_text,
                             'tickangle': 45},
                      yaxis={'title': f"Number of New Hosts", 'tickformat': "s%"},
                      )
    return fig
