class PassengerHashTable:
    def __init__(self):
        self.table = {}

    def insert(self, passenger):
        self.table[passenger.pnr] = passenger

    def search(self, pnr):
        return self.table.get(pnr)

    def display(self):
        print("\nPassenger Hash Table:")
        for pnr, passenger in self.table.items():
            print(f"{pnr}: {passenger}")