import csv

MAX_CAPACITY = 10.0

def read_deliveries(filename):
    deliveries = []

    with open(filename,"r",newline="",encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain a header.")

        reader.fieldnames = [
            column.strip().lower()
            for column in reader.fieldnames
        ]

        required_columns = {"id","area","priority","weight"}

        if not required_columns.issubset(reader.fieldnames):

            missing = required_columns - set(reader.fieldnames)

            missing_names = [
                column.capitalize()
                for column in missing
            ]

            raise ValueError("CSV is missing column(s): "+ ", ".join(missing_names))

        # Read every row
        for row_number, row in enumerate(reader,start=2):

            raw_id = row.get("id", "").strip()
            raw_area = row.get("area", "").strip()
            raw_priority = row.get("priority","").strip()
            raw_weight = row.get("weight","").strip()

            if raw_id == "":
                delivery_id = None
            else:
                try:
                    delivery_id = int(raw_id)
                except ValueError:
                    delivery_id = raw_id

            if raw_priority == "":
                priority = None
            else:
                try:
                    priority = int(raw_priority)
                except ValueError:
                    priority = raw_priority

            if raw_weight == "":
                weight = None
            else:
                try:
                    weight = float(raw_weight)
                except ValueError:
                    weight = raw_weight

            delivery = {"id": delivery_id,"area": raw_area,"priority": priority,"weight": weight,"row_number": row_number}

            deliveries.append(delivery)

    return deliveries


def validate_deliveries(deliveries):

    valid_deliveries = []
    rejected_deliveries = []

    seen_ids = set()

    for delivery in deliveries:

        errors = []

        if delivery["id"] is None:
            errors.append("Missing ID")

        elif not isinstance(delivery["id"], int):
            errors.append("ID must be a number")

        elif delivery["id"] in seen_ids:
            errors.append("Duplicate delivery ID")


        if not delivery["area"]:
            errors.append("Missing Area")


        if delivery["priority"] is None:
            errors.append("Missing Priority")

        elif not isinstance(delivery["priority"],int):
            errors.append("Priority must be a number")

        elif delivery["priority"] <= 0:
            errors.append("Priority must be greater than 0")


        if delivery["weight"] is None:
            errors.append("Missing Weight")

        elif not isinstance(delivery["weight"],(int, float)):
            errors.append("Weight must be a number")

        elif delivery["weight"] <= 0:
            errors.append("Weight must be greater than 0")

        elif delivery["weight"] > MAX_CAPACITY:
            errors.append("Package exceeds vehicle capacity of 10 kg")

        if errors:
            rejected_deliveries.append((delivery,", ".join(errors)))
            continue


        seen_ids.add(delivery["id"])
        valid_deliveries.append(delivery)

    return valid_deliveries, rejected_deliveries


def create_trips(deliveries):
    """
    Rules:
    1. Lower priority number is handled first.
    2. Deliveries from the same area are grouped when possible.
    3. Total weight of a trip cannot exceed 10 kg.
    """

    if not deliveries:
        return []

    # Priority first, then area, then ID
    sorted_deliveries = sorted(
        deliveries,
        key=lambda delivery: (
            delivery["priority"],
            delivery["area"],
            delivery["id"]
        )
    )

    remaining = sorted_deliveries.copy()
    trips = []

    while remaining:

        first_delivery = remaining.pop(0)

        current_trip = [first_delivery]
        current_weight = first_delivery["weight"]

        # add deliveries from the same area
        i = 0

        while i < len(remaining):

            delivery = remaining[i]

            same_area = (delivery["area"] == first_delivery["area"])

            fits_capacity = (current_weight + delivery["weight"] <= MAX_CAPACITY)

            if same_area and fits_capacity:
                current_trip.append(delivery)
                current_weight += delivery["weight"]
                remaining.pop(i)
            else:
                i += 1

        trips.append(current_trip)

    return trips


def get_trip_weight(trip):
    return sum(delivery["weight"] for delivery in trip)


def get_remaining_capacity(trip):
    return MAX_CAPACITY - get_trip_weight(trip)


def export_trips_to_csv(filename, trips, rejected=None):

    headers = [
        "Trip",
        "Delivery ID",
        "Area",
        "Priority",
        "Package Weight (kg)",
        "Trip Total (kg)",
        "Remaining Capacity (kg)"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Vaild DELIVERIES"])
        writer.writerow(headers)
        

        for trip_number, trip in enumerate(trips, start=1):
            trip_weight = get_trip_weight(trip)
            remaining_capacity = get_remaining_capacity(trip)

            for delivery in trip:
                writer.writerow([
                    trip_number,
                    delivery["id"],
                    delivery["area"],
                    delivery["priority"],
                    f"{delivery['weight']:.1f}",
                    f"{trip_weight:.1f}",
                    f"{remaining_capacity:.1f}"
                ])

        if rejected:
            writer.writerow([])
            writer.writerow(["REJECTED DELIVERIES"])
            writer.writerow(["Delivery ID", "Area", "Priority", "Package Weight (kg)", "Reason"])

            for delivery, reason in rejected:
                delivery_id = delivery["id"] if delivery["id"] is not None else "Missing"
                area = delivery["area"] if delivery["area"] else "Missing"
                priority = delivery["priority"] if delivery["priority"] is not None else "Missing"
                weight = f"{delivery['weight']:.1f}" if isinstance(delivery["weight"], (int, float)) else "Missing"

                writer.writerow([
                    delivery_id,
                    area,
                    priority,
                    weight,
                    reason
                ])