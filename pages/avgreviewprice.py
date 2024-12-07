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
page_name = "avgreviewprice"
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
                dcc.Graph(id="avg_review_price_graph"),
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


@callback(Output("avg_review_price_graph", "figure"),
          [Input("city-select", "value")],
          )
def update_graph(cities):
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

    params = {"CityName": cities[0]}
    df = db_query(engine, query, params)

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
