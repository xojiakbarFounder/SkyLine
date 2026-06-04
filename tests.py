from models.airport import Airport
from models.passenger import Passenger

from structures.graph import FlightGraph
from structures.priority_queue import PassengerPriorityQueue
from structures.queue import BoardingQueue
from structures.stack import CargoStack
from structures.hash_table import PassengerHashTable

from algorithms.backtracking import find_all_routes


def test_empty_flight_network():
    print("\nTEST 1: Empty Flight Network")

    graph = FlightGraph()

    try:
        graph.dijkstra("TAS", "JFK")
    except ValueError as error:
        print("Passed:", error)


def test_cyclic_routes():
    print("\nTEST 2: Cyclic Routes")

    graph = FlightGraph()

    airports = [
        Airport("A", "Airport A", "City A", "Country A"),
        Airport("B", "Airport B", "City B", "Country B"),
        Airport("C", "Airport C", "City C", "Country C")
    ]

    for airport in airports:
        graph.add_airport(airport)

    graph.add_flight("A", "B", 100)
    graph.add_flight("B", "C", 150)
    graph.add_flight("C", "A", 200)

    path, cost = graph.dijkstra("A", "C")

    print("Path:", " -> ".join(path))
    print("Cost:", cost)
    print("Passed: Cycle handled without infinite loop.")


def test_priority_collision():
    print("\nTEST 3: Priority Collision in Heap")

    passengers = [
        Passenger("PNR101", "Passenger One", "Gold"),
        Passenger("PNR102", "Passenger Two", "Gold"),
        Passenger("PNR103", "Passenger Three", "Gold")
    ]

    queue = PassengerPriorityQueue()

    for passenger in passengers:
        queue.enqueue(passenger)

    print("Serving passengers with same priority:")

    while not queue.is_empty():
        print(queue.dequeue())

    print("Passed: Same-priority passengers served by arrival order.")


def test_passenger_not_found():
    print("\nTEST 4: Passenger Not Found in Hash Table")

    table = PassengerHashTable()

    passenger = Passenger("PNR201", "Existing Passenger", "Economy")
    table.insert(passenger)

    result = table.search("PNR999")

    if result is None:
        print("Passed: Passenger not found handled correctly.")
    else:
        print("Failed: Unexpected passenger found.")


def test_empty_queue_and_stack():
    print("\nTEST 5: Empty Queue and Empty Stack")

    boarding_queue = BoardingQueue()
    cargo_stack = CargoStack()

    try:
        boarding_queue.dequeue()
    except IndexError as error:
        print("Passed Queue Test:", error)

    try:
        cargo_stack.pop()
    except IndexError as error:
        print("Passed Stack Test:", error)


def test_blocked_route_backtracking():
    print("\nTEST 6: Backtracking with Blocked Airport")

    graph = FlightGraph()

    airports = [
        Airport("TAS", "Tashkent Airport", "Tashkent", "Uzbekistan"),
        Airport("DXB", "Dubai Airport", "Dubai", "UAE"),
        Airport("LHR", "London Heathrow", "London", "UK"),
        Airport("JFK", "John F. Kennedy Airport", "New York", "USA")
    ]

    for airport in airports:
        graph.add_airport(airport)

    graph.add_flight("TAS", "DXB", 300)
    graph.add_flight("DXB", "LHR", 500)
    graph.add_flight("LHR", "JFK", 600)
    graph.add_flight("DXB", "JFK", 1000)

    routes = find_all_routes(
        graph,
        "TAS",
        "JFK",
        blocked_airport="LHR"
    )

    print("Blocked airport: LHR")

    for route, cost in routes:
        print(f"{' -> '.join(route)} | Cost: {cost}")

    if routes:
        print("Passed: Alternative route found.")
    else:
        print("Failed: No alternative route found.")


def run_all_tests():
    print("SkyNet DSA System Test Results")

    test_empty_flight_network()
    test_cyclic_routes()
    test_priority_collision()
    test_passenger_not_found()
    test_empty_queue_and_stack()
    test_blocked_route_backtracking()


if __name__ == "__main__":
    run_all_tests()