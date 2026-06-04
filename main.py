from models.airport import Airport
from structures.graph import FlightGraph
from models.passenger import Passenger
from structures.priority_queue import PassengerPriorityQueue
from structures.queue import BoardingQueue
from structures.stack import CargoStack
from structures.bst import FlightPriceBST
from structures.hash_table import PassengerHashTable
from algorithms.sorting import quick_sort, merge_sort
from algorithms.kmp import kmp_search
from algorithms.backtracking import find_all_routes
from algorithms.route_explorer import RouteExplorer

def main():
    print("SkyNet Global Aviation Logistics & Management System")
    print("Phase 1: Flight Network using Graph, Dijkstra, and Prim MST")

    graph = FlightGraph()

    airports = [
        Airport("TAS", "Islam Karimov Tashkent International Airport", "Tashkent", "Uzbekistan"),
        Airport("DXB", "Dubai International Airport", "Dubai", "UAE"),
        Airport("IST", "Istanbul Airport", "Istanbul", "Turkey"),
        Airport("LHR", "Heathrow Airport", "London", "United Kingdom"),
        Airport("JFK", "John F. Kennedy International Airport", "New York", "USA")
    ]

    for airport in airports:
        graph.add_airport(airport)

    graph.add_flight("TAS", "DXB", 300)
    graph.add_flight("TAS", "IST", 250)
    graph.add_flight("DXB", "LHR", 500)
    graph.add_flight("IST", "LHR", 350)
    graph.add_flight("LHR", "JFK", 600)
    graph.add_flight("DXB", "JFK", 1000)
    graph.add_flight("IST", "DXB", 400)
    graph.add_flight("IST", "JFK", 900)
    graph.add_flight("DXB", "TAS", 300)

    graph.display_network()

    print("\nFinding cheapest route from TAS to JFK...")
    path, cost = graph.dijkstra("TAS", "JFK")

    if not path:
        print("No route found.")
    else:
        print("Best Route:", " -> ".join(path))
        print("Total Cost:", cost)

    print("\nBackup Communication Network using Prim MST")
    mst, total = graph.prim_mst("TAS")

    for source, destination, cost in mst:
        print(f"{source} -> {destination} | Cost: {cost}")

    print(f"\nTotal Infrastructure Cost: {total}")

    # PHASE 2 SHU YERDAN BOSHLANADI
    print("\nPhase 2: Passenger Priority & Check-in System")

    passengers = [
        Passenger("PNR001", "Ali Karimov", "Economy"),
        Passenger("PNR002", "Sarah Johnson", "Gold"),
        Passenger("PNR003", "John Smith", "Platinum"),
        Passenger("PNR004", "Dilshod Akramov", "Economy"),
        Passenger("PNR005", "Aisha Rahman", "Gold")
    ]

    check_in_queue = PassengerPriorityQueue()

    for passenger in passengers:
        check_in_queue.enqueue(passenger)

    check_in_queue.display()

    print("\nServing passengers by priority:")

    while not check_in_queue.is_empty():
        served = check_in_queue.dequeue()
        print(f"Served: {served}")
    boarding_queue = BoardingQueue()

    for passenger in passengers:
        boarding_queue.enqueue(passenger)

    boarding_queue.display()

    print("\nBoarding passengers FIFO:")
    while not boarding_queue.is_empty():
        boarded = boarding_queue.dequeue()
        print(f"Boarded: {boarded}")

    cargo_stack = CargoStack()

    cargo_items = ["BAG001", "BAG002", "BAG003", "BAG004"]

    for item in cargo_items:
        cargo_stack.push(item)

    cargo_stack.display()

    print("\nUnloading cargo LIFO:")
    while not cargo_stack.is_empty():
        unloaded = cargo_stack.pop()
        print(f"Unloaded: {unloaded}")
    print("\nPhase 3: High-Speed Search & Data Retrieval")

    price_tree = FlightPriceBST()

    flight_prices = [
        (300, "TAS-DXB"),
        (250, "TAS-IST"),
        (500, "DXB-LHR"),
        (350, "IST-LHR"),
        (600, "LHR-JFK"),
        (1000, "DXB-JFK")
    ]

    for price, flight_code in flight_prices:
        price_tree.insert(price, flight_code)

    print("\nFlights with prices between 300 and 600:")
    results = price_tree.range_query(300, 600)

    for flight_code, price in results:
        print(f"{flight_code} | Price: {price}")

    passenger_table = PassengerHashTable()

    for passenger in passengers:
        passenger_table.insert(passenger)

    passenger_table.display()

    print("\nSearching passenger by PNR:")
    search_pnr = "PNR003"
    found_passenger = passenger_table.search(search_pnr)

    if found_passenger:
        print(f"Found: {found_passenger}")
    else:
        print("Passenger not found.")

    print("\nPhase 4: Data Analytics & String Processing")

    daily_flights = [
        {"flight": "TAS-DXB", "departure_time": "14:30"},
        {"flight": "TAS-IST", "departure_time": "09:15"},
        {"flight": "DXB-LHR", "departure_time": "22:00"},
        {"flight": "IST-LHR", "departure_time": "16:45"},
        {"flight": "LHR-JFK", "departure_time": "06:20"},
        {"flight": "DXB-JFK", "departure_time": "11:10"}
    ]

    print("\nFlights sorted by departure time using QuickSort:")
    quick_sorted = quick_sort(daily_flights)

    for flight in quick_sorted:
        print(f"{flight['flight']} | Departure: {flight['departure_time']}")

    print("\nFlights sorted by departure time using MergeSort:")
    merge_sorted = merge_sort(daily_flights)

    for flight in merge_sorted:
        print(f"{flight['flight']} | Departure: {flight['departure_time']}")

    passenger_manifest = """
    Ali Karimov
    Sarah Johnson
    John Smith
    Dilshod Akramov
    Aisha Rahman
    """

    search_name = "John Smith"
    matches = kmp_search(passenger_manifest, search_name)

    print(f"\nKMP Search for passenger name: {search_name}")

    if matches:
        print(f"Pattern found at index position(s): {matches}")
    else:
        print("Pattern not found.")
    print("\nPhase 5: Contingency Planning using Backtracking")

    
    print("\nRoute Tree and Multi-Route Search")

    route_explorer = RouteExplorer(graph)

    origin = "IST"
    destination = "TAS"

    all_routes = route_explorer.find_all_routes(
        origin,
        destination,
        max_stops=2
    )

    print(f"\nAll possible routes from {origin} to {destination}:")

    if all_routes:
        for index, route in enumerate(all_routes, start=1):
            print(
                f"Route {index}: "
                f"{' -> '.join(route['path'])} | "
                f"Cost: {route['cost']} | "
                f"Stops: {route['stops']} | "
                f"{route['type']}"
            )
    else:
        print("No route found.")

    best_route = route_explorer.find_best_route(
        origin,
        destination,
        max_stops=2
    )

    print("\nRecommended Best Route:")

    if best_route:
        print(
            f"{' -> '.join(best_route['path'])} | "
            f"Cost: {best_route['cost']} | "
            f"Stops: {best_route['stops']} | "
            f"{best_route['type']}"
        )
    else:
        print("No recommended route available.")

    print("\nRoute Tree from IST:")

    route_tree = route_explorer.build_route_tree("IST", max_depth=3)
    print(route_tree)

    blocked_airport = "LHR"

    alternative_routes = find_all_routes(
        graph,
        "TAS",
        "JFK",
        blocked_airport
    )

    print(f"\nBlocked airport: {blocked_airport}")
    print("Alternative routes from TAS to JFK:")

    if alternative_routes:
        for route, route_cost in alternative_routes:
            print(f"{' -> '.join(route)} | Cost: {route_cost}")
    else:
        print("No alternative route found.")

if __name__ == "__main__":
    main()
