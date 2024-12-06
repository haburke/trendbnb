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
from pages.utils import get_data, get_table

page_name = __file__.split("/")[-1].split(".py")[0]

# -- plotly figs -------------------------------------------------------------------------------------------------------
x, y = get_data()
values, headers = get_table()
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
fig.update_layout(template="plotly_dark")

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        header(page_info[page_name]["page-title"]),

        dbc.Card([ 
            navbar_main,
            html.Div([
                dcc.Markdown(children='''
                # About Trendbnb 
                
                ---

                ##### LINKS
                * Database Source: 

                ##### Project Contributors

                ''')
            ], style={'padding': '50px'}),
            # Dash Graph
            dcc.Graph(figure=fig),
            dcc.Graph(figure=fig),

            # Dash Table
            dash_table.DataTable(values, headers),
            
        ], body=True, style={"margin": '200px', "margin-top":50, "border-bottom":0}), 

    ], className="dbc", fluid=True)

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])