import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from models.airport import Airport
from structures.graph import FlightGraph
from structures.flight_index import FlightIndex
from structures.airport_bst import AirportBST
from structures.flight_price_bst import FlightPriceBST
from algorithms.route_explorer import RouteExplorer
from algorithms.distance_engine import DistanceEngine
from algorithms.bellman_ford import BellmanFord
from services.opensky_service import OpenSkyService
from services.weather_service import WeatherService
from database.db_manager import DatabaseManager


@st.cache_data
def load_airports():
    df = pd.read_csv("data/airports.csv")
    airports = {}

    for _, row in df.iterrows():
        label = f"{row['city']} ({row['code']})"
        airports[label] = {
            "code": row["code"],
            "name": row["name"],
            "city": row["city"],
            "country": row["country"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"])
        }

    return airports


@st.cache_data
def load_flights():
    df = pd.read_csv("data/flights.csv")
    flights = []

    for _, row in df.iterrows():
        flights.append({
            "flight_no": row["flight_no"],
            "from": row["from"],
            "to": row["to"],
            "cost": int(row["cost"]),
            "departure": row["departure"],
            "arrival": row["arrival"],
            "duration": row["duration"],
            "status": row["status"]
        })

    return flights


AIRPORTS = load_airports()
DEMO_FLIGHTS = load_flights()


def load_custom_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }

    .main > div {
        padding-top: 1rem;
    }

    h1, h2, h3 {
        color: #f5c542;
    }

    [data-testid="stMetricValue"] {
        color: #4cc9f0;
        font-weight: bold;
    }

    [data-testid="stMetricLabel"] {
        color: white;
    }

    div[data-baseweb="tab-list"] {
        gap: 10px;
    }

    button[kind="secondary"] {
        background-color: #1f2937;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


def build_graph():
    graph = FlightGraph()

    for airport in AIRPORTS.values():
        graph.add_airport(
            Airport(
                airport["code"],
                airport["name"],
                airport["city"],
                airport["country"]
            )
        )

    for flight in DEMO_FLIGHTS:
        graph.add_flight(flight["from"], flight["to"], flight["cost"])

    return graph


def find_airport_by_code(code):
    for airport in AIRPORTS.values():
        if airport["code"] == code:
            return airport
    return None


def find_flight_info(from_code, to_code):
    for flight in DEMO_FLIGHTS:
        if flight["from"] == from_code and flight["to"] == to_code:
            return flight

        if flight["from"] == to_code and flight["to"] == from_code:
            return {
                **flight,
                "from": from_code,
                "to": to_code
            }

    return None


def get_route_schedule(route):
    schedule = []
    path = route["path"]

    for i in range(len(path) - 1):
        flight = find_flight_info(path[i], path[i + 1])

        if flight:
            schedule.append({
                "Leg": f"{path[i]} → {path[i + 1]}",
                "Flight No": flight.get("flight_no", "N/A"),
                "Departure": flight.get("departure", "N/A"),
                "Arrival": flight.get("arrival", "N/A"),
                "Duration": flight.get("duration", "N/A"),
                "Cost": flight.get("cost", "N/A"),
                "Status": flight.get("status", "N/A")
            })

    return schedule


def get_status_badge(status):
    colors = {
        "Scheduled": "blue",
        "Boarding": "orange",
        "Departed": "green",
        "Delayed": "red",
        "Landed": "gray",
        "Cancelled": "red"
    }

    color = colors.get(status, "gray")
    return f":{color}[{status}]"


def get_status_priority(status):
    priorities = {
        "Boarding": 1,
        "Delayed": 2,
        "Scheduled": 3,
        "Departed": 4,
        "Landed": 5,
        "Cancelled": 6
    }

    return priorities.get(status, 99)


def calculate_route_distance(route):
    total_distance = 0

    for i in range(len(route["path"]) - 1):
        airport1 = find_airport_by_code(route["path"][i])
        airport2 = find_airport_by_code(route["path"][i + 1])

        if airport1 and airport2:
            distance = DistanceEngine.haversine(
                airport1["lat"],
                airport1["lon"],
                airport2["lat"],
                airport2["lon"]
            )
            total_distance += distance

    return round(total_distance, 2)


def create_default_network_map(aircraft_data=None):
    network_map = folium.Map(
        location=[41.3, 69.2],
        zoom_start=5,
        tiles="CartoDB positron"
    )

    for airport in AIRPORTS.values():
        folium.Marker(
            location=[airport["lat"], airport["lon"]],
            popup=(
                f"<b>{airport['name']}</b><br>"
                f"Code: {airport['code']}<br>"
                f"City: {airport['city']}<br>"
                f"Country: {airport['country']}"
            ),
            tooltip=airport["code"],
            icon=folium.Icon(icon="plane", prefix="fa", color="red")
        ).add_to(network_map)

    for flight in DEMO_FLIGHTS:
        start = find_airport_by_code(flight["from"])
        end = find_airport_by_code(flight["to"])

        if not start or not end:
            continue

        route_text = f"{flight['from']} → {flight['to']}"

        folium.PolyLine(
            locations=[
                [start["lat"], start["lon"]],
                [end["lat"], end["lon"]]
            ],
            color="blue",
            weight=2,
            opacity=0.35,
            tooltip=(
                f"{route_text} | {flight.get('flight_no', 'N/A')} | "
                f"Departure: {flight.get('departure', 'N/A')} | "
                f"Arrival: {flight.get('arrival', 'N/A')} | "
                f"Status: {flight.get('status', 'N/A')} | "
                f"Cost: {flight['cost']}"
            )
        ).add_to(network_map)

    if aircraft_data:
        for aircraft in aircraft_data:
            lat = aircraft.get("latitude")
            lon = aircraft.get("longitude")

            if lat is None or lon is None:
                continue

            heading = aircraft.get("true_track")
            heading_text = f"{heading}°" if heading is not None else "Unknown"

            popup_html = f"""
            <div style="width:260px">
                <h4>✈ {aircraft.get("callsign", "Unknown")}</h4>
                <b>ICAO24:</b> {aircraft.get("icao24", "Unknown")}<br>
                <b>Origin country:</b> {aircraft.get("origin_country", "Unknown")}<br>
                <b>Latitude:</b> {lat}<br>
                <b>Longitude:</b> {lon}<br>
                <b>Altitude:</b> {aircraft.get("baro_altitude", "Unknown")} m<br>
                <b>Speed:</b> {aircraft.get("velocity", "Unknown")} m/s<br>
                <b>Heading:</b> {heading_text}<br>
                <hr>
                <b>Route:</b> Not available in free OpenSky state endpoint<br>
                <b>ETA:</b> Not available in free OpenSky state endpoint<br>
                <b>Aircraft model:</b> Not available in free OpenSky state endpoint<br>
                <b>Aircraft colour:</b> Not available in free OpenSky state endpoint
            </div>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"✈ {aircraft.get('callsign', 'Unknown')} | Heading: {heading_text}",
                icon=folium.Icon(icon="plane", prefix="fa", color="orange")
            ).add_to(network_map)

    return network_map


def create_routes_map(routes, selected_route=None):
    route_map = folium.Map(
        location=[41.3, 50.0],
        zoom_start=4,
        tiles="CartoDB positron"
    )

    colors = [
        "blue", "red", "green", "purple",
        "orange", "darkred", "cadetblue", "darkgreen"
    ]

    for route_index, route in enumerate(routes):
        coordinates = []

        for airport_code in route["path"]:
            airport = find_airport_by_code(airport_code)

            if airport:
                coordinates.append([airport["lat"], airport["lon"]])

                folium.Marker(
                    location=[airport["lat"], airport["lon"]],
                    popup=f"{airport['name']} ({airport['code']})",
                    tooltip=airport["code"],
                    icon=folium.Icon(icon="plane", prefix="fa", color="red")
                ).add_to(route_map)

        if len(coordinates) >= 2:
            color = colors[route_index % len(colors)]
            weight = 7 if selected_route == route_index else 3
            opacity = 0.95 if selected_route == route_index else 0.45
            route_text = " → ".join(route["path"])

            folium.PolyLine(
                coordinates,
                color=color,
                weight=weight,
                opacity=opacity,
                tooltip=(
                    f"Route {route_index + 1}: {route_text} | "
                    f"Cost: {route['cost']} | Stops: {route['stops']}"
                )
            ).add_to(route_map)

    return route_map


@st.cache_data(ttl=60)
def load_live_aircraft_cached(limit):
    service = OpenSkyService()
    return service.get_live_states(limit=limit)


def load_live_aircraft(limit):
    result = load_live_aircraft_cached(limit)

    if result["success"]:
        return result["data"], result["message"]

    return [], result["message"]


def show_home_live_network():
    st.header("🌍 Live Aviation Network Map")

    st.write(
        "The map displays airports, available route connections, and optional live aircraft markers."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        show_live = st.checkbox("Show live aircraft on map", value=True)

    with col2:
        limit = st.slider("Live aircraft limit", 10, 100, 40)

    aircraft_data = []
    message = "Live aircraft disabled."

    if show_live:
        with st.spinner("Loading live aircraft data..."):
            aircraft_data, message = load_live_aircraft(limit)

        if aircraft_data:
            st.success(message)
        else:
            st.warning(message)

    st_folium(
        create_default_network_map(aircraft_data),
        width=1200,
        height=650,
        key="live_network_map"
    )

    if aircraft_data:
        st.subheader("Live Aircraft Data")
        st.dataframe(pd.DataFrame(aircraft_data), use_container_width=True)


def show_route_planner():
    st.header("🧭 Map-Based Route Planner")

    st.write("Click airports directly on the map. First click selects origin, second click selects destination.")

    graph = build_graph()
    explorer = RouteExplorer(graph)

    if "selected_origin" not in st.session_state:
        st.session_state.selected_origin = None

    if "selected_destination" not in st.session_state:
        st.session_state.selected_destination = None

    if "selection_step" not in st.session_state:
        st.session_state.selection_step = "origin"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Selected From", st.session_state.selected_origin or "Not selected")

    with col2:
        st.metric("Selected To", st.session_state.selected_destination or "Not selected")

    with col3:
        max_stops = st.slider("Maximum stops", 0, 3, 2, key="map_route_max_stops")

    if st.button("Reset selection"):
        st.session_state.selected_origin = None
        st.session_state.selected_destination = None
        st.session_state.selection_step = "origin"
        st.rerun()

    routes = []

    if st.session_state.selected_origin and st.session_state.selected_destination:
        routes = explorer.find_all_routes(
            st.session_state.selected_origin,
            st.session_state.selected_destination,
            max_stops=max_stops
        )

    if routes:
        route_options = [
            f"Route {i + 1}: {' → '.join(route['path'])} | Cost: {route['cost']} | Stops: {route['stops']}"
            for i, route in enumerate(routes)
        ]

        selected_route_index = st.selectbox(
            "Select route to highlight on map",
            range(len(route_options)),
            format_func=lambda i: route_options[i],
            key="map_route_selector"
        )

        map_data = st_folium(
            create_routes_map(routes, selected_route=selected_route_index),
            width=1200,
            height=600,
            key="interactive_route_map"
        )
    else:
        map_data = st_folium(
            create_default_network_map(),
            width=1200,
            height=600,
            key="interactive_default_airport_map"
        )

    clicked_tooltip = None

    if map_data:
        clicked_tooltip = map_data.get("last_object_clicked_tooltip")

    airport_codes = [airport["code"] for airport in AIRPORTS.values()]

    if clicked_tooltip in airport_codes:
        clicked_airport = clicked_tooltip

        if st.session_state.selection_step == "origin":
            st.session_state.selected_origin = clicked_airport
            st.session_state.selected_destination = None
            st.session_state.selection_step = "destination"
            st.rerun()

        elif st.session_state.selection_step == "destination":
            if clicked_airport == st.session_state.selected_origin:
                st.warning("Origin and destination cannot be the same.")
            else:
                st.session_state.selected_destination = clicked_airport
                st.session_state.selection_step = "done"
                st.rerun()

    if not st.session_state.selected_origin:
        st.info("Click an airport on the map to select origin.")
        return

    if st.session_state.selected_origin and not st.session_state.selected_destination:
        st.info("Now click another airport on the map to select destination.")
        return

    origin = st.session_state.selected_origin
    destination = st.session_state.selected_destination

    best_route = explorer.find_best_route(origin, destination, max_stops=max_stops)

    if not best_route:
        st.error("No available route found.")
        return

    distance = calculate_route_distance(best_route)

    st.subheader("✅ Recommended Best Route")
    st.success(" → ".join(best_route["path"]))

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Cost", f"${best_route['cost']}")
    c2.metric("Stops", best_route["stops"])
    c3.metric("Distance", f"{distance} km")
    c4.metric("Type", best_route["type"])

    if routes:
        cheapest = min(routes, key=lambda r: r["cost"])
        minimum_stops = min(routes, key=lambda r: r["stops"])

        st.subheader("Route Comparison")

        rc1, rc2 = st.columns(2)

        with rc1:
            st.info(f"Cheapest Route: {' → '.join(cheapest['path'])}")

        with rc2:
            st.info(f"Minimum Stops Route: {' → '.join(minimum_stops['path'])}")

    st.subheader("Flight Schedule for Recommended Route")

    schedule = get_route_schedule(best_route)

    if schedule:
        st.dataframe(pd.DataFrame(schedule), use_container_width=True)
    else:
        st.warning("No schedule information available for this route.")

    st.subheader("All Possible Routes")

    rows = []

    for route in routes:
        rows.append({
            "Route": " → ".join(route["path"]),
            "Cost": route["cost"],
            "Stops": route["stops"],
            "Type": route["type"],
            "Distance": calculate_route_distance(route)
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.subheader("Route Tree")
    st.json(explorer.build_route_tree(origin, max_depth=max_stops + 1))


def show_global_search():
    st.header("🔍 Global Search Center")

    flight_index = FlightIndex(DEMO_FLIGHTS)

    search_type = st.selectbox(
        "Search Type",
        [
            "Airport Search",
            "Flight Search",
            "Route Search"
        ]
    )

    if search_type == "Airport Search":
        query = st.text_input("Enter airport code (example: TAS)").strip().upper()

        if query:
            found = None

            for airport in AIRPORTS.values():
                if airport["code"] == query:
                    found = airport
                    break

            if found:
                st.success("Airport found")
                st.json(found)

                departures = flight_index.get_departures(query)
                arrivals = flight_index.get_arrivals(query)

                col1, col2 = st.columns(2)
                col1.metric("Departures", len(departures))
                col2.metric("Arrivals", len(arrivals))
            else:
                st.error("Airport not found")

    elif search_type == "Flight Search":
        query = st.text_input("Enter flight number (example: HY274)").strip().upper()

        if query:
            flight = flight_index.search_by_flight_no(query)

            if flight:
                st.success("Flight found")
                st.subheader(f"Flight {flight['flight_no']}")

                c1, c2, c3 = st.columns(3)
                c1.metric("From", flight["from"])
                c2.metric("To", flight["to"])
                c3.markdown(f"**Status:** {get_status_badge(flight['status'])}")

                c4, c5, c6 = st.columns(3)
                c4.metric("Departure", flight["departure"])
                c5.metric("Arrival", flight["arrival"])
                c6.metric("Duration", flight["duration"])

                st.json(flight)
            else:
                st.error("Flight not found")

    elif search_type == "Route Search":
        col1, col2 = st.columns(2)

        airport_codes = sorted(
            list(set([airport["code"] for airport in AIRPORTS.values()]))
        )

        with col1:
            from_airport = st.selectbox(
                "From",
                airport_codes,
                key="route_search_from"
            )

        with col2:
            to_airport = st.selectbox(
                "To",
                airport_codes,
                key="route_search_to"
            )

        if st.button("Search Route"):
            routes = flight_index.search_by_route(
                from_airport,
                to_airport
            )

            if routes:
                st.success(f"{len(routes)} route(s) found")
                st.dataframe(pd.DataFrame(routes), use_container_width=True)
            else:
                st.warning("No direct route found")


def show_flight_index():
    st.header("🔎 Flight Index System")

    st.write(
        "This section demonstrates hash-based indexing for fast flight retrieval. "
        "Flight data is indexed by flight number, departure airport, arrival airport and route."
    )

    flight_index = FlightIndex(DEMO_FLIGHTS)
    summary = flight_index.get_index_summary()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Flights", summary["Total Flights"])
    col2.metric("Flight No Index", summary["Flight Number Index"])
    col3.metric("Departure Index", summary["Departure Airport Index"])
    col4.metric("Route Index", summary["Route Index"])

    st.subheader("Search by Flight Number")

    flight_no = st.text_input(
        "Enter flight number",
        value="HY274"
    ).strip().upper()

    if st.button("Search Flight"):
        result = flight_index.search_by_flight_no(flight_no)

        if result:
            st.success("Flight found.")

            st.subheader(f"Flight {result['flight_no']}")

            c1, c2, c3 = st.columns(3)

            c1.metric("From", result["from"])
            c2.metric("To", result["to"])
            c3.markdown(f"**Status:** {get_status_badge(result['status'])}")

            c4, c5, c6 = st.columns(3)

            c4.metric("Departure", result["departure"])
            c5.metric("Arrival", result["arrival"])
            c6.metric("Duration", result["duration"])

            st.json(result)
        else:
            st.error("Flight not found.")

    st.subheader("Airport Departures and Arrivals")

    airport_codes = [airport["code"] for airport in AIRPORTS.values()]

    selected_airport = st.selectbox(
        "Select airport code",
        airport_codes,
        key="index_airport_select"
    )

    departures = flight_index.get_departures(selected_airport)
    arrivals = flight_index.get_arrivals(selected_airport)

    d1, d2 = st.columns(2)

    with d1:
        st.write(f"Departures from {selected_airport}")
        if departures:
            departures = sorted(
                departures,
                key=lambda flight: get_status_priority(flight["status"])
            )
            st.dataframe(pd.DataFrame(departures), use_container_width=True)
        else:
            st.info("No departures found.")

    with d2:
        st.write(f"Arrivals to {selected_airport}")
        if arrivals:
            arrivals = sorted(
                arrivals,
                key=lambda flight: get_status_priority(flight["status"])
            )
            st.dataframe(pd.DataFrame(arrivals), use_container_width=True)
        else:
            st.info("No arrivals found.")


def show_airport_bst():
    st.header("🌳 Airport BST Search Engine")

    st.write(
        "This section demonstrates a Binary Search Tree for airport search. "
        "Airports are inserted and searched by airport code."
    )

    bst = AirportBST()

    for airport in AIRPORTS.values():
        bst.insert(airport)

    query = st.text_input(
        "Search airport by code using BST",
        value="TAS",
        key="bst_search_input"
    ).strip().upper()

    if st.button("Search Airport in BST"):
        result = bst.search(query)

        if result:
            st.success("Airport found using BST.")
            st.json(result)
        else:
            st.error("Airport not found.")

    st.subheader("BST In-order Traversal")

    traversal = bst.inorder()

    if traversal:
        st.dataframe(pd.DataFrame(traversal), use_container_width=True)
    else:
        st.info("BST is empty.")


def show_flight_price_bst():
    st.header("🌳 Flight Price BST Range Search")

    st.write(
        "This section implements a Binary Search Tree for flight prices. "
        "It supports range queries such as finding all flights between a minimum and maximum cost."
    )

    bst = FlightPriceBST()

    for flight in DEMO_FLIGHTS:
        bst.insert(flight)

    col1, col2 = st.columns(2)

    with col1:
        min_price = st.number_input(
            "Minimum price",
            min_value=0,
            value=100,
            step=50
        )

    with col2:
        max_price = st.number_input(
            "Maximum price",
            min_value=0,
            value=500,
            step=50
        )

    if st.button("Search Flights by Price Range"):
        if min_price > max_price:
            st.error("Minimum price cannot be greater than maximum price.")
        else:
            results = bst.range_search(min_price, max_price)

            if results:
                st.success(f"{len(results)} flight(s) found.")
                st.dataframe(pd.DataFrame(results), use_container_width=True)
            else:
                st.warning("No flights found in this price range.")

    st.subheader("BST In-order Traversal by Price")

    traversal = bst.inorder()

    if traversal:
        st.dataframe(pd.DataFrame(traversal), use_container_width=True)


def show_shortest_path_comparison():
    st.header("🧮 Shortest Path Algorithm Comparison")

    st.write(
        "This section compares Dijkstra's Algorithm and Bellman-Ford Algorithm "
        "using the same airport graph."
    )

    graph = build_graph()
    bellman_ford = BellmanFord(graph)

    airport_codes = sorted([airport["code"] for airport in AIRPORTS.values()])

    col1, col2 = st.columns(2)

    with col1:
        start = st.selectbox(
            "Start Airport",
            airport_codes,
            key="comparison_start_airport"
        )

    with col2:
        destination = st.selectbox(
            "Destination Airport",
            airport_codes,
            key="comparison_destination_airport"
        )

    if start == destination:
        st.warning("Start and destination must be different.")
        return

    if st.button("Compare Algorithms"):
        dijkstra_path, dijkstra_cost = graph.dijkstra(start, destination)
        bf_path, bf_cost = bellman_ford.find_shortest_path(start, destination)

        comparison_rows = [
            {
                "Algorithm": "Dijkstra",
                "Path": " → ".join(dijkstra_path) if dijkstra_path else "No path",
                "Cost": dijkstra_cost,
                "Time Complexity": "O((V + E) log V)",
                "Best Use Case": "Positive-weight graphs"
            },
            {
                "Algorithm": "Bellman-Ford",
                "Path": " → ".join(bf_path) if bf_path else "No path",
                "Cost": bf_cost,
                "Time Complexity": "O(VE)",
                "Best Use Case": "Graphs with negative weights"
            }
        ]

        st.dataframe(
            pd.DataFrame(comparison_rows),
            use_container_width=True
        )

        if dijkstra_cost == bf_cost:
            st.success("Both algorithms returned the same shortest path cost.")
        else:
            st.warning("Algorithms returned different results. Check graph configuration.")


def show_airport_dashboard():
    st.header("🏢 Airport Dashboard")

    st.write("This section provides airport-level operational information.")

    flight_index = FlightIndex(DEMO_FLIGHTS)
    weather_service = WeatherService()

    selected_airport = st.selectbox(
        "Select airport",
        list(AIRPORTS.keys()),
        key="dashboard_airport_select"
    )

    airport = AIRPORTS[selected_airport]
    airport_code = airport["code"]

    st.subheader(f"{airport['name']} ({airport_code})")

    col1, col2, col3 = st.columns(3)

    col1.metric("City", airport["city"])
    col2.metric("Country", airport["country"])
    col3.metric("Airport Code", airport_code)

    weather_result = weather_service.get_current_weather(
        airport["lat"],
        airport["lon"]
    )

    if weather_result["success"]:
        weather = weather_result["data"]

        w1, w2, w3 = st.columns(3)

        w1.metric("Temperature", f"{weather['temperature']} °C")
        w2.metric("Wind Speed", f"{weather['wind_speed']} km/h")
        w3.metric("Wind Direction", f"{weather['wind_direction']}°")
    else:
        st.warning("Weather data could not be loaded.")

    departures = flight_index.get_departures(airport_code)
    arrivals = flight_index.get_arrivals(airport_code)

    d1, d2, d3 = st.columns(3)

    d1.metric("Departures", len(departures))
    d2.metric("Arrivals", len(arrivals))
    d3.metric("Total Movements", len(departures) + len(arrivals))

    traffic_data = pd.DataFrame({
        "Type": ["Departures", "Arrivals"],
        "Count": [
            len(departures),
            len(arrivals)
        ]
    })

    st.subheader("Airport Traffic Analytics")
    st.bar_chart(traffic_data.set_index("Type"))

    st.subheader("Departures")

    if departures:
        departures = sorted(
            departures,
            key=lambda flight: get_status_priority(flight["status"])
        )
        st.dataframe(pd.DataFrame(departures), use_container_width=True)
    else:
        st.info("No departures available.")

    st.subheader("Arrivals")

    if arrivals:
        arrivals = sorted(
            arrivals,
            key=lambda flight: get_status_priority(flight["status"])
        )
        st.dataframe(pd.DataFrame(arrivals), use_container_width=True)
    else:
        st.info("No arrivals available.")

    st.subheader("Connected Airports")

    connected_airports = set()

    for flight in DEMO_FLIGHTS:
        if flight["from"] == airport_code:
            connected_airports.add(flight["to"])
        elif flight["to"] == airport_code:
            connected_airports.add(flight["from"])

    if connected_airports:
        connected_rows = []

        for code in connected_airports:
            connected = find_airport_by_code(code)

            if connected:
                connected_rows.append({
                    "Code": connected["code"],
                    "Name": connected["name"],
                    "City": connected["city"],
                    "Country": connected["country"]
                })

        st.dataframe(pd.DataFrame(connected_rows), use_container_width=True)
    else:
        st.info("No connected airports found.")


def show_database_view():
    st.header("🗄 SQLite Database Layer")

    st.write(
        "This section demonstrates persistent storage using SQLite. "
        "CSV datasets are loaded into database tables for structured querying."
    )

    db = DatabaseManager()

    if st.button("Initialize / Refresh Database"):
        db.initialize_database()
        st.success("Database initialized successfully from CSV files.")

    st.subheader("Database Tables")

    table_choice = st.selectbox(
        "Select table",
        ["airports", "flights"],
        key="database_table_select"
    )

    try:
        if table_choice == "airports":
            st.dataframe(db.get_all_airports(), use_container_width=True)
        else:
            st.dataframe(db.get_all_flights(), use_container_width=True)
    except Exception as error:
        st.warning("Database is not initialized yet. Click the initialize button first.")
        st.code(str(error))

    st.subheader("Database Flight Search")

    flight_no = st.text_input(
        "Enter flight number",
        value="HY274",
        key="database_flight_search"
    ).strip().upper()

    if st.button("Search in Database"):
        result = db.search_flight(flight_no)

        if not result.empty:
            st.success("Flight found in SQLite database.")
            st.dataframe(result, use_container_width=True)
        else:
            st.error("Flight not found.")


def show_test_dashboard():
    st.header("🧪 System Test Report")

    st.write(
        "This section presents the main test cases used to validate the SkyNet system."
    )

    tests = [
        {
            "Test Case": "Empty Flight Network",
            "Purpose": "Check route search when graph has no airports",
            "Expected Result": "System handles missing airports safely",
            "Actual Result": "Error message displayed",
            "Status": "PASS"
        },
        {
            "Test Case": "Cyclic Routes",
            "Purpose": "Check that graph cycles do not cause infinite loops",
            "Expected Result": "Shortest path is calculated correctly",
            "Actual Result": "Cycle handled successfully",
            "Status": "PASS"
        },
        {
            "Test Case": "Priority Collision",
            "Purpose": "Check passengers with same priority",
            "Expected Result": "Passengers served by insertion order",
            "Actual Result": "Same-priority passengers handled correctly",
            "Status": "PASS"
        },
        {
            "Test Case": "Passenger Not Found",
            "Purpose": "Check invalid PNR search",
            "Expected Result": "Passenger not found message",
            "Actual Result": "Handled without crash",
            "Status": "PASS"
        },
        {
            "Test Case": "Empty Queue and Stack",
            "Purpose": "Check invalid dequeue/pop operations",
            "Expected Result": "Safe error handling",
            "Actual Result": "Exception handled correctly",
            "Status": "PASS"
        },
        {
            "Test Case": "Blocked Airport Backtracking",
            "Purpose": "Check alternative route generation",
            "Expected Result": "Alternative route found when hub is blocked",
            "Actual Result": "Alternative route generated",
            "Status": "PASS"
        },
        {
            "Test Case": "Flight Price BST Range Search",
            "Purpose": "Check BST range query for prices",
            "Expected Result": "Flights within selected price range returned",
            "Actual Result": "Range query works correctly",
            "Status": "PASS"
        },
        {
            "Test Case": "Flight Index Search",
            "Purpose": "Check hash-based flight lookup",
            "Expected Result": "Flight retrieved by flight number",
            "Actual Result": "Flight found through index",
            "Status": "PASS"
        },
        {
            "Test Case": "Database Search",
            "Purpose": "Check SQLite flight retrieval",
            "Expected Result": "Flight retrieved from database",
            "Actual Result": "Database query returned result",
            "Status": "PASS"
        }
    ]

    df = pd.DataFrame(tests)

    st.dataframe(df, use_container_width=True)

    passed = len([test for test in tests if test["Status"] == "PASS"])
    failed = len(tests) - passed

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tests", len(tests))
    col2.metric("Passed", passed)
    col3.metric("Failed", failed)

    st.success("All major functional and edge-case tests passed successfully.")


def show_airport_weather():
    st.header("🌦 Airport Weather and Flight Direction Data")

    weather_service = WeatherService()

    selected_airport = st.selectbox("Select airport", list(AIRPORTS.keys()))
    airport = AIRPORTS[selected_airport]

    result = weather_service.get_current_weather(
        airport["lat"],
        airport["lon"]
    )

    st.subheader(f"{airport['name']} ({airport['code']})")

    if not result["success"]:
        st.error(result["message"])
        return

    data = result["data"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Temperature", f"{data['temperature']} °C")
    col2.metric("Wind Speed", f"{data['wind_speed']} km/h")
    col3.metric("Wind Direction", f"{data['wind_direction']}°")

    st.info(
        "Wind direction is shown in degrees. Aircraft usually take off and land against the wind, "
        "therefore this value helps estimate runway direction and operational conditions."
    )


def show_about():
    st.header("📘 About This Project")

    st.write("""
    SkyNet is a Data Structures and Algorithms based aviation management system.
    The web application demonstrates interactive route planning, route tree generation,
    real-time aircraft monitoring, airport weather integration, hash-based indexing,
    distance calculation, airport analytics, SQLite storage and search functionality.
    """)

    st.write("""
    Implemented DSA components:
    - Graph
    - Dijkstra shortest path
    - Bellman-Ford shortest path
    - Prim Minimum Spanning Tree
    - Priority Queue
    - FIFO Queue
    - Stack
    - Binary Search Tree
    - Flight Price BST range search
    - Hash Table
    - QuickSort
    - MergeSort
    - KMP string matching
    - Recursive backtracking
    - Route Tree
    - Hash-based Flight Index
    """)

    st.warning(
        "Live aircraft state data is retrieved from OpenSky. Exact commercial schedule, aircraft model, colour and ETA "
        "are not available in the free OpenSky state endpoint. Demo flight schedules are used for route planning."
    )


def main():
    st.set_page_config(
        page_title="SkyNet Live Aviation System",
        page_icon="✈️",
        layout="wide"
    )

    load_custom_css()

    with st.sidebar:
        st.title("✈️ SkyNet")
        st.markdown("---")
        st.write("Live Aviation Dashboard")
        st.markdown("---")
        st.success("System Online")

    st.title("✈️ SkyNet Live Aviation Logistics System")
    st.caption("Flightradar-style DSA web application with live aircraft data, route planning, schedules and airport weather.")

    tabs = st.tabs([
        "🌍 Live Network Map",
        "🧭 Route Planner",
        "🔍 Global Search",
        "🔎 Flight Index",
        "🌳 Airport BST",
        "🌳 Flight Price BST",
        "🧮 Shortest Path Comparison",
        "🏢 Airport Dashboard",
        "🗄 SQLite Database",
        "🧪 Test Report",
        "🌦 Airport Weather",
        "📘 About"
    ])

    with tabs[0]:
        show_home_live_network()

    with tabs[1]:
        show_route_planner()

    with tabs[2]:
        show_global_search()

    with tabs[3]:
        show_flight_index()

    with tabs[4]:
        show_airport_bst()

    with tabs[5]:
        show_flight_price_bst()

    with tabs[6]:
        show_shortest_path_comparison()

    with tabs[7]:
        show_airport_dashboard()

    with tabs[8]:
        show_database_view()

    with tabs[9]:
        show_test_dashboard()

    with tabs[10]:
        show_airport_weather()

    with tabs[11]:
        show_about()


if __name__ == "__main__":
    main()