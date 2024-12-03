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
<<<<<<< Updated upstream
from pages.utils import dbc_css
from config.cred import USERNAME, PASSWORD
=======
#from pages.utils import dbc_css
from config.cred import USERNAME, PASSWORD, HOST, SID
>>>>>>> Stashed changes

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
<<<<<<< Updated upstream
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
=======
username = USERNAME
password = PASSWORD
host = HOST
port = 1521
sid =  SID

dsn = oracledb.makedsn(host, port, sid=sid)

connection_string = f"oracle+oracledb://{username}:{password}@{host}:{port}/{sid}"

engine = sa.create_engine(connection_string)

try:
    connection = engine.connect()

    print("Successfully connected to the database.")

    query = "SELECT COUNT(*) FROM Listing"

    df = pd.read_sql(query, connection)
    print(df)

except oracledb.DatabaseError as e:
    error, = e.args
    print(f"Error Code: {error.code}")
    print(f"Error Message: {error.message}")

finally:
    if connection:
        connection.close()
>>>>>>> Stashed changes

# -- init dash ---------------------------------------------------------------------------------------------------------
app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP, 'assets/styles.css', dbc_css],
           suppress_callback_exceptions=True,
           use_pages=True)
pages = page_registry
container = page_container

app.run_server(host="0.0.0.0", port="8060", debug=True)
