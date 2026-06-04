class Passenger:
    PRIORITY_LEVELS = {
        "Platinum": 3,
        "Gold": 2,
        "Economy": 1
    }

    def __init__(self, pnr, name, ticket_status):
        self.pnr = pnr
        self.name = name
        self.ticket_status = ticket_status
        self.priority = self.PRIORITY_LEVELS.get(ticket_status, 1)

    def __str__(self):
        return f"{self.pnr} - {self.name} ({self.ticket_status})"