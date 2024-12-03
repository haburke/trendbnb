# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import os
import json

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import Dash
import dash_bootstrap_components as dbc


# -- theme template css ------------------------------------------------------------------------------------------------
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