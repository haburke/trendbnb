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
from pages.utils import db_query

page_name = "home"

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


            # Total Tuples Graph
            dcc.Loading(
                dash_table.DataTable(
                    id='total-tuples-table',
                    columns=[{"name": i, "id": i} for i in ['Data Table']],
                    data=[{'Data Table': "Loading"}],
                    editable=True,
                    style_data={
                        'color': 'black',
                        'backgroundColor': 'white'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(220, 220, 220)',
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(210, 210, 210)',
                        'color': 'black',
                        'fontWeight': 'bold'
                    }
                ),
            ),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid", 
                             'border-width': "1px", 'border-radius': 0}), 

    ], className="dbc", fluid=True)

@callback(
    Output("avg-review-trend-graph", "figure"),
    [Input("avg-review-trend-graph", "data")],
)
def update_review_trend(figure):
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

    params = {"CityName": "Paris", "NumberOfYears": 15}
    df = db_query(query, params)

    fig = px.line(data_frame=df,
                  # x=df['reviewdate'],
                  y=df['avgreviewscore'], title="Average Review Trend", line_group=":CITYNAME",)
    tick_locs = np.where(df.reviewdate.astype(str).str.endswith(("01", "07")))[0]
    tick_text = [f"{v[0:4]}-{v[4:]}" for v in df.reviewdate.astype(str).values[tick_locs]]
    fig.update_layout(template="plotly_dark",
                      showlegend=True,
                      xaxis={'title': "Date",
                             'tickmode': 'array',
                             'tickvals': tick_locs,
                             'ticktext': tick_text,
                             'tickangle': 45},
                      yaxis={'title': f"Average Review Score for {params['CityName']}",})
    return fig

@callback(
    Output('total-tuples-table', 'data'),
    Output('total-tuples-table', 'columns'),
    Input('total-tuples-table', 'data'),
    prevent_initial_call=True
)
def update_graphs(value):
    from pages.utils import db_query
    table_names = ["Host", "Listing", "AirBnB", "Review", "DetailedReview"]
    results = {"TableName": [], "TupleCount": []}
    sum = 0
    for table in table_names:
        query = f"SELECT COUNT(*) AS TUPLE_COUNT FROM {table}"
        df = db_query(query)
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


if __name__ == '__main__':
    from utils import run_app, db_query

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])