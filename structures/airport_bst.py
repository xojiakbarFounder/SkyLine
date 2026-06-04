class AirportNode:
    def __init__(self, airport):
        self.airport = airport
        self.left = None
        self.right = None


class AirportBST:
    def __init__(self):
        self.root = None

    def insert(self, airport):
        self.root = self._insert(self.root, airport)

    def _insert(self, node, airport):
        if node is None:
            return AirportNode(airport)

        if airport["code"] < node.airport["code"]:
            node.left = self._insert(node.left, airport)
        else:
            node.right = self._insert(node.right, airport)

        return node

    def search(self, code):
        return self._search(self.root, code)

    def _search(self, node, code):
        if node is None:
            return None

        if code == node.airport["code"]:
            return node.airport

        if code < node.airport["code"]:
            return self._search(node.left, code)

        return self._search(node.right, code)

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.airport)
            self._inorder(node.right, result)