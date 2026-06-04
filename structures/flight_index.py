class FlightIndex:
    def __init__(self, flights):
        self.flights = flights
        self.flight_no_index = {}
        self.departure_index = {}
        self.arrival_index = {}
        self.route_index = {}

        self.build_indexes()

    def build_indexes(self):
        for flight in self.flights:
            flight_no = flight["flight_no"]
            from_airport = flight["from"]
            to_airport = flight["to"]
            route_key = f"{from_airport}-{to_airport}"

            self.flight_no_index[flight_no] = flight

            if from_airport not in self.departure_index:
                self.departure_index[from_airport] = []

            self.departure_index[from_airport].append(flight)

            if to_airport not in self.arrival_index:
                self.arrival_index[to_airport] = []

            self.arrival_index[to_airport].append(flight)

            if route_key not in self.route_index:
                self.route_index[route_key] = []

            self.route_index[route_key].append(flight)

    def search_by_flight_no(self, flight_no):
        return self.flight_no_index.get(flight_no)

    def get_departures(self, airport_code):
        return self.departure_index.get(airport_code, [])

    def get_arrivals(self, airport_code):
        return self.arrival_index.get(airport_code, [])

    def search_by_route(self, from_airport, to_airport):
        route_key = f"{from_airport}-{to_airport}"
        return self.route_index.get(route_key, [])

    def get_index_summary(self):
        return {
            "Total Flights": len(self.flights),
            "Flight Number Index": len(self.flight_no_index),
            "Departure Airport Index": len(self.departure_index),
            "Arrival Airport Index": len(self.arrival_index),
            "Route Index": len(self.route_index),
        }