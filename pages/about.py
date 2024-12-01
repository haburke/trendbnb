# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
# from pages.navbar import *

# # -- customize simple navbar -------------------------------------------------------------------------------------------
# navbar_main = deepcopy(navbar)
# for nav in navbar_main.children[0].children.children.children.children:
#     if nav.children.id == 'about-select':
#         nav.children.active = True
#         nav.children.style = {"background-color": "var(--bs-dark)"}
#     elif nav.children.id == 'login-select':
#         nav.children.style = {'display': 'none'}

# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        # navbar_main,

        html.Div([
            # dbc.Button(
            #     "Click me", id="example-button", className="me-2", n_clicks=0
            # ),
            # html.Span(id="example-output", style={"verticalAlign": "middle"}),

            dcc.Markdown(children='''
            # About Trendbnb 
            

            # Application Idea


            # Database Motivation and User Interest

            
            ---

            ##### LINKS
            * Database Source: 

            ##### Project Contributors

            ''')
        ], style={'padding': '50px'})

    ], className="dbc", fluid=True)

# @callback(
#     Output("example-output", "children"), [Input("example-button", "n_clicks")]
# )
# def on_button_click(n):
#     if n is None:
#         return "Not clicked."
#     else:
#         return f"Clicked {n} times."

if __name__ == '__main__':
    from pages.utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path='/about')