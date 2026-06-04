from collections import deque


class BoardingQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, passenger):
        self.queue.append(passenger)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Boarding queue is empty.")

        return self.queue.popleft()

    def is_empty(self):
        return len(self.queue) == 0

    def display(self):
        if self.is_empty():
            print("Boarding queue is empty.")
            return

        print("\nBoarding FIFO Queue:")
        for passenger in self.queue:
            print(passenger)