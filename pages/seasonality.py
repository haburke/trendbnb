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
import numpy as np
import pandas as pd
import sqlalchemy as sa

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import db_query, engine


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


def get_review_years():
    df = db_query(engine,
                  """
                SELECT
                    DISTINCT EXTRACT(YEAR FROM ReviewDate) AS YEAR
                FROM
                    Review
                ORDER BY YEAR
                  """)
    return df


def norm(array):
    return (array-array.min())/(array.max()-array.min())


# -- register page -----------------------------------------------------------------------------------------------------
page_name = "seasonality"
register_page(__name__, path=page_info[page_name]["href"])

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        dbc.Card([
            navbar_main,

            # Summary Div
            html.Div(
                [
                    html.H5("Description"),
                    html.P(
                        """
                        We are looking at the number of reviews over a given month aggregated across
                        years in order to look at the trends in seasonal changes in a given city. 
                        """
                    ),

                    html.H5("Motivation"),
                    html.P(
                        """
                        This analysis could be useful for a legislator to coordinate citywide events 
                        at peak times of tourist visitation. It could also help agents coordinate with the needs 
                        of a client who are looking for a summer home they can rent out in the winter.
                        """
                    )
                ], className="summary"
            ),

            # Graph for displaying results
            dcc.Loading(
                dcc.Graph(id="seasonality_graph"),
            ),

            # City Select
            html.Div("Select Cities"),
            dcc.Dropdown(id='city-select',
                         options=get_review_cities().city,
                         multi=True,
                         clearable=True,
                         value=["Paris", "Brooklyn"]),

            # Year Select
            html.Div("Select Years"),
            dcc.Dropdown(id='year-select',
                         options=get_review_years().year,
                         multi=True,
                         clearable=False,
                         value=[2020, 2021]),

            # Normalize Select
            dcc.Checklist(
                id='normalize',
                options=[{'label': 'Normalize (MinMax)', 'value': 'norm'}],
                value=[]
            ),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid",
                             'border-width': "1px", 'border-radius': 0}),
    ], className="dbc", fluid=True)


@callback(Output("seasonality_graph", "figure"),
          [Input("city-select", "value"),
           Input("year-select", "value"),
           Input("normalize", "value")],
          )
def update_graph(cities, years, normalize):
    normalize = len(normalize) > 0
    query = sa.text("""
    WITH MonthlyReviewData AS (
        SELECT 
            L.City,
            EXTRACT(MONTH FROM R.ReviewDate) AS ReviewMonth,
            COUNT(R.ReviewID) AS ReviewCount
        FROM 
            Review R
            INNER JOIN Listing L ON R.ListingID = L.ListingID
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
    dfs = []
    for city in cities:
        months = None
        reviews = None
        for year in years:
            params = {"CityName": city, "Year": (2027-year)*12}
            df = db_query(engine, query, params)
            if months is None:
                months = df.reviewmonth
            if reviews is None:
                reviews = [df.reviewcount]
            else:
                reviews.append(df.reviewcount)

        df_city = pd.DataFrame({"Month": months,
                                city: norm(np.nansum(reviews, axis=0)) if normalize else np.nanmean(reviews, axis=0)})
        dfs.append(df_city)
    df_merged = dfs[0]
    for df_ in dfs[1:]:
        df_merged = df_merged.merge(df_, on="Month", how="outer")

    fig = px.line(data_frame=df_merged,
                  y=cities,
                  title=f"Seasonality Trends Over Time {"(Normalized)" if normalize else ""}",)
    fig.update_layout(template="plotly_dark",
                      showlegend=True,
                      xaxis={'title': "Month",
                             'tickmode': 'array',
                             'tickvals': list(range(0, 11)),
                             'ticktext': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                             'tickangle': 45},
                      yaxis={'title': f"Reviewed Listings {"[arb.]" if normalize else "[Count]"}",
                             'tickformat': "%.0f" if normalize else ""},
                      )
    return fig
