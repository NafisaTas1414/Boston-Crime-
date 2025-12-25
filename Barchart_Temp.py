import hvplot.pandas
import panel as pn

def create_bar_chart(df, x_col, y_col, title, xlabel, ylabel, height=570, width=660):
    """
    Generate a visually improved bar chart with better colors, fonts, and axis formatting.

    Parameters:
        df (pd.DataFrame): The data source for the chart.
        x_col (str): The column to use for the x-axis.
        y_col (str): The column to use for the y-axis.
        title (str): The title of the chart.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        height (int): Height of the chart.
        width (int): Width of the chart.

    Returns:
        pn.pane.HoloViews: A Panel-rendered bar chart.
    """
    # CHECKS if dataframe is empty
    if df.empty:
        return pn.pane.Markdown("No data available for the given parameters.")

    # Set dynamic y-axis limit with a 20% buffer for better visualization
    ylim_max = df[y_col].max() * 1.2

    # Create an interactive bar chart using hvPlot by adding features like the hover tool
    chart = df.hvplot.bar(
        x=x_col,
        y=y_col,
        bar_width=0.7,  # Adjust bar width for better spacing
        rot=15,  # Rotate x-axis labels slightly for better readability
        height=height,
        width=width,
        ylim=(0, ylim_max),  # Auto generates y-axis scaling
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        hover=True,
        color="skyblue",
        line_color="black",
        padding=(0.2, 0.05),
        xlim=(-0.5, len(df) - 0.5),
    ).opts(
        # Configures visual styling and interactivity settings
        active_tools=[],
        responsive=True,
        clone=True,
        toolbar="above",
        aspect=2,
        fontsize={
            "title": 14,
            "xlabel": 12,
            "ylabel": 12,
            "xticks": 8,
            "yticks": 10
        },
        bgcolor="whitesmoke",
        framewise=True
    )

    return pn.pane.HoloViews(chart, linked_axes=False)
