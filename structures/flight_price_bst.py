class FlightPriceNode:
    def __init__(self, flight):
        self.flight = flight
        self.price = flight["cost"]
        self.left = None
        self.right = None


class FlightPriceBST:
    def __init__(self):
        self.root = None

    def insert(self, flight):
        self.root = self._insert(self.root, flight)

    def _insert(self, node, flight):
        if node is None:
            return FlightPriceNode(flight)

        if flight["cost"] < node.price:
            node.left = self._insert(node.left, flight)
        else:
            node.right = self._insert(node.right, flight)

        return node

    def range_search(self, min_price, max_price):
        results = []
        self._range_search(self.root, min_price, max_price, results)
        return results

    def _range_search(self, node, min_price, max_price, results):
        if node is None:
            return

        if node.price > min_price:
            self._range_search(node.left, min_price, max_price, results)

        if min_price <= node.price <= max_price:
            results.append(node.flight)

        if node.price < max_price:
            self._range_search(node.right, min_price, max_price, results)

    def inorder(self):
        results = []
        self._inorder(self.root, results)
        return results

    def _inorder(self, node, results):
        if node:
            self._inorder(node.left, results)
            results.append(node.flight)
            self._inorder(node.right, results)