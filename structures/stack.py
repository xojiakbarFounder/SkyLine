class CargoStack:
    def __init__(self):
        self.stack = []

    def push(self, luggage_id):
        self.stack.append(luggage_id)

    def pop(self):
        if self.is_empty():
            raise IndexError("Cargo stack is empty.")

        return self.stack.pop()

    def is_empty(self):
        return len(self.stack) == 0

    def display(self):
        if self.is_empty():
            print("Cargo stack is empty.")
            return

        print("\nCargo LIFO Stack:")
        for luggage in reversed(self.stack):
            print(luggage)