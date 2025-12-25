"""
Nafisa Tasnia
DS3500
1/31/2025
Homework 3: Build dashboard (This is my frontend code for visualizing the dashboard)
"""
import panel as pn
from Barchart_Temp import create_bar_chart
from Line_chart_temp import create_line_chart
from Making_Sankey import make_sankey
from Heatmap_Template import create_heatmap
from Stacked_chart_template_V2 import stacked_bar_chart
from HW3_CRIME_API import Crime_API

# Initialize Panel and CrimeAPI instance
pn.extension(sizing_mode="stretch_width")
crime_api = Crime_API()

# Year Dropdown (For Crime Trends)
year_options = list(range(2020, 2026))
year_input = pn.widgets.Select(name="Select Year", options=year_options, value=2020)

# Year Slider (For Crime Heatmap)
year_slider = pn.widgets.IntSlider(name="Select Year", start=2020, end=2025, step=1, value=2022)

# Fetch unique crime categories dynamically
crime_category_options = crime_api.get_unique_crime_categories()
crime_category_dropdown = pn.widgets.Select(name="Select Crime Category",
                                            options=crime_category_options, value=crime_category_options[0])

# Dropdown for Crime Type Selection (For Heatmap)
crime_type_dropdown = pn.widgets.Select(name="Select Crime Type",
                                        options=crime_api.get_unique_crime_types(), value="All Crimes")

def create_crime_chart(year):
    """
    Fetches and creates a bar chart of the top crimes in Boston for a given year.
    """
    df = crime_api.fetch_boston_top_crimes(year)
    return create_bar_chart(df=df, x_col="Crime", y_col="crime_count",
                            title=f"Top Crimes in Boston ({year})", xlabel="Crime", ylabel="Crime Count")

def create_district_chart(year):
    """
    Fetches and creates a bar chart showing the top 5 crime districts in Boston for a given year.
    """
    df = crime_api.fetch_top_districts(year)
    return create_bar_chart(df=df, x_col="DISTRICT", y_col="crime_count",
                            title=f"Top 5 Crime Districts ({year})", xlabel="District", ylabel="Crime Count")

def create_day_of_week_chart(year):
    """
    Fetches and creates a line chart showing total crime counts by day of the week for a given year.
    """
    df = crime_api.fetch_crime_by_day_of_week(year)
    return create_line_chart(df=df, x_col="DAY_OF_WEEK", y_col="crime_count",
                             title=f"Crime by Day of the Week ({year})", xlabel="Day of Week", ylabel="Crime Count")


def create_monthly_trend_chart(year):
    """
    Fetches and creates a line chart showing crime trends by month for a given year.
    """
    df = crime_api.fetch_crime_by_month_all_years()
    df = df[df["YEAR"] == year]  # Filter data for the selected year
    return create_line_chart(df=df, x_col="MONTH", y_col="crime_count",
                             title=f"Monthly Crime Trend ({year})", xlabel="Month", ylabel="Crime Count")


def create_crime_category_trend_chart(selected_category):
    """
    Fetches and creates a line chart showing crime trends over time for a selected crime category.
    """
    df = crime_api.fetch_crime_category_trends(selected_category)
    return create_line_chart(df=df, x_col="Year", y_col="Crime Count",
                             title=f"{selected_category} Trends Over Time", xlabel="Year", ylabel="Total Crime Count")


def create_stacked_bar_chart(selected_category):
    """
    Fetches and creates a stacked bar chart comparing a selected crime category to all other crimes.
    """
    df = crime_api.fetch_crime_category_proportions(selected_category)
    return stacked_bar_chart(df=df, x_col="YEAR", y_cols=[selected_category, "Other Crimes"],
                             title=f"{selected_category} vs. Other Crimes", xlabel="Year", ylabel="Total Crime Count")

def create_crime_heatmap(year, crime_type):
    """
    Fetches and creates a heatmap of crime locations for a given year and crime type.
    """
    df = crime_api.fetch_crime_locations(year, crime_type)
    return create_heatmap(df=df, lat_col="Lat", lon_col="Long", center=[42.3601, -71.0589],
                          zoom_start=12, height=750, width=1800)

def create_sankey_chart():
    """
    Fetches and creates a Sankey diagram to visualize the flow of crime categories across districts and years.
    """
    df = crime_api.fetch_sankey_data()
    return make_sankey(df, "District", "Year", "Crime_Category", vals="Crime_Count")


# to display sankey diagram
sankey_pane = pn.pane.Plotly(create_sankey_chart())

# Bind Functions to Widgets
crime_chart_pane = pn.bind(create_crime_chart, year_input.param.value)
district_chart_pane = pn.bind(create_district_chart, year_input.param.value)
day_of_week_chart_pane = pn.bind(create_day_of_week_chart, year_input.param.value)
monthly_trend_chart_pane = pn.bind(create_monthly_trend_chart, year_input.param.value)
crime_heatmap_pane = pn.bind(create_crime_heatmap, year_slider.param.value, crime_type_dropdown.param.value)
crime_category_chart_pane = pn.bind(create_stacked_bar_chart, crime_category_dropdown.param.value)
crime_category_trend_chart_pane = pn.bind(create_crime_category_trend_chart, crime_category_dropdown.param.value)

# Page 1 setup: Crime Trends Dashboard (shows some overall trends in the data)
crime_dashboard = pn.Column(
    pn.pane.Markdown("### Select Year to View Crime Trends"), year_input,
    pn.Row(
        pn.Card(crime_chart_pane, title="Top 10 Crimes in Boston", height=700, width=700),
        pn.Card(day_of_week_chart_pane, title="Crime by Day of the Week", height=700, width=700),
    ),
    pn.Row(
        pn.Card(district_chart_pane, title="Top 5 Crime Districts", height=700, width=700),
        pn.Card(monthly_trend_chart_pane, title="Monthly Crime Trends", height=700, width=700),
    )
)

# Page 2 setup: the visuals that will be shown -> Crime Heatmap View
heatmap_page = pn.Column(
    pn.pane.Markdown("## Crime Heatmap by Year & Crime Type"),
    pn.Row(year_slider, crime_type_dropdown),
    pn.Row(pn.Card(crime_heatmap_pane, title="Crime Heatmap", width=900, height=600))
)

# Page 3 setup: Crime Category Analysis
crime_category_page = pn.Column(
    pn.pane.Markdown("## Crime Category Analysis"),
    pn.Row(crime_category_dropdown),
    pn.Row(
        pn.Card(crime_category_chart_pane, title="Stacked Crime Category Chart", height=600, width=700),
        pn.Card(crime_category_trend_chart_pane, title="Crime Category Trends Over Time", height=600, width=700),
    ),
    pn.Card(sankey_pane, title="Top 3 Crime Types by District Over Time", height=600, width=1400)
)

# All the tabs/pages that will be shown on my dashboard
multi_page_dashboard = pn.Tabs(
    ("Crime Trends", crime_dashboard),
    ("Crime Heatmap", heatmap_page),
    ("Crime Category", crime_category_page),
)

# FastListTemplate for Dashboard
template = pn.template.FastListTemplate(
    title="Boston Crime Dashboard",
    main=[multi_page_dashboard],
    accent_base_color="#88d8b0",
    header_background="#88d8b0"
)


if __name__ == "__main__":
    # to run and show the dashboard
    pn.serve(template, show=True)
