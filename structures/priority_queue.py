import heapq


class PassengerPriorityQueue:
    def __init__(self):
        self.heap = []
        self.counter = 0

    def enqueue(self, passenger):
        # Python heapq is min-heap, so priority is negative for max-heap behaviour
        heapq.heappush(
            self.heap,
            (-passenger.priority, self.counter, passenger)
        )
        self.counter += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Priority queue is empty.")

        return heapq.heappop(self.heap)[2]

    def is_empty(self):
        return len(self.heap) == 0

    def display(self):
        if self.is_empty():
            print("Priority queue is empty.")
            return

        print("\nCheck-in Priority Queue:")
        for priority, order, passenger in self.heap:
            print(f"{passenger.name} | {passenger.ticket_status}")