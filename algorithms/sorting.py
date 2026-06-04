def quick_sort(flights):
    if len(flights) <= 1:
        return flights

    pivot = flights[len(flights) // 2]
    pivot_time = pivot["departure_time"]

    left = [
        flight for flight in flights
        if flight["departure_time"] < pivot_time
    ]

    middle = [
        flight for flight in flights
        if flight["departure_time"] == pivot_time
    ]

    right = [
        flight for flight in flights
        if flight["departure_time"] > pivot_time
    ]

    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(flights):
    if len(flights) <= 1:
        return flights

    mid = len(flights) // 2
    left_half = merge_sort(flights[:mid])
    right_half = merge_sort(flights[mid:])

    return merge(left_half, right_half)


def merge(left, right):
    sorted_flights = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i]["departure_time"] <= right[j]["departure_time"]:
            sorted_flights.append(left[i])
            i += 1
        else:
            sorted_flights.append(right[j])
            j += 1

    sorted_flights.extend(left[i:])
    sorted_flights.extend(right[j:])

    return sorted_flights