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

# -- modal menus -------------------------------------------------------------------------------------------------------
login_modal = dbc.Modal([
    dbc.ModalBody(
        dbc.Container([
            dbc.FormFloating([
                dbc.Input(type='text', id='login_username_input'),
                dbc.Label("Username")
            ]),
            dbc.FormFloating([
                dbc.Input(type='text', id='login_password_input'),
                dbc.Label("Password")
            ]),
            dbc.Button("Submit", type="submit", class_name='w-100', id='login_submit_button', n_clicks=0)
        ])
    )], id='modal', is_open=False, centered=True, fade=True, backdrop=True, keyboard=True)

# -- header ------------------------------------------------------------------------------------------------------------
title = html.H3("Trendbnb")
logo = html.Img(
    src="./assets/bee_logo.png", style={"height": 50, "margin-top": 8, "margin-bottom": 8}
)

header = dbc.Row([
    dbc.Col(logo, width="auto", align="center"), 
    dbc.Col(title, width="auto", align="center"),
    dbc.Col([
        dbc.Button("Login", id="login-button"),
        login_modal
    ])
    ], style={"background-color":"var(--bs-dark)", 'box-shadow': "0px 0px 5px 0px #111111"})

login_button = dbc.Button("Click Me", id="logged-in-button", n_clicks=0)

# -- init dash ---------------------------------------------------------------------------------------------------------
app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP, 'assets/styles.css', dbc_css],
           suppress_callback_exceptions=True,
           use_pages=True)

app.layout = html.Div([
    header,

    html.Div(id="homepage-div"),
    dcc.Store(id="logged-in"),
    html.Div([
        login_button,
    ], id="login-button-div"),
    html.Div(id="hidden-div")
])

# Login button triggers modal
@callback(
    Output("modal", "is_open"),
    [Input("login-button", "n_clicks"),
     Input("login_submit_button", "n_clicks")],
    [State("modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    [Output("hidden-div", "children"),
     Output("login-button-div", "children"),
     Output("homepage-div", "children")],
    [Input("login_submit_button", "n_clicks"),
     Input("login_username_input", "value"),
     Input("login_password_input", "value")]
)
def submit_login(n, username, password):
    if (n and username == "admin" and password == "admin") or debug_mode:
        return html.Div(page_container), html.H1("yourname"), html.Div()
    return html.Div(), login_button, html.Div()

if __name__ == "__main__":
    debug_mode = True   
    app.run(host="0.0.0.0", port="8060", debug=False)
