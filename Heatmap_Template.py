import folium
import panel as pn
import pandas as pd
from folium.plugins import HeatMap

# I put default values for parameters like zoom_start and height to ensure a consistent appearance
# across different visualizations, while still allowing flexibility if specific adjustments are needed.
def create_heatmap(df, lat_col="Lat", lon_col="Long", center=None,
                   zoom_start=12, radius=12, blur=15, max_zoom=1, height=750, width=1800):
    """
    Generate a reusable Folium heatmap from a DataFrame.

    Parameters:
        df (pd.DataFrame): The dataframe containing latitude and longitude columns.
        lat_col (str): The name of the latitude column in df.
        lon_col (str): The name of the longitude column in df.
        center (list or tuple, optional): Coordinates [lat, lon] to center the map.
                                          Defaults to Boston [42.3601, -71.0589] if None.
        zoom_start (int): Initial zoom level of the map.
        radius (int): Radius of each point in the heatmap.
        blur (int): Amount of blurring applied to heatmap points.
        max_zoom (int): Maximum zoom for clustering.
        height (int): Height of the displayed map.
        width (int): Width of the displayed map.

    Returns:
        pn.pane.plot.Folium: A Panel-compatible Folium heatmap.
    """
    # message if dataframe is empty
    if df.empty or lat_col not in df.columns or lon_col not in df.columns:
        return pn.pane.Markdown("No location data available.")

    # Create a Folium map centered on the given coordinates
    crime_map = folium.Map(location=center, zoom_start=zoom_start)

    # Convert DataFrame coordinates into a list of (lat, lon) pairs
    heat_data = df[[lat_col, lon_col]].dropna().values.tolist()

    # Adds the heatmap layer
    HeatMap(heat_data, radius=radius, blur=blur, max_zoom=max_zoom).add_to(crime_map)

    # Converts the Folium map into a Panel pane
    return pn.pane.plot.Folium(crime_map, height=height, width=width)
