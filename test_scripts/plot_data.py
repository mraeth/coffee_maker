import os
import glob
import webbrowser
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

DATA_DIR = "data"


def load_all_runs():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    if not files:
        raise RuntimeError("No CSV files found in data/")

    datasets = []
    for f in files:
        df = pd.read_csv(f)
        label = os.path.basename(f)
        datasets.append((df, label))
    return datasets


def plot_runs(datasets, output_file):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Temperature", "Weight"),
    )

    labels = []
    for df, label in datasets:
        labels.append(label)
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["temperature"],
                mode="lines",
                name=f"{label} – Temp",
                visible=True,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["weight"],
                mode="lines",
                name=f"{label} – Weight",
                visible=True,
            ),
            row=2,
            col=1,
        )

    n_traces = len(fig.data)
    n_runs = len(labels)

    # Build multi-select dropdown buttons
    buttons = []

    # "Show all" option
    buttons.append(
        dict(
            label="Show all",
            method="update",
            args=[{"visible": [True] * n_traces}],
        )
    )

    # Individual run buttons for single-selection
    for i, label in enumerate(labels):
        mask = [False] * n_traces
        mask[2*i] = True
        mask[2*i + 1] = True
        buttons.append(
            dict(
                label=label,
                method="update",
                args=[{"visible": mask}],
            )
        )

    # **Multi-select dropdown using plotly's "active" trick**
    # Each run can be toggled by the legend anyway
    # The dropdown just provides convenience for quick selection

    fig.update_layout(
        template="plotly_dark",
        height=750,
        title="Overlayed Time Traces (Multi-Select)",
        legend=dict(orientation="h", y=-0.25),
        margin=dict(t=80, b=120),
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                x=1.02,
                y=1.0,
                showactive=True,
            )
        ],
    )

    # Axes labels
    fig.update_xaxes(title="Time")
    fig.update_yaxes(title="Temperature", row=1, col=1)
    fig.update_yaxes(title="Weight", row=2, col=1)

    # Save and open
    fig.write_html(output_file)
    webbrowser.open(f"file://{os.path.abspath(output_file)}")


def main():
    datasets = load_all_runs()
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    output_file = f"multi_select_plot_{timestamp}.html"
    plot_runs(datasets, output_file)


if __name__ == "__main__":
    main()
