"""visualize helpers for metrics"""

import pandas as pd
from matplotlib.figure import Figure


def plot_coverage_accuracy_curve(
    curve_df: pd.DataFrame, title: str = "Coverage-Accuracy Curve"
) -> Figure:
    """Plots coverage-accuracy curve using matplotlib.
    Args:
        curve_df: DataFrame with 'coverage' and 'accuracy' columns
        title: title of the plot
    Returns:
        Matplotlib Figure object
    """
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(curve_df["coverage"], curve_df["accuracy"], marker="o")
    ax.set_title(title)
    ax.set_xlabel("Coverage")
    ax.set_ylabel("Accuracy")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True)
    return fig
