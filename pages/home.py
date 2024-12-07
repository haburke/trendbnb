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
                        html.H5("Summary"),
                        html.P(
                            "By utilizing an extensive database with over 400,000 Airbnb listing records"
                        ),
                    ], className="summary"
                ),

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
