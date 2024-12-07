# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import get_data, get_table, db_query

page_name = "about"

# -- plotly figs -------------------------------------------------------------------------------------------------------
x, y = get_data()
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
fig.update_layout(template="plotly_dark")

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

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

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid", 
                             'border-width': "1px", 'border-radius': 0}), 

    ], className="dbc", fluid=True)
    
# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [

        dbc.Card(
            [ 
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

            ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid", 
                             'border-width': "1px", 'border-radius': 0}), 

    ], className="dbc", fluid=True)

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])