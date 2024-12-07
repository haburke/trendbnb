# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

import numpy as np
# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
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


# -- register page -----------------------------------------------------------------------------------------------------
page_name = "home"
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

            # Reviews
            dcc.Loading(
                dcc.Graph(id="avg-review-trend-graph"),
            ),

            # City Select
            html.Div("Select Cities"),
            dcc.Dropdown(id='city-select',
                         options=get_review_cities().city,
                         multi= True,
                         clearable=True,
                         value=["Paris", "Brooklyn"]),

            # Total Tuples Graph
            html.Div("Total Tuples Table"),
            dcc.Loading(
                dash_table.DataTable(
                    id='total-tuples-table',
                    columns=[{"name": i, "id": i} for i in ['Data Table']],
                    data=[{'Data Table': "Loading"}],
                ),
            ),

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

@callback(
    Output('total-tuples-table', 'data'),
    Output('total-tuples-table', 'columns'),
    Input('total-tuples-table', 'data'),
)
def update_graphs(value):
    from pages.utils import db_query
    table_names = ["Host", "Listing", "AirBnB", "Review", "DetailedReview"]
    results = {"TableName": [], "TupleCount": []}
    sum = 0
    for table in table_names:
        query = f"SELECT COUNT(*) AS TUPLE_COUNT FROM {table}"
        df = db_query(engine, query)
        count = df.tuple_count.values[0]
        sum += count
        results["TableName"].append(table)
        results["TupleCount"].append(count)
    results["TableName"].append("Total")
    results["TupleCount"].append(sum)
    df = pd.DataFrame.from_dict(results)
    data = df.to_dict('records')
    columns = [{"name": i, "id": i} for i in df.columns]
    return data, columns
