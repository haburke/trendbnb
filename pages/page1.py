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


fig = px.line(data_frame=df, x=df['registrationyear'], y=df['numberofhosts'], title="Number of Hosts Per Year")

#used for making layout use integers for axis and not half values for years
fig.update_layout(
    xaxis=dict(tickmode='linear', tick0=df['registrationyear'].min(), dtick=1),
    yaxis=dict(tickmode='linear', tick0=df['numberofhosts'].min(), dtick=500)
)

fig.update_layout(template="plotly_dark")


# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [

        dbc.Card([
            navbar_main,
            dcc.Graph(figure=fig),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid",
                             'border-width': "1px", 'border-radius': 0}),

    ], className="dbc", fluid=True)

if __name__ == '__main__':
    from utils import run_app

    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])

