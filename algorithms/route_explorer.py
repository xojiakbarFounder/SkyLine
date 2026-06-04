class RouteExplorer:
    def __init__(self, graph):
        self.graph = graph

    def find_all_routes(self, start, destination, max_stops=2):
        routes = []
        visited = set()

        def dfs(current, path, total_cost):
            stops = len(path) - 2

            if stops > max_stops:
                return

            if current == destination:
                routes.append({
                    "path": path.copy(),
                    "cost": total_cost,
                    "stops": max(0, len(path) - 2),
                    "type": self._route_type(path)
                })
                return

            visited.add(current)

            for neighbour, cost in self.graph.adjacency_list.get(current, []):
                if neighbour not in visited:
                    path.append(neighbour)
                    dfs(neighbour, path, total_cost + cost)
                    path.pop()

            visited.remove(current)

        dfs(start, [start], 0)

        routes.sort(key=lambda route: (route["cost"], route["stops"]))
        return routes

    def find_best_route(self, start, destination, max_stops=2):
        routes = self.find_all_routes(start, destination, max_stops)

        if not routes:
            return None

        return routes[0]

    def build_route_tree(self, start, max_depth=3):
        tree = {}

        def dfs(current, depth, visited):
            if depth == 0:
                return {}

            branch = {}

            for neighbour, cost in self.graph.adjacency_list.get(current, []):
                if neighbour not in visited:
                    branch[neighbour] = {
                        "cost": cost,
                        "connections": dfs(
                            neighbour,
                            depth - 1,
                            visited | {neighbour}
                        )
                    }

            return branch

        tree[start] = dfs(start, max_depth, {start})
        return tree

    def _route_type(self, path):
        stops = len(path) - 2

        if stops == 0:
            return "Direct flight"
        elif stops == 1:
            return "One-stop flight"
        else:
            return f"{stops}-stop flight"