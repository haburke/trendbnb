# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import os
import json
from pathlib import Path
from configparser import ConfigParser

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import Dash
import dash_bootstrap_components as dbc
import oracledb
import sqlalchemy as sa
import pandas as pd

# -- theme template css ------------------------------------------------------------------------------------------------
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from sqlalchemy.engine import create_engine

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------

def get_data():
    return [1, 2, 3], [4, 1, 2]

def get_table():
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
    values = df.to_dict('records')
    headers = [{"name": i, "id": i} for i in df.columns]
    return values, headers

def get_config():
    cfg_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent/'config'
    cfg = ConfigParser()
    cfg.read(cfg_dir/'config.ini')
    return cfg

def db_func():
    from config.cred import USERNAME, PASSWORD, HOST, SID
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


# -- theme template css ------------------------------------------------------------------------------------------------
'''
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")


def get_config():
    cfg_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent/'configs'
    cfg = ConfigParser()
    cfg.read(cfg_dir/'config.ini')
    return cfg


def oracle_query(query: str = None):
    if query is None:
        query = test_query
    return pd.read_sql_query(query, engine)


def run_app(layout):
    parser = ArgumentParser()
    parser.add_argument("--host", default='0.0.0.0')
    parser.add_argument("--port", default='8060')
    parser.add_argument("-d", "--debug", action='store_true', default=False)
    args = parser.parse_args()
    args.debug = False

    app = Dash(__name__,
               external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP, 'assets/styles.css', dbc_css],
               suppress_callback_exceptions=True)
    app.layout = layout
    app.run_server(host=args.host, port=args.port, debug=args.debug)

    return app

'''