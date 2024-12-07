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
from pages.utils import db_query

page_name = "seasonality"

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
                    id="city_input_2",
                    placeholder="Enter a city name here...",
                    type="text",
                    style={"width": "50%"}
                ),
                dbc.Button(
                    "Search",
                    id="city_search_button_2",
                    n_clicks=0,
                    color="primary",
                    style={"margin-left": "10px"}
                ),
            ],
            style={"margin-bottom": "20px"}
        ),
        dcc.Dropdown(id='year_dropdown_1',
             options=[
                      {'label': '2012', 'value': (15*12)},
                      {'label': '2013', 'value': (14*12)},
                      {'label': '2014', 'value': (13*12)},
                      {'label': '2015', 'value': (12*12)},
                      {'label': '2016', 'value': (11*12)},
                      {'label': '2017', 'value': (10*12)},
                      {'label': '2018', 'value': (9*12)},
                      {'label': '2019', 'value': (8*12)},
                      {'label': '2020', 'value': (7*12)},
                      {'label': '2021', 'value': (6*12)}],
             value="2017",
             style={'width': "50%"}),
        # Graph for displaying results
        dcc.Graph(id="seasonality_graph"),
    ], className="dbc", fluid=True)

@callback(Output("seasonality_graph", "figure"),
        [Input("city_search_button_2", "n_clicks")],
        [State("city_input_2", "value")],
         [Input("year_dropdown_1", "value")]
          )
def update_graph(n_clicks, selected_city, selected_year):
    if not selected_city:
        selected_city = "Paris"
    query = sa.text("""WITH MonthlyReviewData AS (
                        SELECT 
                            L.City,
                            EXTRACT(MONTH FROM R.ReviewDate) AS ReviewMonth,
                            COUNT(R.ReviewID) AS ReviewCount
                        FROM 
                            "ANDREW.GOLDSTEIN".Review R
                            INNER JOIN "ANDREW.GOLDSTEIN".Listing L ON R.ListingID = L.ListingID
                        WHERE 
                            L.City = :CityName
                            AND R.ReviewDate >= ADD_MONTHS(SYSDATE, -1 * :Year)
                            AND R.ReviewDate < ADD_MONTHS(SYSDATE, (-1 * :Year)+12)
                        GROUP BY 
                            L.City, EXTRACT(MONTH FROM R.ReviewDate)
                    )
                    SELECT ReviewMonth, ReviewCount
                    FROM MonthlyReviewData
                    ORDER BY ReviewMonth DESC
                    """)

    params = {"CityName":selected_city, "Year":selected_year}
    df = db_query(query, params)

    if df.empty:
        fig = px.scatter(title=f"No data was found. Please enter a different specifications for city or year.")

    else:
        fig = px.line(data_frame=df, x=df['reviewmonth'], y=df['reviewcount'], title="Seasonality Trends Over Time",
                      labels={'reviewmonth': 'Review Month', 'reviewcount': 'Review Count'})

        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ),
            yaxis=dict(tickmode='linear', tick0=df['reviewcount'].min(), dtick=500)
        )

    fig.update_layout(template="plotly_dark")
    return fig

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])

