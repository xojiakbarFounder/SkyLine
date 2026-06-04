class ErrorHandler:

    @staticmethod
    def validate_airport(code, airports):
        airport_codes = [
            airport["code"]
            for airport in airports.values()
        ]

        if code not in airport_codes:
            raise ValueError(
                f"Airport '{code}' does not exist."
            )

    @staticmethod
    def validate_route(start, destination):
        if start == destination:
            raise ValueError(
                "Origin and destination cannot be the same."
            )

    @staticmethod
    def validate_price_range(min_price, max_price):
        if min_price > max_price:
            raise ValueError(
                "Minimum price cannot exceed maximum price."
            )