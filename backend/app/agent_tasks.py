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


def get_united_tasks(trip=None):
    """Generate United booking tasks with dynamic trip details."""
    t = trip or {}
    from_airport = t.get("from_airport", "SFO")
    to_airport = t.get("to_airport", "JFK")
    departure_date = t.get("departure_date", "2026-03-20")
    return_date = t.get("return_date", "2026-03-25")
    passengers = t.get("passengers", "1")

    return [
        {
            "id": "search_flights",
            "name": "Search for flights",
            "description": f"Find the flight search form, enter {from_airport} to {to_airport}, select {departure_date}, and search",
            "actions": [
                {"type": "fill", "target": "departure/from airport field", "value": from_airport},
                {"type": "fill", "target": "arrival/to airport field", "value": to_airport},
                {"type": "fill", "target": "departure date field", "value": departure_date},
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


def get_airbnb_tasks(trip=None):
    """Generate Airbnb listing booking tasks with dynamic trip details.

    Matches the real Airbnb listing page flow:
    1. Read listing info (price, capacity, amenities)
    2. Open the check-in date picker and select dates
    3. Set guest count
    4. Review pricing breakdown
    5. Click Reserve / Message Host
    """
    t = trip or {}
    check_in = t.get("check_in", "2026-03-20")
    check_out = t.get("check_out", "2026-03-25")
    guests = t.get("guests", "2")

    return [
        {
            "id": "read_listing",
            "name": "Read listing details",
            "description": "Read the listing page to find the nightly price, maximum guest capacity, key amenities, and house rules",
            "actions": [
                {"type": "read", "target": "nightly price"},
                {"type": "read", "target": "maximum guest count"},
                {"type": "read", "target": "key amenities list"},
                {"type": "read", "target": "house rules or cancellation policy"},
            ],
            "success_condition": "Listing price, guest capacity, and amenities are visible and readable",
        },
        {
            "id": "select_checkin",
            "name": "Select check-in date",
            "description": f"Click on the check-in date field in the booking card on the right side, then select {check_in} from the calendar",
            "actions": [
                {"type": "click", "target": "CHECK-IN date field or 'Add date' button in the booking card"},
                {"type": "click", "target": f"calendar day matching {check_in}"},
            ],
            "success_condition": "Check-in date is selected and shown in the booking card",
        },
        {
            "id": "select_checkout",
            "name": "Select check-out date",
            "description": f"Select check-out date {check_out} from the calendar that appeared after selecting check-in",
            "actions": [
                {"type": "click", "target": f"calendar day matching {check_out}"},
            ],
            "success_condition": "Check-out date is selected, both dates shown in booking card, and total price is now visible",
        },
        {
            "id": "set_guests",
            "name": "Set number of guests",
            "description": f"Open the guests dropdown and set to {guests} guests",
            "actions": [
                {"type": "click", "target": "GUESTS dropdown or '1 guest' button in the booking card"},
                {"type": "click", "target": f"increase adults/guests button until count reaches {guests}"},
            ],
            "success_condition": f"Guest count shows {guests} guests in the booking card",
        },
        {
            "id": "reserve",
            "name": "Click Reserve",
            "description": "Click the Reserve button to proceed with the booking (or 'Message Host' if Reserve is not available)",
            "actions": [
                {"type": "click", "target": "Reserve button or Request to Book button"},
            ],
            "success_condition": "Navigated to the booking/checkout page or message host form",
        },
    ]


def get_tasks(site_type, trip_details=None):
    """Get task set for a site type with optional dynamic trip details."""
    if site_type == "united":
        return get_united_tasks(trip_details)
    if site_type == "airbnb":
        return get_airbnb_tasks(trip_details)
    return None


# Legacy static lookup (kept for backward compat)
TASK_SETS = {
    "united": get_united_tasks(),
    "airbnb": get_airbnb_tasks(),
}
