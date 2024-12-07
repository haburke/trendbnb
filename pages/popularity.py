# ======================================================================================================================
# import standard library packages
# ----------------------------------------------------------------------------------------------------------------------
from copy import deepcopy

# ======================================================================================================================
# import dash library packages
# ----------------------------------------------------------------------------------------------------------------------
from dash import register_page, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# ======================================================================================================================
# import local packages
# ----------------------------------------------------------------------------------------------------------------------
from pages.components import *
from pages.utils import db_query, engine  # Import engine

# Page Configurations
page_name = "popularity"
db_owner = "ANDREW.GOLDSTEIN"

# ======================================================================================================================
# Query Definition
# ----------------------------------------------------------------------------------------------------------------------
def popListOverTime(city: str, years: int) -> str:
    return f'''
    WITH ReviewCountData AS (
        SELECT 
            L.City,
            EXTRACT(YEAR FROM R.ReviewDate) AS ReviewYear,
            COUNT(R.ReviewID) AS ReviewCount
        FROM 
            "{db_owner}".Review R
            INNER JOIN "{db_owner}".Listing L ON R.ListingID = L.ListingID
        WHERE 
            L.City = '{city}'
            AND R.ReviewDate >= L.FirstReview
            AND EXTRACT(YEAR FROM R.ReviewDate) >= EXTRACT(YEAR FROM SYSDATE) - {years}
        GROUP BY 
            L.City, EXTRACT(YEAR FROM R.ReviewDate)
    )
    SELECT 
        ReviewYear, 
        SUM(ReviewCount) AS TotalReviews
    FROM ReviewCountData
    GROUP BY ReviewYear
    ORDER BY ReviewYear
    '''

# ======================================================================================================================
# Layout with User Input
# ----------------------------------------------------------------------------------------------------------------------
navbar_main = deepcopy(navbar)
set_active(navbar_main, page_name)

layout = dbc.Container(
    [
        dbc.Card([
            navbar_main,

            # Summary Section
            html.Div(
                [
                    html.H5("Description"),
                    html.P(
                        """
                        This query calculates how many reviews Airbnb listings in a specific city received over the
                         past few years. The user can select the number of years in which to review. This gives 
                         insight into the popularity of Airbnb listings in that city over time.
                        """
                    ),

                    html.H5("Motivation"),
                    html.P(
                        """
                        It offers valuable insights for Airbnb hosts, property managers, and analysts to understand 
                        trends in listing popularity. They could determine if Airbnb is becoming more or less popular 
                        in a city, and if there are specific years with spikes in activity, does it correlate with 
                        special events. Superbowl, Olympics, etc.
                        """
                    )
                ],
                className="summary"
            ),

            # Input Fields and Graph
            html.Div(
                [
                    dbc.InputGroup(
                        [
                            dbc.Input(
                                id="city_input",
                                placeholder="Enter a city name...",
                                type="text",
                                style={"background-color": "#2c2f33", "color": "white", "border": "1px solid #444"},
                            ),
                            dbc.Select(
                                id="year_dropdown",
                                options=[{"label": f"{i} years", "value": i} for i in range(3, 11)],
                                value=5,  # Default value
                                style={"background-color": "#2c2f33", "color": "white", "border": "1px solid #444"},
                            ),
                            dbc.Button(
                                "Search",
                                id="search_button",
                                n_clicks=0,
                                color="primary",
                                style={"margin-left": "10px"}
                            ),
                        ],
                        style={"margin-bottom": "20px", "justify-content": "center"},
                    ),
                    dcc.Graph(id="popularity_graph"),
                ],
            ),
        ], body=True, style={"margin": '20%', "margin-top": 50, 'border-color': "#111111", 'border-style': "solid",
                             'border-width': "1px", 'border-radius': 0}),
    ],
    className="dbc",
    fluid=True,
)

# ======================================================================================================================
# Callback for Graph Update
# ----------------------------------------------------------------------------------------------------------------------
@callback(
    Output("popularity_graph", "figure"),
    [Input("search_button", "n_clicks")],
    [State("city_input", "value"), State("year_dropdown", "value")]
)
def update_popularity_graph(n_clicks, selected_city, selected_years):
    if not selected_city:
        selected_city = "Paris"  # Default city
    if not selected_years:
        selected_years = 5  # Default years
    query = popListOverTime(selected_city, selected_years)
    query_results = db_query(engine, query)  # Use engine in db_query

    if query_results is not None and not query_results.empty:
        query_results["reviewyear"] = query_results["reviewyear"].astype(int)
        query_results["totalreviews"] = query_results["totalreviews"].astype(int)
        x = query_results["reviewyear"].tolist()
        y = query_results["totalreviews"].tolist()
    else:
        x, y = [], []

    fig = go.Figure()

    if x and y:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color="royalblue", width=2),
                marker=dict(size=6, color="darkblue"),
            )
        )
        fig.update_layout(
            title=f"Popularity of Listings Over Time in {selected_city} ({selected_years} years)",
            xaxis=dict(title="Year", tickmode="linear", dtick=1),
            yaxis=dict(title="Total Reviews", rangemode="tozero"),
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
        )
    else:
        fig.update_layout(
            title=f"No data found for {selected_city} ({selected_years} years). Please try another search.",
            template="plotly_dark",
        )

    return fig

# ======================================================================================================================
# Run Application
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    from utils import run_app
    app = run_app(layout=layout)
else:
    register_page(__name__, path=page_info[page_name]["href"])
