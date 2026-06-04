import heapq


class FlightGraph:
    def __init__(self):
        self.airports = {}
        self.adjacency_list = {}

    def add_airport(self, airport):
        if airport.code not in self.airports:
            self.airports[airport.code] = airport
            self.adjacency_list[airport.code] = []

    def add_flight(self, from_code, to_code, cost):
        if from_code not in self.airports or to_code not in self.airports:
            raise ValueError("Both airports must exist before adding a flight.")

        # Undirected graph for MST
        self.adjacency_list[from_code].append((to_code, cost))
        self.adjacency_list[to_code].append((from_code, cost))

    def display_network(self):
        for airport, routes in self.adjacency_list.items():
            print(f"\n{airport} routes:")
            if not routes:
                print("  No outgoing flights")
            for destination, cost in routes:
                print(f"  -> {destination} | Cost: {cost}")

    def dijkstra(self, start_code, end_code):
        if start_code not in self.airports or end_code not in self.airports:
            raise ValueError("Start or destination airport does not exist.")

        distances = {airport: float("inf") for airport in self.airports}
        previous = {airport: None for airport in self.airports}

        distances[start_code] = 0
        priority_queue = [(0, start_code)]

        while priority_queue:
            current_distance, current_airport = heapq.heappop(priority_queue)

            if current_airport == end_code:
                break

            if current_distance > distances[current_airport]:
                continue

            for neighbour, cost in self.adjacency_list[current_airport]:
                new_distance = current_distance + cost

                if new_distance < distances[neighbour]:
                    distances[neighbour] = new_distance
                    previous[neighbour] = current_airport
                    heapq.heappush(priority_queue, (new_distance, neighbour))

        path = []
        current = end_code

        while current is not None:
            path.insert(0, current)
            current = previous[current]

        if distances[end_code] == float("inf"):
            return None, float("inf")

        return path, distances[end_code]

    def prim_mst(self, start_code):
        if start_code not in self.airports:
            raise ValueError("Start airport does not exist.")

        visited = set()
        mst_edges = []
        total_cost = 0

        min_heap = [(0, start_code, None)]

        while min_heap:
            cost, current, parent = heapq.heappop(min_heap)

            if current in visited:
                continue

            visited.add(current)

            if parent is not None:
                mst_edges.append((parent, current, cost))
                total_cost += cost

            for neighbour, weight in self.adjacency_list[current]:
                if neighbour not in visited:
                    heapq.heappush(min_heap, (weight, neighbour, current))

        return mst_edges, total_cost