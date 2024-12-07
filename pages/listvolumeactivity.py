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

page_name = "listvolumeactivity"

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
        dcc.Graph(id="list_volume_graph"),
    ], className="dbc", fluid=True)

@callback(Output("list_volume_graph", "figure"),
        [Input("city_search_button_4", "n_clicks")],
        [State("city_input_4", "value")],
          )
def update_graph(n_clicks, selected_city):
    if not selected_city:
        selected_city = "Paris"
    query = sa.text(""" MultipleListings AS (
                    SELECT h.HostID, h.Name, l.ListingID, l.City
                    FROM Host h
                    JOIN Listing l ON h.HostID = l.HostID
                    WHERE l.City = :CityName AND h.HostListingAmount > 1
                    GROUP BY h.HostID, h.Name, l.ListingID, l.City
                ),
                HostBookingFrequency AS (
                    SELECT ml.HostID, ml.Name, COUNT(r.ReviewID) AS TotalReviews,
                           ROUND(COUNT(r.ReviewID) / 12.0, 2) AS AvgMonthlyReviews
                    FROM MultipleListings ml
                    LEFT JOIN Review r ON ml.ListingID = r.ListingID
                    GROUP BY ml.HostID, ml.Name
                )
                SELECT HostID, Name, TotalReviews, AvgMonthlyReviews
                FROM HostBookingFrequency
                ORDER BY AvgMonthlyReviews DESC;
                    """)

    params = {"CityName":selected_city}
    df = db_query(query, params)

    if df.empty:
        fig = px.scatter(title=f"No data was found. Please enter a different specifications for city or year.")

    else:
        fig = px.line(data_frame=df, x=df[''], y=df['reviewcount'], title="Seasonality Trends Over Time")

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
