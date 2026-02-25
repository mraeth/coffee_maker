import time
import numpy as np

import dash
from dash import dcc, html, Input, Output, State, callback_context

import plotly.graph_objs as go

import dash_bootstrap_components as dbc

import plotly.io as pio

from scipy.special import erf

from dash import dash_table

import os
import csv
from datetime import datetime

from dash.exceptions import PreventUpdate

pio.templates.default = "plotly_dark"
pio.templates["plotly_dark"]["layout"]["font"]["size"] = 18
pio.templates["plotly_dark"]["layout"]["font"]["family"] = "Arial"

MAX_POINTS = 600  # cap stored/rendered data points (~5 min at 500 ms)

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1"}
    ]
)
server = app.server  # useful if you deploy later

# ---- App state (simple version) ----
x_data = []
temp_data = []
weight_data = []

t0 = time.time()

max_temperature = 100
recipe = 60 #g/l
coffee_amount = 20 #g
weight_target = coffee_amount / recipe * 1000   # ml

running = False


def save_time_traces(time_data, temperature_data, weight_data,
                     identifier=None, base_dir="data"):

    os.makedirs(base_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    suffix = f"_{identifier}" if identifier else ""
    filename = os.path.join(base_dir, f"{timestamp}{suffix}.csv")

    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "temperature", "weight"])
        for t, temp, w in zip(time_data, temperature_data, weight_data):
            writer.writerow([t, temp, w])

    return filename


# ---- Layout ----
app.layout = dbc.Container(
    fluid=True,
    style={"maxWidth": "900px", "padding": "10px"},
    children=[
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id="status-table",
                    columns=[
                        {"name": "Quantity", "id": "quantity"},
                        {"name": "Value", "id": "value"}
                    ],
                    data=[
                        {"quantity": "Recipe", "value": f"{recipe} g/l"},
                        {"quantity": "Coffee Amount", "value": f"{coffee_amount} g"},
                        {"quantity": "Target Weight", "value": f"{weight_target:.2f} ml"},
                        {"quantity": "- °C", "value": "- g"},
                    ],
                    style_header={
                        "backgroundColor": "#222",
                        "color": "white",
                        "fontWeight": "bold",
                    },
                    style_cell={
                        "backgroundColor": "#111",
                        "color": "white",
                        "fontSize": "22px",
                        "fontFamily": "monospace",
                        "padding": "6px",
                        "textAlign": "center",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": 3},  # first row
                            "fontSize": "25px",
                            "fontWeight": "bold",
                            "color": "#00ff99",
                        }
                    ],
                ),
                className="my-3"
            )
        ),


        dbc.Row(
            dbc.Col(
                dcc.Graph(id="temperature-graph"),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(id="weight-graph"),
                width=12
            )
        ),

        dcc.Interval(
            id="interval",
            interval=100,   # ms
            n_intervals=0,
            disabled=True
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Start / Stop",
                        id="start-btn",
                        color="success",
                        size="lg",
                        className="w-100"
                    ),
                    width=6
                ),
                dbc.Col(
                    dbc.Button(
                        "Reset",
                        id="reset-btn",
                        color="danger",
                        size="lg",
                        className="w-100"
                    ),
                    width=6
                ),
            ],
            className="my-3"
        ),

        dbc.Row(
            dbc.Col(
                [
                    dbc.Button(
                        "Save",
                        id="save-btn",
                        color="secondary",
                        size="lg",
                        className="w-100"
                    ),

                    dbc.Input(
                        id="save-id",
                        placeholder="Optional run identifier (e.g. test_01)",
                        type="text",
                        className="mt-2"
                    ),

                    html.Div(
                        id="save-status",
                        className="text-center mt-2"
                    ),
                ],
                width=12
            ),
            className="my-3"
        ),
    ]
)

@app.callback(
    Output("interval", "disabled"),
    Input("start-btn", "n_clicks"),
    State("interval", "disabled"),
)
def toggle_start(n_clicks, disabled):
    if n_clicks is None or n_clicks == 0:
        return True
    return not disabled


def reset_plot():
    global x_data, temp_data, weight_data, t0
    temp_data = []
    t0 = time.time()
    x_data = []
    weight_data = []


@app.callback(
    Output("temperature-graph", "figure"),
    Output("weight-graph", "figure"),
    Output("status-table", "data"),
    Input("interval", "n_intervals"),
    Input("reset-btn", "n_clicks"),
)
def update_all(n_intervals, reset_clicks):
    global x_data, temp_data, weight_data, t0

    ctx = callback_context
    trigger = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if trigger == "reset-btn":
        reset_plot()
    elif trigger == "interval":
        t = time.time() - t0
        x_data.append(t)
        temp_data.append(95 - 0.5*t + np.random.randn()*2)
        weight_data.append((1 + erf((t-5)/5))*0.5 * weight_target*1.15 + np.random.randn()*5)

        if len(x_data) > MAX_POINTS:
            x_data = x_data[-MAX_POINTS:]
            temp_data = temp_data[-MAX_POINTS:]
            weight_data = weight_data[-MAX_POINTS:]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_data, y=temp_data, mode="lines", name="Temperature (°C)"))
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Temperature (°C)",
        margin=dict(l=40, r=20, t=30, b=40),
        uirevision="constant"
    )
    fig.update_yaxes(range=[50, max_temperature + 10])

    color = "green"
    if weight_data:
        last_w = weight_data[-1]
        if last_w > weight_target:
            color = "red"
        elif last_w > 0.8 * weight_target:
            color = "orange"
        elif last_w > 0.6 * weight_target:
            color = "yellow"

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x_data, y=weight_data, line_color=color, mode="lines", name="Weight (g)"))
    fig2.add_hline(y=weight_target, line_dash="dash", line_color="blue", annotation_text="Target Weight", annotation_position="top left")
    fig2.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Weight (g)",
        margin=dict(l=40, r=20, t=30, b=40),
        uirevision="constant"
    )
    fig2.update_yaxes(range=[0, max(1.1*weight_target, max(weight_data, default=0))])

    current_temp = temp_data[-1] if temp_data else 0
    current_weight = weight_data[-1] if weight_data else 0
    table_data = [
        {"quantity": "Recipe", "value": f"{recipe} g/l"},
        {"quantity": "Coffee Amount", "value": f"{coffee_amount} g"},
        {"quantity": "Target Weight", "value": f"{weight_target:.2f} ml"},
        {"quantity": f"{current_temp:.2f} °C", "value": f"{current_weight:.2f} ml"},
    ]

    return fig, fig2, table_data


@app.callback(
    Output("save-status", "children"),
    Input("save-btn", "n_clicks"),
    State("save-id", "value"),
)
def save_button_callback(n_clicks, identifier):
    if not n_clicks:
        raise PreventUpdate

    if len(x_data) == 0:
        return "No data to save."

    # Clean identifier (filesystem-safe)
    if identifier:
        identifier = identifier.strip().replace(" ", "_")

    filename = save_time_traces(
        time_data=x_data,
        temperature_data=temp_data,
        weight_data=weight_data,
        identifier=identifier
    )

    return dbc.Alert(
        f"Saved data to {filename}",
        color="success",
        dismissable=True
    )


# ---- Run server ----
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8060, threaded=True)
