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

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import db_query, engine

page_name = "cleanliness"

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        navbar_main,  # Place the navbar outside the input group
        # Input group for city search
        dbc.InputGroup(
            [
                dbc.Input(
                    id="country_input_1",
                    placeholder="Enter a country name here...",
                    type="text",
                    style={"width": "50%"}
                ),
                dbc.Button(
                    "Search",
                    id="country_search_button_1",
                    n_clicks=0,
                    color="primary",
                    style={"margin-left": "10px"}
                ),
            ],
            style={"margin-bottom": "20px"}
        ),
        dcc.Graph(id="cleanliness_graph"),
    ], className="dbc", fluid=True)

@callback(Output("cleanliness_graph", "figure"),
        [Input("country_search_button_1", "n_clicks")],
        [State("country_input_1", "value")],
          )
def update_graph(n_clicks, selected_country):
    if not selected_country:
        selected_city = "France"
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

    params = {"CountryName":selected_country}
    df = db_query(engine, query, params)

    if df.empty:
        fig = px.scatter(title=f"No data was found for the country: {selected_country}.")

    else:
        fig = px.bar(data_frame=df, x=df['year'], y=df['cleanavg'], title="Cleanliness Change Over Time",
                     labels={'year': 'Year', 'cleanavg': 'Average Cleanliness'})

        fig.add_scatter(x=df['year'], y=df['percentagechange'], mode='lines+markers', name='Cleanliness % Change', yaxis='y2')

        fig.update_layout(
            yaxis2=dict(
                title='Percentage Change',
                overlaying='y',
                side='right'
            ),
            yaxis=dict(tickmode='linear', tick0=df['cleanavg'].min(), dtick=0.5)
        )

    fig.update_layout(template="plotly_dark")
    return fig

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])
