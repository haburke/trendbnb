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

page_name = "avgreviewprice"

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
                    id="city_input_3",
                    placeholder="Enter a city name here...",
                    type="text",
                    style={"width": "50%"}
                ),
                dbc.Button(
                    "Search",
                    id="city_search_button_3",
                    n_clicks=0,
                    color="primary",
                    style={"margin-left": "10px"}
                ),
            ],
            style={"margin-bottom": "20px"}
        ),
        # Graph for displaying results
        dcc.Graph(id="avg_review_price_graph"),
    ], className="dbc", fluid=True)

@callback(Output("avg_review_price_graph", "figure"),
        [Input("city_search_button_3", "n_clicks")],
        [State("city_input_3", "value")]
          )
def update_graph(n_clicks, selected_city):
    if not selected_city:
        selected_city = "Paris"
    query = sa.text("""WITH ListingReviews AS (
                    SELECT l.ListingID, l.City, l.DailyPrice, AVG(dr.Rating) AS AverageRating
                    FROM Listing l
                    LEFT JOIN DetailedReview dr ON l.ListingID = dr.ListingID
                    WHERE l.City = :CityName
                    GROUP BY l.ListingID, l.City, l.DailyPrice
                ),
                PriceRanges AS (
                    SELECT CASE
                               WHEN DailyPrice < 50 THEN 1
                               WHEN DailyPrice BETWEEN 50 AND 150 THEN 2
                               ELSE 3
                           END AS PriceRange,
                           AVG(AverageRating) AS AvgRating
                    FROM ListingReviews
                    GROUP BY CASE
                               WHEN DailyPrice < 50 THEN 1
                               WHEN DailyPrice BETWEEN 50 AND 150 THEN 2
                               ELSE 3
                           END
                )
                SELECT PriceRange, ROUND(AvgRating, 2) AS AverageRating
                FROM PriceRanges
                ORDER BY PriceRange
                    """)

    params = {"CityName":selected_city}
    df = db_query(query, params)

    if df.empty:
        fig = px.scatter(title=f"No data was found. Please enter a different specifications for city or year.")

    else:
        fig = px.line(data_frame=df, x=df['pricerange'], y=df['averagerating'], title="Listing Price and Average Review Score Rating",
                      labels={'pricerange': 'Price Range', 'averagerating': 'Average Rating'})

        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 4)),
                ticktext=['Low', 'Medium', 'High']
            ),
            yaxis=dict(tickmode='linear', tick0=df['averagerating'].min(), dtick=0.25)
        )

    fig.update_layout(template="plotly_dark")
    return fig

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])
