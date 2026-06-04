class BellmanFord:
    def __init__(self, graph):
        self.graph = graph

    def find_shortest_path(self, start, destination):
        airports = list(self.graph.airports.keys())

        if start not in airports or destination not in airports:
            raise ValueError("Start or destination airport does not exist.")

        distances = {airport: float("inf") for airport in airports}
        previous = {airport: None for airport in airports}

        distances[start] = 0

        edges = []

        for from_airport, neighbours in self.graph.adjacency_list.items():
            for to_airport, cost in neighbours:
                edges.append((from_airport, to_airport, cost))

        for _ in range(len(airports) - 1):
            for from_airport, to_airport, cost in edges:
                if (
                    distances[from_airport] != float("inf")
                    and distances[from_airport] + cost < distances[to_airport]
                ):
                    distances[to_airport] = distances[from_airport] + cost
                    previous[to_airport] = from_airport

        for from_airport, to_airport, cost in edges:
            if (
                distances[from_airport] != float("inf")
                and distances[from_airport] + cost < distances[to_airport]
            ):
                raise ValueError("Graph contains a negative weight cycle.")

        path = []
        current = destination

        while current is not None:
            path.insert(0, current)
            current = previous[current]

        if distances[destination] == float("inf"):
            return None, float("inf")

        return path, distances[destination]