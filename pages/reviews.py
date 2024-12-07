# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import sqlalchemy as sa
import numpy as np
import pandas as pd

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import get_data, get_table, db_query, engine


# -- helper functions --------------------------------------------------------------------------------------------------
def get_review_cities():
    df = db_query(engine, """
                  WITH ReviewData AS (
            SELECT 
                L.City AS City
            FROM 
                Listing L
                INNER JOIN Review R ON L.ListingID = R.ListingID
                INNER JOIN DetailedReview DR ON R.ListingID = DR.ListingID
        )
        SELECT City, COUNT(City) AS Count
        FROM ReviewData
        GROUP BY City
        ORDER BY COUNT(City) DESC
                  """)
    return df


# -- register page -----------------------------------------------------------------------------------------------------
page_name = "reviews"
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
                        "By utilizing an extensive database with over 400,000 Airbnb listings, this dashboard"
                        "offers visualization of complex trends that can help inform hosts, real estate agents,"
                        "property managers, and local legislators about Airbnb listing data. Our trend analysis"
                        "provides insights into local markets."
                    ),
                ], className="summary"
            ),

            # Reviews
            dcc.Loading(
                dcc.Graph(id="avg-review-trend-graph"),
            ),

            # City Select
            html.Div("Select Cities"),
            dcc.Dropdown(id='city-select',
                         options=get_review_cities().city,
                         multi=True,
                         clearable=True,
                         value=["Paris", "Brooklyn"]),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid",
                             'border-width': "1px", 'border-radius': 0}),

    ], className="dbc", fluid=True)


@callback(
    Output("avg-review-trend-graph", "figure"),
    [Input("city-select", "value")],
)
def update_review_trend(cities):
    query = sa.text("""
    WITH ReviewData AS (
        SELECT 
            L.City,
            EXTRACT(YEAR FROM R.ReviewDate) * 100 + EXTRACT(MONTH FROM R.ReviewDate) AS ReviewDate,
            DR.Rating
        FROM 
            Listing L
            INNER JOIN Review R ON L.ListingID = R.ListingID
            INNER JOIN DetailedReview DR ON R.ListingID = DR.ListingID
        WHERE 
            L.City = :CityName
    )
    SELECT :CityName, ReviewDate, AVG(Rating) AS AvgReviewScore
    FROM ReviewData
    WHERE ReviewDate >= EXTRACT(YEAR FROM SYSDATE) * 100 + EXTRACT(MONTH FROM SYSDATE) - :NumberOfYears * 100
    GROUP BY ReviewDate
    ORDER BY ReviewDate""")
    dfs = []
    for city in cities:
        params = {"CityName": city, "NumberOfYears": 15}
        df_city = db_query(engine, query, params)
        df_city = pd.DataFrame({"Date": df_city.reviewdate, city: df_city.avgreviewscore})
        dfs.append(df_city)
    df_merged = dfs[0]
    for df_ in dfs[1:]:
        df_merged = df_merged.merge(df_, on="Date", how="outer")


    fig = px.line(data_frame=df_merged,
                  y=cities,
                  title="Average Review Trend")
    tick_locs = np.where(df_merged.Date.astype(str).str.endswith(("01", "07")))[0]
    tick_text = [f"{v[0:4]}-{v[4:]}" for v in df_merged.Date.astype(str).values[tick_locs]]
    fig.update_layout(template="plotly_dark",
                      showlegend=True,
                      xaxis={'title': "Date",
                             'tickmode': 'array',
                             'tickvals': tick_locs,
                             'ticktext': tick_text,
                             'tickangle': 45},
                      yaxis={'title': f"Average Review Score per Month", 'tickformat': "s%"},
                      )
    return fig
