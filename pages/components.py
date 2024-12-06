# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
import os
from pathlib import Path


# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import Dash, html, dcc, page_registry, page_container, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template, ThemeChangerAIO


# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.utils import get_config


# -- define styles -----------------------------------------------------------------------------------------------------
FOOTER_STYLE = {
    "position": "fixed",
    "bottom": 15,
    "left": 0,
    "right": 0,
    "height": 20,
}

# -- init templates ----------------------------------------------------------------------------------------------------
templates = ["bootstrap", "cerulean", "cosmo", "cyborg", "darkly", "flatly", "journal", "litera",
             "lumen", "lux", "materia", "minty", "morph", "pulse", "quartz", "sandstone", "simplex",
             "sketchy", "slate", "solar", "spacelab", "superhero", "united", "vapor", "yeti", "zephyr"]
load_figure_template(templates)

# -- init config -------------------------------------------------------------------------------------------------------
cfg = get_config()

# -- init pages --------------------------------------------------------------------------------------------------------
page_info = {
    "home":{"id": "home-select", "href": "/", "page-title": "Home"},
    "page1": {"id": "page1-select", "href": "/page1", "page-title": "Page1"},
    "about": {"id": "about-select", "href": "/about", "page-title": "About"},
}

# -- navbar components -------------------------------------------------------------------------------------------------
theme_button = ThemeChangerAIO(aio_id="theme", radio_props={"value": dbc.themes.DARKLY})
nav_options = dbc.Nav([
    dbc.NavItem(dbc.NavLink(page_info[link]["page-title"],
                            href=page_info[link]["href"],
                            id=page_info[link]["id"]), class_name='nav-pill') for link in page_info], 
                            class_name='nav-pills', justified=True, style={'margin-top':150})
contact_info = dbc.Row([
                            dbc.Col([
                                html.P(
                                    f"Contact: {cfg['app']['contact']}",
                                    style={'margin': 0}
                                ),
                                html.A(
                                    "Source code",
                                    href="https://www.github.com",
                                    style={'margin-right': 10}
                                ),
                                html.A(
                                    "Documentation",
                                    href="https://www.github.com"
                                ),
                            ], style={'font-size': 12})
                        ], style={'margin-left': "auto", 'margin-right': 10})
dk_bg = {'background-image': f'url({cfg["navbar"]["dark_bg"]})', 'height': 190, 'background-size': "cover"}
lt_bg = {'background-image': f'url({cfg["navbar"]["light_bg"]})', 'height': 190, 'background-size': "cover"}
navbar = dbc.Row(
                dbc.Col(nav_options, style={'margin-left': "20%", 'margin-right': "20%"}),
                style=dk_bg, id="nav"
                )


def set_active(navbar_main, page_name):
    for nav in navbar_main.children.children.children:
        if nav.children.id == page_info[page_name]['id']:
            nav.children.active = True
            nav.children.style = {'background-color': "var(--bs-dark)", 'border-bottom-left-radius': 0, 
                                  'border-bottom-right-radius': 0}
        elif nav.children.id == 'login-select':
            nav.children.style = {'display': "none"}
    

# -- footer ------------------------------------------------------------------------------------------------------------
footer = html.Footer(theme_button, style=FOOTER_STYLE)

# @callback(
#     [Output(link["id"], "active") for link in page_info],
#     Input("url", "pathname"),
#     prevent_initial_call=True,
# )
# def update_active_page(pathname):
#     return [True if link['href'] == pathname else False for link in page_info]


@callback(
    Output('nav', 'style'),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    prevent_initial_call=True,
)
def update_nav_theme(theme):
    if any([val in theme for val in ['cyborg', 'darkly', 'slate', 'solar', 'superhero', 'vapor']]):
        return dk_bg
    else:
        return lt_bg