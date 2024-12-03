# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import Dash, html, dcc, page_registry, page_container, Input, Output, State
import dash_bootstrap_components as dbc

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.utils import dbc_css
from config.cred import USERNAME, PASSWORD

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from sqlalchemy.engine import create_engine

DIALECT = 'oracle'
SQL_DRIVER = 'cx_oracle'
HOST = 'subdomain.domain.tld'
PORT = 1521
SERVICE = 'oracle_db_service_name'
ENGINE_PATH = f"{DIALECT}+{SQL_DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/?service_name={SERVICE}"
engine = create_engine(ENGINE_PATH)

# == test query ========================================================================================================
import pandas as pd
df = pd.read_sql_query('SELECT * FROM TABLE', engine)
print(df.head())

# -- init dash ---------------------------------------------------------------------------------------------------------
app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP, 'assets/styles.css', dbc_css],
           suppress_callback_exceptions=True,
           use_pages=True)
pages = page_registry
container = page_container

app.run_server(host="0.0.0.0", port="8060", debug=True)
