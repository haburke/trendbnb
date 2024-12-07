# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import Dash, html, dcc, page_registry, page_container, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlalchemy as sa
import pandas as pd
import oracledb

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.utils import dbc_css

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------


# -- header ------------------------------------------------------------------------------------------------------------
title = html.H3("Trendbnb")
logo = html.Img(
    src="./assets/trendbnb_logo.png", style={'height': 80, 'margin': "8px 0px 8px 30px"}
)

header = dbc.Row([
    dbc.Col(logo, width="auto", align="center"), 
    dbc.Col(title, width="auto", align="center"),

    ], style={"background-color":"var(--bs-dark)", 'box-shadow': "0px 0px 5px 0px #111111"})


# -- init dash ---------------------------------------------------------------------------------------------------------
app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP, 'assets/styles.css', dbc_css],
           suppress_callback_exceptions=True,
           use_pages=True)

app.layout = html.Div([
    header,
    page_container
])


if __name__ == "__main__":
    debug_mode = True   
    app.run(host="0.0.0.0", port=8060, debug=False)
