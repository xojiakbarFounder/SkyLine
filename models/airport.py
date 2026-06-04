class Airport:
    def __init__(self, code, name, city, country):
        self.code = code
        self.name = name
        self.city = city
        self.country = country

    def __str__(self):
        return f"{self.code} - {self.name}, {self.city}, {self.country}"