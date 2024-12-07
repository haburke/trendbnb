# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import sqlalchemy as sa

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import db_query


page_name = "page1"

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

# -- plotly figs -------------------------------------------------------------------------------------------------------'''
'''
query = sa.text("""WITH HostData AS (
    SELECT 
        H.HostID,
        EXTRACT(YEAR FROM H.HostSince) AS RegistrationYear,
        L.City
    FROM 
        Host H
        INNER JOIN Listing L ON H.HostID = L.HostID
    WHERE 
        L.City = :CityName
)
SELECT RegistrationYear, COUNT(DISTINCT HostID) AS NumberOfHosts
FROM HostData
WHERE RegistrationYear >= EXTRACT(YEAR FROM SYSDATE) - 10
GROUP BY RegistrationYear
ORDER BY RegistrationYear""")

params={"CityName": "Paris"}
df = db_query(query, params)


fig = px.line(data_frame=df, x=df['registrationyear'], y=df['numberofhosts'], title="Number of Hosts Over Time")

#used for making layout use integers for axis and not half values for years
fig.update_layout(
    xaxis=dict(tickmode='linear', tick0=df['registrationyear'].min(), dtick=1),
    yaxis=dict(tickmode='linear', tick0=df['numberofhosts'].min(), dtick=500)
)

fig.update_layout(template="plotly_dark")
'''

'''
dcc.Dropdown(id='city_dropdown',
             options=[{'label': 'Paris', 'value': 'Paris'},
                      {'label': 'New York City', 'value': 'New York City'}],
             value="Paris",
             style={'width': "50%"}),
'''

# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        navbar_main,  # Place the navbar outside the input group
        # Input group for city search
        dbc.InputGroup(
            [
                dbc.Input(
                    id="city_input",
                    placeholder="Enter a city name here...",
                    type="text",
                    style={"width": "50%"}
                ),
                dbc.Button(
                    "Search",
                    id="city_search_button",
                    n_clicks=0,
                    color="primary",
                    style={"margin-left": "10px"}
                ),
            ],
            style={"margin-bottom": "20px"}
        ),
        # Graph for displaying results
        dcc.Graph(id="num_host_graph"),
    ], className="dbc", fluid=True)

@callback(Output("num_host_graph", "figure"),
        [Input("city_search_button", "n_clicks")],
        [State("city_input", "value")]
          )
def update_graph(n_clicks, selected_city):
    if not selected_city:
        selected_city = "Paris"
    query = sa.text("""WITH HostData AS (
        SELECT 
            H.HostID,
            EXTRACT(YEAR FROM H.HostSince) AS RegistrationYear,
            L.City
        FROM 
            Host H
            INNER JOIN Listing L ON H.HostID = L.HostID
        WHERE 
            L.City = :CityName
    )
    SELECT RegistrationYear, COUNT(DISTINCT HostID) AS NumberOfHosts
    FROM HostData
    WHERE RegistrationYear >= EXTRACT(YEAR FROM SYSDATE) - 10
    GROUP BY RegistrationYear
    ORDER BY RegistrationYear""")

    params = {"CityName":selected_city}
    df = db_query(query, params)

    if df.empty:
        fig = px.scatter(title=f"No data was found for the city: {selected_city}. Please enter a different one.")

    else:
        fig = px.line(data_frame=df, x=df['registrationyear'], y=df['numberofhosts'], title="Number of Hosts Over Time")

        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=df['registrationyear'].min(), dtick=1),
            yaxis=dict(tickmode='linear', tick0=df['numberofhosts'].min(), dtick=500)
        )

    fig.update_layout(template="plotly_dark")
    return fig

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])

