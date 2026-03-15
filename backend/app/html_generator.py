"""HTML Generator — converts optimized JSON into a functional, agent-navigable booking page.

Generates pages that:
- Look like the original site (similar branding/layout)
- Have working forms with semantic HTML the agent can interact with
- Include data-action and data-entity-type attributes for agent grounding
- Support multi-step booking flows (search → select → passenger → payment → confirm)
"""

import hashlib
import json
from pathlib import Path
from typing import Optional

import openai

from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL

GENERATED_DIR = Path(__file__).parent.parent / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

nebius_client = openai.OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)


def _render_entity_row(key, val):
    if isinstance(val, list):
        val = ", ".join(str(v) for v in val)
    if val is None:
        return ""
    return f'<div class="entity-row" data-entity-type="{key}"><span class="label">{key.replace("_", " ").title()}</span><span class="value">{val}</span></div>'


def _render_entities(entities):
    if isinstance(entities, list):
        parts = []
        for e in entities:
            if isinstance(e, dict):
                k = e.get("type", e.get("entity_type", "info"))
                v = e.get("value", e.get("name", ""))
                parts.append(_render_entity_row(k, v))
            else:
                parts.append(f'<div class="entity-row">{e}</div>')
        return "\n".join(p for p in parts if p)
    elif isinstance(entities, dict):
        return "\n".join(_render_entity_row(k, v) for k, v in entities.items() if v is not None)
    return ""


def _render_facts(facts):
    if not facts:
        return ""
    items = "\n".join(f"<li>{f}</li>" for f in facts)
    return f"<ul>{items}</ul>"


def _render_actions_buttons(actions):
    if not actions:
        return ""
    btns = []
    for a in actions:
        name = a if isinstance(a, str) else a.get("name", a.get("action", "Action"))
        btns.append(f'<button class="action-btn" data-action="{name}">{name.replace("_", " ").title()}</button>')
    return "\n".join(btns)


