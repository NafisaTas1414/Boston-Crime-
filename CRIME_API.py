"""
Nafisa Tasnia
DS3500
1/31/2025
Homework 3: Build dashboard (This is my Crime API)
"""
import sqlite3
import pandas as pd

class Crime_API:

    # this path is for me to get connected to my database
    def __init__(self, db_path="/Users/nt/Desktop/Crime/crime_dashboard.db"):
        """Initialize the connection to the SQLite database."""
        self.db_path = db_path

    def get_db_connection(self):
        """Create and return a connection to the database."""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """Run a SQL query and return a DataFrame."""
        with self.get_db_connection() as conn:
            return pd.read_sql(query, conn, params=params)

    def fetch_boston_top_crimes(self, year: int = None, limit: int = 10) -> pd.DataFrame:
        """Fetch the top N most frequent crimes in Boston for a given year."""
        query = """
            SELECT LOWER(OFFENSE_DESCRIPTION) AS Crime, COUNT(*) AS crime_count
            FROM boston_crime
        """
        params = []

        if year:
            query += " WHERE YEAR = ?"
            params.append(year)

        query += " GROUP BY Crime ORDER BY crime_count DESC LIMIT ?;"
        params.append(limit)

        return self.execute_query(query, tuple(params))

    def fetch_top_districts(self, year):
        """Fetch the top 5 districts with the highest crime counts in Boston for a given year."""
        query = """
            SELECT DISTRICT, crime_count
            FROM crime_count_by_district_year
            WHERE YEAR = ?
            ORDER BY crime_count DESC
            LIMIT 5;
        """
        return self.execute_query(query, (year,))

    def fetch_crime_by_day_of_week(self, year):
        """Fetch total crime counts grouped by day of the week for a selected year."""
        query = """
            SELECT LOWER(DAY_OF_WEEK) AS DAY_OF_WEEK, COUNT(*) AS crime_count
            FROM boston_crime
            WHERE YEAR = ?
            GROUP BY DAY_OF_WEEK
        """
        df = self.execute_query(query, (year,))

        # Ensure all weekdays are represented, even if some have zero crimes
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        crime_dict = {day: 0 for day in weekdays}

        for _, row in df.iterrows():
            crime_dict[row["DAY_OF_WEEK"].strip().lower()] = row["crime_count"]

        final_df = pd.DataFrame(list(crime_dict.items()), columns=["DAY_OF_WEEK", "crime_count"])
        final_df["DAY_OF_WEEK"] = pd.Categorical(final_df["DAY_OF_WEEK"], categories=weekdays, ordered=True)

        return final_df.sort_values("DAY_OF_WEEK")

    def fetch_crime_by_month_all_years(self):
        """Fetch total crime counts grouped by month for all years."""
        query = """
            SELECT YEAR, MONTH, COUNT(*) AS crime_count
            FROM boston_crime
            GROUP BY YEAR, MONTH
            ORDER BY YEAR, MONTH
        """
        df = self.execute_query(query)

        df = df.dropna(subset=["MONTH"])
        df["YEAR"] = df["YEAR"].astype(int)
        df["MONTH"] = df["MONTH"].astype(int)

        return df

    def fetch_crime_category_proportions(self, selected_category: str) -> pd.DataFrame:
        """
        Fetch crime counts for a selected category vs. all other crimes per year.
        """
        query = """
            SELECT 
                YEAR,
                SUM(CASE WHEN CRIME_CATEGORY = ? THEN crime_count ELSE 0 END) AS selected_category,
                SUM(crime_count) AS total_crimes
            FROM crime_category_counts
            WHERE YEAR IS NOT NULL
            GROUP BY YEAR
            ORDER BY YEAR;
        """
        df = self.execute_query(query, (selected_category,))

        # Calculate the count of all other crimes by subtracting the selected category count from the total
        df["Other Crimes"] = df["total_crimes"] - df["selected_category"]

        # Rename the selected category column for clarity
        df = df.rename(columns={"selected_category": selected_category})

        return df[["YEAR", selected_category, "Other Crimes"]]

    def fetch_crime_locations(self, year, crime_type="All Crimes"):
        """Fetch crime locations (Lat, Long) for a selected year."""
        query = """
            SELECT Lat, Long
            FROM boston_crime
            WHERE YEAR = ?
            AND Lat IS NOT NULL 
            AND Long IS NOT NULL
        """
        params = [year]

        if crime_type != "All Crimes":
            query += " AND LOWER(OFFENSE_DESCRIPTION) = LOWER(?)"
            params.append(crime_type)

        return self.execute_query(query, tuple(params))

    def get_unique_crime_categories(self):
        """Fetch distinct crime categories from the crime_category_counts table."""
        query = "SELECT DISTINCT CRIME_CATEGORY FROM crime_category_counts ORDER BY CRIME_CATEGORY ASC;"
        df = self.execute_query(query)
        return df["CRIME_CATEGORY"].tolist()

    def fetch_sankey_data(self, start_year=2020, end_year=2025):
        """Fetch the top 3 crime categories per district per year."""
        query = """
            WITH RankedCrimes AS (
                SELECT
                    b.YEAR AS Year,
                    b.DISTRICT AS District,
                    c.CRIME_CATEGORY AS Crime_Category,
                    SUM(c.crime_count) AS Crime_Count,
                    RANK() OVER (
                        PARTITION BY b.YEAR, b.DISTRICT 
                        ORDER BY SUM(c.crime_count) DESC
                    ) AS rank
                FROM boston_crime b
                JOIN crime_category_counts c
                ON b.YEAR = c.YEAR
                WHERE b.DISTRICT IS NOT NULL
                AND b.YEAR BETWEEN ? AND ?
                GROUP BY b.YEAR, b.DISTRICT, c.CRIME_CATEGORY
            )
            SELECT Year, District, Crime_Category, Crime_Count
            FROM RankedCrimes
            WHERE rank <= 3  
            ORDER BY Year DESC, District, Crime_Count DESC;
        """
        return self.execute_query(query, (start_year, end_year))

    def fetch_crime_category_trends(self, selected_category):
        """Fetch crime category trends over the years for a specific category."""
        query = """
            SELECT 
                YEAR AS "Year", 
                CRIME_CATEGORY AS "Crime Category", 
                SUM(crime_count) AS "Crime Count"
            FROM crime_category_counts
            WHERE CRIME_CATEGORY = ?
            GROUP BY YEAR, CRIME_CATEGORY
            ORDER BY YEAR ASC;
        """
        return self.execute_query(query, (selected_category,))

    def get_unique_crime_types(self):
        """
        Fetches a list of unique crime types from the database.

        Returns:
            list: A sorted list of unique crime types with "All Crimes" as the first option.
        """

        # SQL query to get distinct crime types (case-insensitive)
        query = "SELECT DISTINCT LOWER(OFFENSE_DESCRIPTION) AS Crime FROM boston_crime ORDER BY Crime ASC"

        # Execute the query and store results in a DataFrame
        df = self.execute_query(query)

        # Ensure there are no missing values and prepend "All Crimes" for UI dropdown
        return ["All Crimes"] + df["Crime"].dropna().tolist()

