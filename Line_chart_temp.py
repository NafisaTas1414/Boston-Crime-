import panel as pn
import pandas as pd

def create_line_chart(df, x_col, y_col, title, xlabel, ylabel, width=600, height=500, color="red"):
    """
    Generate a reusable line chart with circle markers at each data point.
    Automatically extends x-axis range to prevent data points from being cut off.

    Args:
        df (pd.DataFrame): The data to plot.
        x_col (str): Column for the x-axis.
        y_col (str): Column for the y-axis.
        title (str): Chart title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        width (int): Chart width.
        height (int): Chart height.
        color (str): Color for scatter points (default: "red").

    Returns:
        pn.pane.HoloViews: A Panel-compatible HoloViews line chart.
    """

    # Check if dataframe is empty
    if df.empty:
        return pn.pane.Markdown("No data available.")

    df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0).astype(int)

    # 20% buffer for y-axis
    ylim_max = df[y_col].max() * 1.2

    # Determine x-axis range and add padding if numerical
    if pd.api.types.is_numeric_dtype(df[x_col]) or pd.api.types.is_datetime64_any_dtype(df[x_col]):
        x_min, x_max = df[x_col].min(), df[x_col].max()
        xlim_min, xlim_max = x_min - 1, x_max + 1  # Extend the x-axis range
    else:
        xlim_min, xlim_max = None, None  # Don't modify if x-axis is categorical

    # Create the line chart
    # I made height, width, color, and labels customizable, while providing defaults.
    # This ensures flexibility if I don’t have a specific color or size in mind in the future.
    line_chart = df.hvplot.line(
        x=x_col,
        y=y_col,
        line_width=3,
        height=height,
        width=width,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        ylim=(0, ylim_max),
        hover=True
    ) * df.hvplot.scatter(
        x=x_col,
        y=y_col,
        size=100,
        color=color,
        alpha=0.7,
        bgcolor="whitesmoke",
        framewise=True
    )

    # Apply x-axis padding only when needed
    if xlim_min is not None and xlim_max is not None:
        line_chart = line_chart.opts(xlim=(xlim_min, xlim_max))

    # Removes active default tools and makes chart responsive
    line_chart = line_chart.opts(active_tools=[], responsive=True, clone=True)

    return pn.pane.HoloViews(line_chart, linked_axes=False)

