# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import Dash, html, dcc, page_registry, page_container, Input, Output, State
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

# -- init dash ---------------------------------------------------------------------------------------------------------
app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP, 'assets/styles.css', dbc_css],
           suppress_callback_exceptions=True,
           use_pages=True)
pages = page_registry
container = page_container

app.run_server(host="0.0.0.0", port="8060", debug=False)
