"""Booking task definitions for the Playwright agent.

Each task is a structured step the agent attempts on the page.
The agent uses the LLM to map these steps to actual page elements.
"""

MOCK_PASSENGER = {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "phone": "415-555-0142",
    "date_of_birth": "1990-03-15",
}

MOCK_PAYMENT = {
    "card_number": "4111111111111111",
    "card_name": "John Smith",
    "expiry": "12/27",
    "cvv": "123",
    "billing_zip": "94107",
}

MOCK_TRAVEL = {
    "from_airport": "SFO",
    "to_airport": "JFK",
    "departure_date": "2026-03-20",
    "return_date": "2026-03-25",
    "passengers": "1",
}

UNITED_BOOKING_TASKS = [
    {
        "id": "search_flights",
        "name": "Search for flights",
        "description": "Find the flight search form, enter SFO to JFK, select dates, and search",
        "actions": [
            {"type": "fill", "target": "departure/from airport field", "value": MOCK_TRAVEL["from_airport"]},
            {"type": "fill", "target": "arrival/to airport field", "value": MOCK_TRAVEL["to_airport"]},
            {"type": "fill", "target": "departure date field", "value": MOCK_TRAVEL["departure_date"]},
            {"type": "click", "target": "search flights button"},
        ],
        "success_condition": "Flight results are displayed on the page",
    },
    {
        "id": "select_flight",
        "name": "Select a flight",
        "description": "Choose the cheapest available nonstop flight from the search results",
        "actions": [
            {"type": "click", "target": "select button for the cheapest nonstop flight"},
        ],
        "success_condition": "A specific flight is selected and passenger form appears",
    },
    {
        "id": "fill_passenger",
        "name": "Fill passenger information",
        "description": "Enter passenger name, email, phone, and date of birth",
        "actions": [
            {"type": "fill", "target": "first name field", "value": MOCK_PASSENGER["first_name"]},
            {"type": "fill", "target": "last name field", "value": MOCK_PASSENGER["last_name"]},
            {"type": "fill", "target": "email field", "value": MOCK_PASSENGER["email"]},
            {"type": "fill", "target": "phone field", "value": MOCK_PASSENGER["phone"]},
            {"type": "click", "target": "continue/next button"},
        ],
        "success_condition": "Passenger info accepted, payment form appears",
    },
    {
        "id": "fill_payment",
        "name": "Enter payment details",
        "description": "Fill in credit card number, name, expiry, CVV, and billing zip",
        "actions": [
            {"type": "fill", "target": "card number field", "value": MOCK_PAYMENT["card_number"]},
            {"type": "fill", "target": "name on card field", "value": MOCK_PAYMENT["card_name"]},
            {"type": "fill", "target": "expiry date field", "value": MOCK_PAYMENT["expiry"]},
            {"type": "fill", "target": "CVV/security code field", "value": MOCK_PAYMENT["cvv"]},
            {"type": "fill", "target": "billing zip code field", "value": MOCK_PAYMENT["billing_zip"]},
            {"type": "click", "target": "review/continue button"},
        ],
        "success_condition": "Payment accepted, review or confirmation page appears",
    },
    {
        "id": "confirm_booking",
        "name": "Confirm the booking",
        "description": "Review booking details and click the final confirm/book button",
        "actions": [
            {"type": "click", "target": "confirm booking / complete purchase button"},
        ],
        "success_condition": "Booking confirmation page shown with confirmation number",
    },
]

AIRBNB_BOOKING_TASKS = [
    {
        "id": "view_listing",
        "name": "View listing details",
        "description": "Read the listing page to find price, guests, amenities",
        "actions": [
            {"type": "read", "target": "nightly price"},
            {"type": "read", "target": "max guest count"},
            {"type": "read", "target": "cancellation policy"},
        ],
        "success_condition": "Listing details are visible and readable",
    },
    {
        "id": "select_dates",
        "name": "Select check-in and check-out dates",
        "description": "Enter travel dates into the booking form",
        "actions": [
            {"type": "fill", "target": "check-in date field", "value": "2026-03-20"},
            {"type": "fill", "target": "check-out date field", "value": "2026-03-25"},
            {"type": "fill", "target": "number of guests field", "value": "2"},
        ],
        "success_condition": "Dates and guests selected, total price shown",
    },
    {
        "id": "fill_guest_info",
        "name": "Fill guest information",
        "description": "Enter guest name, email, phone for the reservation",
        "actions": [
            {"type": "fill", "target": "first name field", "value": MOCK_PASSENGER["first_name"]},
            {"type": "fill", "target": "last name field", "value": MOCK_PASSENGER["last_name"]},
            {"type": "fill", "target": "email field", "value": MOCK_PASSENGER["email"]},
            {"type": "fill", "target": "phone field", "value": MOCK_PASSENGER["phone"]},
            {"type": "click", "target": "continue/next button"},
        ],
        "success_condition": "Guest info accepted, payment form appears",
    },
    {
        "id": "fill_payment",
        "name": "Enter payment details",
        "description": "Fill in credit card information for the booking",
        "actions": [
            {"type": "fill", "target": "card number field", "value": MOCK_PAYMENT["card_number"]},
            {"type": "fill", "target": "name on card field", "value": MOCK_PAYMENT["card_name"]},
            {"type": "fill", "target": "expiry date field", "value": MOCK_PAYMENT["expiry"]},
            {"type": "fill", "target": "CVV/security code field", "value": MOCK_PAYMENT["cvv"]},
            {"type": "click", "target": "continue/review button"},
        ],
        "success_condition": "Payment accepted, review page appears",
    },
    {
        "id": "confirm_booking",
        "name": "Confirm the reservation",
        "description": "Review and confirm the Airbnb reservation",
        "actions": [
            {"type": "click", "target": "confirm reservation / book now button"},
        ],
        "success_condition": "Reservation confirmed with confirmation details shown",
    },
]

TASK_SETS = {
    "united": UNITED_BOOKING_TASKS,
    "airbnb": AIRBNB_BOOKING_TASKS,
}
