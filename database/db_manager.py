import sqlite3
import pandas as pd


class DatabaseManager:
    def __init__(self, db_path="skynet.db"):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        airports_df = pd.read_csv("data/airports.csv")
        flights_df = pd.read_csv("data/flights.csv")

        connection = self.connect()

        airports_df.to_sql(
            "airports",
            connection,
            if_exists="replace",
            index=False
        )

        flights_df.to_sql(
            "flights",
            connection,
            if_exists="replace",
            index=False
        )

        connection.close()

    def get_all_airports(self):
        connection = self.connect()
        df = pd.read_sql_query("SELECT * FROM airports", connection)
        connection.close()
        return df

    def get_all_flights(self):
        connection = self.connect()
        df = pd.read_sql_query("SELECT * FROM flights", connection)
        connection.close()
        return df

    def search_flight(self, flight_no):
        connection = self.connect()

        query = """
        SELECT * FROM flights
        WHERE flight_no = ?
        """

        df = pd.read_sql_query(query, connection, params=(flight_no,))
        connection.close()
        return df

    def get_airport_movements(self, airport_code):
        connection = self.connect()

        query = """
        SELECT * FROM flights
        WHERE "from" = ? OR "to" = ?
        """

        df = pd.read_sql_query(
            query,
            connection,
            params=(airport_code, airport_code)
        )

        connection.close()
        return df