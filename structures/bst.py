class FlightPriceNode:
    def __init__(self, price, flight_code):
        self.price = price
        self.flight_code = flight_code
        self.left = None
        self.right = None


class FlightPriceBST:
    def __init__(self):
        self.root = None

    def insert(self, price, flight_code):
        self.root = self._insert_recursive(self.root, price, flight_code)

    def _insert_recursive(self, node, price, flight_code):
        if node is None:
            return FlightPriceNode(price, flight_code)

        if price < node.price:
            node.left = self._insert_recursive(node.left, price, flight_code)
        else:
            node.right = self._insert_recursive(node.right, price, flight_code)

        return node

    def range_query(self, min_price, max_price):
        results = []
        self._range_query_recursive(self.root, min_price, max_price, results)
        return results

    def _range_query_recursive(self, node, min_price, max_price, results):
        if node is None:
            return

        if node.price > min_price:
            self._range_query_recursive(node.left, min_price, max_price, results)

        if min_price <= node.price <= max_price:
            results.append((node.flight_code, node.price))

        if node.price < max_price:
            self._range_query_recursive(node.right, min_price, max_price, results)