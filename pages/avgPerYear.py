# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import sqlalchemy as sa

# ======================================================================================================================
# import non-standard library packages
# ----------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import get_data, get_table, db_query, engine

page_name = "avgPerYear"
city_name = "Amsterdam"
db_owner = "ANDREW.GOLDSTEIN"

def someQuery(city:str) -> str:
    return f'''
    SELECT COUNT(*) 
    FROM "{db_owner}".Listing L 
    WHERE L.City = '{city}' 
    '''


def avgPerYearQuery(city:str) -> str:
    return f'''
    WITH YearlyPriceData AS (
        SELECT 
            L.City,
            EXTRACT(YEAR FROM L.FirstReview) AS ListingYear,
            AVG(L.DailyPrice) AS AvgDailyPrice
        FROM "{db_owner}".Listing L
        WHERE L.City = '{city}'
        GROUP BY L.City, EXTRACT(YEAR FROM L.FirstReview)
    ),
    PriceChange AS (
        SELECT 
            ListingYear,
            AvgDailyPrice,
            LAG(AvgDailyPrice) OVER (ORDER BY ListingYear) AS PrevYearAvgPrice
        FROM YearlyPriceData
    )
    SELECT ListingYear, round(AvgDailyPrice),
        CASE 
            WHEN PrevYearAvgPrice IS NOT NULL THEN
                ROUND((AvgDailyPrice - PrevYearAvgPrice) / PrevYearAvgPrice * 100, 2)
            ELSE
                NULL
        END AS PercentageChange
    FROM PriceChange
    ORDER BY ListingYear
    '''

# -- plotly figs -------------------------------------------------------------------------------------------------------
x, y = get_data()
values, headers = get_table()
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
fig.update_layout(template="plotly_dark")

# -- customize simple navbar -------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)


layout = dbc.Container(
    [
        dbc.Card([ 
            navbar_main,
            
            html.Div(
                    [
                        html.H5("Summary"),
                        html.P(
                    
                            "By utilizing an extensive database with over 400,000 Airbnb listing records"
                        ),
                    ], className="summary"
                ),

        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid", 
                             'border-width': "1px", 'border-radius': 0}), 

    ], className="dbc", fluid=True)
    
# -- layout ------------------------------------------------------------------------------------------------------------
layout = dbc.Container(
    [
        dbc.Card(
            [ 
                navbar_main,
                html.Div(
                    [
                        html.H5("Summary"),
                        html.P(
                            "Shows the Average Price Change per year for a selected city, showing trends in the market over time."
                            "This allows for prediction of future trends and can be used to inform property owners about hosting decisions."
                        ),
                    ], className="summary"
                ),
                #
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
                dcc.Graph(id="candlestick"),
                #        
            ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid", 
                             'border-width': "1px", 'border-radius': 0}),
        
    ],
    className="dbc", fluid=True)

@callback(
    Output("candlestick", "figure"),
    [Input("city_search_button", "n_clicks")],
    [State("city_input", "value")]
)
def update_graph(n_clicks, selected_city):
    if not selected_city:
        selected_city = "Paris"
    query = sa.text(f"""
        WITH YearlyPriceData AS (
            SELECT 
                L.City,
                EXTRACT(YEAR FROM L.FirstReview) AS ListingYear,
                AVG(L.DailyPrice) AS AvgDailyPrice
            FROM "ANDREW.GOLDSTEIN".Listing L
            WHERE L.City = :CityName -- Replace with the desired city
            GROUP BY L.City, EXTRACT(YEAR FROM L.FirstReview)
        ),
        PriceChange AS (
            SELECT 
                ListingYear,
                AvgDailyPrice,
                LAG(AvgDailyPrice) OVER (ORDER BY ListingYear) AS PrevYearAvgPrice
            FROM YearlyPriceData
        )
        SELECT ListingYear, round(AvgDailyPrice) AS AvgDailyPrice,
            CASE 
                WHEN PrevYearAvgPrice IS NOT NULL THEN
                    ROUND((AvgDailyPrice - PrevYearAvgPrice) / PrevYearAvgPrice * 100, 2)
                ELSE
                    NULL
            END AS PercentageChange
        FROM PriceChange
        ORDER BY ListingYear
        """)

    params = {"CityName":selected_city}
    df = db_query(engine, query, params)
    print(df)
    if df.empty:
        #change the title
        fig = go.Figure(layout={"Title":f"No data was found for the city: {selected_city}. Please enter a different one."})
    else:
        listYear = df['listingyear']
        avgPrice = df['avgdailyprice']
        perChange = df['percentagechange']
        fig = go.Figure(data=[go.Candlestick(x=listYear,
                                            open=avgPrice*(1 - perChange/100) if perChange is not None else avgPrice,
                                            high=avgPrice,
                                            low=avgPrice,
                                            close=avgPrice,
                                            name='Price Change')])
        fig.add_scatter(x=listYear,
                        y=avgPrice,
                        name='Average Price',
                        mode='lines+markers')
        
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,)
    return fig



if __name__ == '__main__':
    from utils import run_app
    app = run_app(layout=layout)
    
else:
    register_page(__name__, path=page_info[page_name]["href"])
    