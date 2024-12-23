# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, dash_table

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import engine


# -- helper functions --------------------------------------------------------------------------------------------------


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
                        html.H5("Application Overview"),
                        html.P(
                    
                            "Trendbnb is a data dashboard that visualizes historical "
	                        "Airbnb trends such as pricing, seasonality, host behavior, and "
	                        "review scores across many cities worldwide. These insights assist "
	                        "potential Airbnb hosts, real estate agents, property managers, and "
	                        "local legislators in making informed decisions regarding short-term rentals."
                        ),
                    ], className="summary"
                ),

            dbc.Row([
                dbc.Col([
                    # Total Tuples Graph
                    html.Div("Total Tuples Table"),
                    dcc.Loading(
                        dash_table.DataTable(
                            id='total-tuples-table',
                            columns=[{"name": i, "id": i} for i in ['Data Table']],
                            data=[{'Data Table': "Loading"}],
                        ),
                    )],
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H5("Data Sources"),
                            html.P([
                                "Our listing data is sourced from ",
                                html.A("Airbnb Global",
                                       href="https://www.kaggle.com/datasets/joebeachcapital/airbnb",
                                       className="link"),
                                " Listings, containing information on more than 400,000 Airbnb listings worldwide.",
                                html.Br(),
                                "The Airbnb review data we use is sourced from ",
                                html.A("Airbnb Listings",
                                       href="https://www.kaggle.com/datasets/mysarahmadbhat/airbnb-listings-reviews",
                                       className="link"),
                                " & Reviews, containing data for 250,000+ listings across 10 major cities.",
                                html.Br(),
                                "Both datasets are publicly available on Kaggle."]
                            ),
                        ], className="summary2"
                    ),
                )
            ]),

            html.Div(
                [
                    html.H5("Contributors"),
                    html.P([
                        "Heather Burke",
                        html.Br(),
                        "Andrew Goldstein",
                        html.Br(),
                        "Bayron Najera",
                        html.Br(),
                        "Anthony Pallitta"
                    ]),
                ], className="summary"
            ),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid", 
                             'border-width': "1px", 'border-radius': 0}), 

    ], className="dbc", fluid=True)


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
