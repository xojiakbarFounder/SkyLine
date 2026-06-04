def find_all_routes(graph, start, destination, blocked_airport=None):
    if start not in graph.adjacency_list or destination not in graph.adjacency_list:
        return []

    if start == blocked_airport or destination == blocked_airport:
        return []

    all_routes = []
    visited = set()

    def backtrack(current, path, total_cost):
        if current == blocked_airport:
            return

        if current == destination:
            all_routes.append((path.copy(), total_cost))
            return

        visited.add(current)

        for neighbour, cost in graph.adjacency_list.get(current, []):
            if neighbour not in visited and neighbour != blocked_airport:
                path.append(neighbour)
                backtrack(neighbour, path, total_cost + cost)
                path.pop()

        visited.remove(current)

    backtrack(start, [start], 0)

    return all_routes