UNITED_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>United Airlines - AI-Optimized Flight Search</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
.topbar {{ background: #002244; color: white; padding: 0.75rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
.topbar h1 {{ font-size: 1.3rem; }}
.topbar .badge {{ background: #00ff88; color: #002244; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 1.5rem; }}
.step {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }}
.step h2 {{ color: #002244; margin-bottom: 1rem; font-size: 1.2rem; border-bottom: 2px solid #002244; padding-bottom: 0.5rem; }}
.form-row {{ display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }}
.form-group {{ flex: 1; min-width: 200px; }}
.form-group label {{ display: block; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.85rem; color: #555; }}
.form-group input, .form-group select {{ width: 100%; padding: 0.6rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }}
.btn-primary {{ background: #002244; color: white; border: none; padding: 0.75rem 2rem; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; }}
.btn-primary:hover {{ background: #003366; }}
.btn-select {{ background: #0066cc; color: white; border: none; padding: 0.5rem 1.5rem; border-radius: 4px; cursor: pointer; font-weight: 600; }}
.flight-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center; }}
.flight-card:hover {{ border-color: #0066cc; background: #f0f7ff; }}
.flight-info h3 {{ font-size: 1rem; color: #002244; }}
.flight-info p {{ font-size: 0.85rem; color: #666; margin-top: 0.2rem; }}
.flight-price {{ font-size: 1.5rem; font-weight: bold; color: #002244; text-align: right; }}
.flight-price .fee {{ font-size: 0.75rem; color: #888; display: block; }}
.entity-row {{ display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid #eee; }}
.entity-row .label {{ color: #666; font-size: 0.85rem; }}
.entity-row .value {{ font-weight: 600; }}
.summary-box {{ background: #f0f7ff; border: 1px solid #cce0ff; border-radius: 8px; padding: 1rem; margin-top: 1rem; }}
.confirmation {{ text-align: center; padding: 2rem; }}
.confirmation .check {{ font-size: 3rem; color: #00aa44; }}
.confirmation h2 {{ color: #002244; margin: 0.5rem 0; }}
.confirmation .conf-num {{ font-size: 1.5rem; font-weight: bold; color: #002244; background: #f0f0f0; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block; margin-top: 0.5rem; }}
.source-link {{ color: #888; font-size: 0.8rem; text-align: center; margin-top: 1rem; }}
.source-link a {{ color: #0066cc; }}
</style>
</head>
<body>
<div class="topbar">
    <h1>United Airlines</h1>
    <span class="badge">AI-OPTIMIZED</span>
</div>
<div class="container">
    <!-- Step 1: Search -->
    <div class="step" id="step-search" data-step="1">
        <h2>Search Flights</h2>
        <form data-action="search-flights">
            <div class="form-row">
                <div class="form-group">
                    <label for="from">From</label>
                    <input type="text" id="from" name="from" placeholder="SFO" data-entity-type="departure-airport">
                </div>
                <div class="form-group">
                    <label for="to">To</label>
                    <input type="text" id="to" name="to" placeholder="JFK" data-entity-type="arrival-airport">
                </div>
                <div class="form-group">
                    <label for="date">Departure Date</label>
                    <input type="date" id="date" name="date" data-entity-type="departure-date">
                </div>
                <div class="form-group">
                    <label for="passengers">Passengers</label>
                    <select id="passengers" name="passengers" data-entity-type="passenger-count">
                        <option value="1">1 Passenger</option>
                        <option value="2">2 Passengers</option>
                        <option value="3">3 Passengers</option>
                    </select>
                </div>
            </div>
            <button type="button" class="btn-primary" data-action="search-flights" onclick="document.getElementById('step-results').style.display='block'">Search Flights</button>
        </form>
    </div>

    <!-- Step 2: Results -->
    <div class="step" id="step-results" data-step="2">
        <h2>Available Flights — SFO to JFK</h2>
        {flight_cards}
    </div>

    <!-- Step 3: Passenger Info -->
    <div class="step" id="step-passenger" data-step="3">
        <h2>Passenger Information</h2>
        <form data-action="fill-passenger">
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" placeholder="John" data-entity-type="passenger-name">
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" placeholder="Smith" data-entity-type="passenger-name">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" placeholder="john@example.com" data-entity-type="email">
                </div>
                <div class="form-group">
                    <label for="phone">Phone</label>
                    <input type="tel" id="phone" name="phone" placeholder="415-555-0142" data-entity-type="phone">
                </div>
            </div>
            <button type="button" class="btn-primary" data-action="continue-to-payment" onclick="document.getElementById('step-payment').style.display='block'">Continue to Payment</button>
        </form>
    </div>

    <!-- Step 4: Payment -->
    <div class="step" id="step-payment" data-step="4">
        <h2>Payment Details</h2>
        <form data-action="fill-payment">
            <div class="form-row">
                <div class="form-group">
                    <label for="card_number">Card Number</label>
                    <input type="text" id="card_number" name="card_number" placeholder="4111 1111 1111 1111" data-entity-type="card-number">
                </div>
                <div class="form-group">
                    <label for="card_name">Name on Card</label>
                    <input type="text" id="card_name" name="card_name" placeholder="John Smith" data-entity-type="card-name">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="expiry">Expiry</label>
                    <input type="text" id="expiry" name="expiry" placeholder="12/27" data-entity-type="card-expiry">
                </div>
                <div class="form-group">
                    <label for="cvv">CVV</label>
                    <input type="text" id="cvv" name="cvv" placeholder="123" data-entity-type="card-cvv">
                </div>
                <div class="form-group">
                    <label for="zip">Billing ZIP</label>
                    <input type="text" id="zip" name="zip" placeholder="94107" data-entity-type="billing-zip">
                </div>
            </div>
            <button type="button" class="btn-primary" data-action="review-booking" onclick="document.getElementById('step-confirm').style.display='block'">Review Booking</button>
        </form>
    </div>

    <!-- Step 5: Confirmation -->
    <div class="step" id="step-confirm" data-step="5">
        <h2>Review & Confirm</h2>
        <div class="summary-box">
            <div class="entity-row"><span class="label">Route</span><span class="value">SFO → JFK</span></div>
            <div class="entity-row"><span class="label">Flight</span><span class="value">UA101 — Nonstop</span></div>
            <div class="entity-row" data-entity-type="price"><span class="label">Price</span><span class="value">$189</span></div>
            <div class="entity-row"><span class="label">Duration</span><span class="value">5h 25m</span></div>
            <div class="entity-row" data-entity-type="baggage-fee"><span class="label">Baggage</span><span class="value">$35/checked bag</span></div>
        </div>
        <div style="margin-top: 1rem; text-align: center;">
            <button class="btn-primary" data-action="confirm-booking" style="background: #00aa44; padding: 1rem 3rem; font-size: 1.1rem;" onclick="document.getElementById('step-done').style.display='block'; this.parentElement.parentElement.style.display='none'">
                Confirm Booking
            </button>
        </div>
    </div>

    <!-- Step 6: Done -->
    <div class="step" id="step-done" data-step="6" style="display:none">
        <div class="confirmation">
            <div class="check">&#10003;</div>
            <h2>Booking Confirmed!</h2>
            <p>Your flight has been booked successfully.</p>
            <div class="conf-num">UA-2026-DEMO-4829</div>
            <div style="margin-top: 1rem;">
                <div class="entity-row"><span class="label">Route</span><span class="value">SFO → JFK</span></div>
                <div class="entity-row"><span class="label">Flight</span><span class="value">UA101 — Nonstop</span></div>
                <div class="entity-row"><span class="label">Date</span><span class="value">March 20, 2026</span></div>
                <div class="entity-row"><span class="label">Passenger</span><span class="value">John Smith</span></div>
            </div>
        </div>
    </div>

    <div class="source-link">
        Optimized from <a href="{source_url}" target="_blank">{source_url}</a> by injester.lol
    </div>
</div>
</body>
</html>"""


AIRBNB_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Airbnb - AI-Optimized Listing</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: Circular, -apple-system, BlinkMacSystemFont, Roboto, sans-serif; background: #fff; color: #222; }}
.topbar {{ background: #ff385c; color: white; padding: 0.75rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
.topbar h1 {{ font-size: 1.3rem; }}
.topbar .badge {{ background: #00ff88; color: #222; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 1.5rem; }}
.listing-header h2 {{ font-size: 1.6rem; color: #222; margin-bottom: 0.5rem; }}
.listing-header .rating {{ color: #ff385c; font-weight: 600; }}
.photo-placeholder {{ background: #f0f0f0; height: 300px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 1.2rem; margin: 1rem 0; }}
.section {{ margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #ddd; }}
.section h3 {{ font-size: 1.1rem; margin-bottom: 0.75rem; }}
.entity-row {{ display: flex; justify-content: space-between; padding: 0.5rem 0; }}
.entity-row .label {{ color: #717171; }}
.entity-row .value {{ font-weight: 600; }}
.amenity-list {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
.amenity {{ background: #f7f7f7; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; }}
.booking-card {{ background: #fff; border: 1px solid #ddd; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 16px rgba(0,0,0,0.12); position: sticky; top: 1rem; }}
.booking-card .price {{ font-size: 1.5rem; font-weight: 700; }}
.booking-card .price span {{ font-size: 0.9rem; font-weight: 400; color: #717171; }}
.form-group {{ margin-bottom: 1rem; }}
.form-group label {{ display: block; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.85rem; color: #555; }}
.form-group input, .form-group select {{ width: 100%; padding: 0.6rem; border: 1px solid #ccc; border-radius: 8px; font-size: 1rem; }}
.btn-reserve {{ background: linear-gradient(to right, #e61e4d, #d70466); color: white; border: none; padding: 0.85rem; width: 100%; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }}
.btn-reserve:hover {{ opacity: 0.9; }}
.btn-primary {{ background: #222; color: white; border: none; padding: 0.75rem 2rem; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }}
.layout {{ display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; }}
.step {{ background: #fafafa; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }}
.step h3 {{ margin-bottom: 1rem; }}
.form-row {{ display: flex; gap: 1rem; margin-bottom: 1rem; }}
.form-row .form-group {{ flex: 1; }}
.confirmation {{ text-align: center; padding: 2rem; }}
.confirmation .check {{ font-size: 3rem; color: #00aa44; }}
.conf-num {{ font-size: 1.3rem; font-weight: bold; background: #f0f0f0; padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; margin-top: 0.5rem; }}
.source-link {{ color: #999; font-size: 0.8rem; text-align: center; margin-top: 2rem; }}
.source-link a {{ color: #ff385c; }}
</style>
</head>
<body>
<div class="topbar">
    <h1>airbnb</h1>
    <span class="badge">AI-OPTIMIZED</span>
</div>
<div class="container">
    <div class="listing-header">
        <h2>{listing_title}</h2>
        <span class="rating">{rating}</span>
    </div>
    <div class="photo-placeholder">Listing Photos</div>

    <div class="layout">
        <div>
            <!-- Listing Details -->
            <div class="section">
                <h3>Listing Details</h3>
                {entities_html}
            </div>
            <div class="section">
                <h3>Key Facts</h3>
                {facts_html}
            </div>
            <div class="section">
                <h3>Description</h3>
                <p>{summary}</p>
            </div>
        </div>

        <div>
            <!-- Booking Card -->
            <div class="booking-card">
                <div class="price" data-entity-type="price">{price} <span>/ night</span></div>
                <form data-action="reserve">
                    <div class="form-group">
                        <label for="checkin">Check-in</label>
                        <input type="date" id="checkin" name="checkin" data-entity-type="checkin-date">
                    </div>
                    <div class="form-group">
                        <label for="checkout">Check-out</label>
                        <input type="date" id="checkout" name="checkout" data-entity-type="checkout-date">
                    </div>
                    <div class="form-group">
                        <label for="guests">Guests</label>
                        <select id="guests" name="guests" data-entity-type="guest-count">
                            <option value="1">1 guest</option>
                            <option value="2">2 guests</option>
                            <option value="3">3 guests</option>
                            <option value="4">4 guests</option>
                        </select>
                    </div>
                    <button type="button" class="btn-reserve" data-action="reserve" onclick="document.getElementById('step-guest').style.display='block'">Reserve</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Guest Info Step -->
    <div class="step" id="step-guest" style="display:none" data-step="3">
        <h3>Guest Information</h3>
        <form data-action="fill-guest-info">
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" placeholder="John">
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" placeholder="Smith">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" placeholder="john@example.com">
                </div>
                <div class="form-group">
                    <label for="phone">Phone</label>
                    <input type="tel" id="phone" name="phone" placeholder="415-555-0142">
                </div>
            </div>
            <button type="button" class="btn-primary" data-action="continue-to-payment" onclick="document.getElementById('step-payment').style.display='block'">Continue to Payment</button>
        </form>
    </div>

    <!-- Payment Step -->
    <div class="step" id="step-payment" style="display:none" data-step="4">
        <h3>Payment</h3>
        <form data-action="fill-payment">
            <div class="form-row">
                <div class="form-group">
                    <label for="card_number">Card Number</label>
                    <input type="text" id="card_number" name="card_number" placeholder="4111 1111 1111 1111">
                </div>
                <div class="form-group">
                    <label for="card_name">Name on Card</label>
                    <input type="text" id="card_name" name="card_name" placeholder="John Smith">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="expiry">Expiry</label>
                    <input type="text" id="expiry" name="expiry" placeholder="12/27">
                </div>
                <div class="form-group">
                    <label for="cvv">CVV</label>
                    <input type="text" id="cvv" name="cvv" placeholder="123">
                </div>
            </div>
            <button type="button" class="btn-primary" data-action="confirm-reservation" onclick="document.getElementById('step-done').style.display='block'; this.parentElement.parentElement.style.display='none'">Confirm Reservation</button>
        </form>
    </div>

    <!-- Confirmation -->
    <div class="step" id="step-done" style="display:none" data-step="5">
        <div class="confirmation">
            <div class="check">&#10003;</div>
            <h2>Reservation Confirmed!</h2>
            <p>Your stay has been booked successfully.</p>
            <div class="conf-num">ABB-2026-DEMO-7291</div>
        </div>
    </div>

    <div class="source-link">
        Optimized from <a href="{source_url}" target="_blank">{source_url}</a> by injester.lol
    </div>
</div>
</body>
</html>"""


GENERIC_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI-Optimized: {title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #e0e0e0; padding: 2rem; }}
.header {{ border-bottom: 2px solid #00ff88; padding-bottom: 1rem; margin-bottom: 2rem; }}
.header h1 {{ color: #00ff88; font-size: 1.5rem; }}
.header .badge {{ display: inline-block; background: #00ff88; color: #0a0a0a; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-top: 0.5rem; }}
.header .source {{ color: #888; font-size: 0.85rem; margin-top: 0.5rem; }}
.section {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
.section h2 {{ color: #00ff88; font-size: 1.1rem; margin-bottom: 1rem; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }}
.intent {{ font-size: 1.2rem; color: #00ccff; font-weight: bold; }}
.entity-row {{ display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #222; }}
.entity-row .label {{ color: #888; text-transform: uppercase; font-size: 0.8rem; }}
.entity-row .value {{ color: #fff; font-weight: 600; text-align: right; max-width: 60%; }}
.action-btn {{ background: #00ff88; color: #0a0a0a; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: bold; cursor: pointer; margin: 0.3rem; font-size: 0.9rem; }}
ul {{ list-style: none; }}
ul li {{ padding: 0.4rem 0; border-left: 3px solid #00ff88; padding-left: 0.8rem; margin-bottom: 0.3rem; }}
.summary {{ font-size: 1rem; line-height: 1.6; color: #ccc; }}
.noise-badge {{ background: #ff4444; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
pre {{ background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; color: #00ff88; }}
</style>
</head>
<body>
<div class="header">
    <h1>AI-Optimized View</h1>
    <span class="badge">AGENT-READY</span>
    <span class="noise-badge">{noise_pct}% noise removed</span>
    <div class="source">Source: <a href="{source_url}" style="color:#00ccff">{source_url}</a></div>
</div>
<div class="section"><h2>Page Intent</h2><div class="intent">{intent}</div></div>
<div class="section"><h2>Extracted Entities</h2>{entities_html}</div>
<div class="section"><h2>Agent Actions</h2>{actions_html}</div>
<div class="section"><h2>Key Facts</h2>{facts_html}</div>
<div class="section"><h2>Agent Summary</h2><div class="summary">{summary}</div></div>
<div class="section"><h2>Structured Data</h2><pre>{json_data}</pre></div>
</body>
</html>"""


def _build_flight_cards(data):
    """Build United-style flight result cards from optimized data."""
    flights = [
        {"id": "UA101", "name": "United UA101 — Nonstop", "price": "$189", "duration": "5h 25m",
         "depart": "8:00 AM SFO", "arrive": "4:25 PM JFK", "baggage": "$35/checked bag"},
        {"id": "UA205", "name": "United UA205 — Nonstop", "price": "$219", "duration": "5h 30m",
         "depart": "12:30 PM SFO", "arrive": "9:00 PM JFK", "baggage": "$35/checked bag"},
        {"id": "UA318", "name": "United UA318 — 1 Stop (ORD)", "price": "$149", "duration": "8h 10m",
         "depart": "6:15 AM SFO", "arrive": "5:25 PM EWR", "baggage": "$35/checked bag"},
    ]

    # Try to pull real data from optimization
    entities = data.get("primary_entities", {})
    if isinstance(entities, list):
        for i, e in enumerate(entities):
            if i < len(flights) and isinstance(e, dict):
                if e.get("value"):
                    flights[i]["name"] = str(e.get("value", flights[i]["name"]))

    cards = []
    for f in flights:
        cards.append(f"""
        <div class="flight-card" data-entity-type="flight" data-flight-id="{f['id']}">
            <div class="flight-info">
                <h3>{f['name']}</h3>
                <p data-entity-type="duration">{f['duration']} | {f['depart']} → {f['arrive']}</p>
                <p data-entity-type="baggage-fee">Baggage: {f['baggage']}</p>
            </div>
            <div>
                <div class="flight-price" data-entity-type="price">{f['price']}</div>
                <button class="btn-select" data-action="select-flight" data-flight-id="{f['id']}"
                    onclick="document.getElementById('step-passenger').style.display='block'">Select</button>
            </div>
        </div>""")
    return "\n".join(cards)


def generate_optimized_html(
    optimized_json: dict,
    url: str,
    page_type: str = "flight_booking",
) -> dict:
    """Generate a browsable AI-optimized HTML page from structured JSON."""

    data = optimized_json
    intent = data.get("page_intent", "Unknown")
    entities = data.get("primary_entities", data.get("entities", {}))
    actions = data.get("agent_actions", data.get("actions", []))
    facts = data.get("key_facts", data.get("facts", []))
    summary = data.get("agent_summary", data.get("summary", ""))
    noise_pct = data.get("noise_removed_pct", data.get("noise_removed", "N/A"))

    if "united" in page_type.lower():
        html_content = UNITED_TEMPLATE.format(
            flight_cards=_build_flight_cards(data),
            source_url=url,
        )
    elif "airbnb" in page_type.lower():
        # Extract listing-specific fields
        listing_title = "Cozy Apartment in San Francisco"
        price = "$150"
        rating = "4.8 (127 reviews)"
        if isinstance(entities, dict):
            listing_title = str(entities.get("listing_title", entities.get("hotel_name", listing_title)))
            price = str(entities.get("nightly_price", entities.get("price", price)))
            rating_val = entities.get("rating", "4.8")
            review_count = entities.get("review_count", "127")
            rating = f"{rating_val} ({review_count} reviews)"

        html_content = AIRBNB_TEMPLATE.format(
            listing_title=listing_title,
            price=price,
            rating=rating,
            entities_html=_render_entities(entities),
            facts_html=_render_facts(facts),
            summary=summary,
            source_url=url,
        )
    else:
        html_content = GENERIC_TEMPLATE.format(
            title=intent,
            source_url=url,
            intent=intent,
            entities_html=_render_entities(entities),
            actions_html=_render_actions_buttons(actions),
            facts_html=_render_facts(facts),
            summary=summary,
            noise_pct=noise_pct,
            json_data=json.dumps(data, indent=2),
        )

    # Generate deterministic filename from URL
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    filename = f"{page_type}_{url_hash}.html"
    filepath = GENERATED_DIR / filename
    filepath.write_text(html_content)

    return {
        "filename": filename,
        "filepath": str(filepath),
        "served_url": f"/generated/{filename}",
        "html_length": len(html_content),
    }


def generate_united_optimized(optimized_json: dict, url: str) -> dict:
    return generate_optimized_html(optimized_json, url, page_type="united_booking")


def generate_airbnb_optimized(optimized_json: dict, url: str) -> dict:
    return generate_optimized_html(optimized_json, url, page_type="airbnb_listing")
