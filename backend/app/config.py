import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1/")
NEBIUS_MODEL = os.getenv("NEBIUS_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct")

# Vishal's proxy sites — direct fetch, no Tavily needed
PROXY_UNITED_URL = os.getenv("PROXY_UNITED_URL", "http://localhost:3001")
PROXY_AIRBNB_URL = os.getenv("PROXY_AIRBNB_URL", "http://localhost:3002")

# Demo benchmark questions
BENCHMARK_QUESTIONS = {
    "united": [
        "What is the cheapest flight from SFO to NYC tomorrow?",
        "How long is the shortest flight?",
        "Which flights are nonstop?",
        "What is the baggage fee?",
        "How do I book for 2 passengers?",
    ],
    "airbnb": [
        "What is the nightly price?",
        "How many guests does this fit?",
        "What is the cancellation policy?",
        "Is wifi included?",
        "What are the check-in instructions?",
    ],
}

# Demo preset URLs (Vishal's proxy sites)
DEMO_URLS = {
    "united": PROXY_UNITED_URL,
    "airbnb": PROXY_AIRBNB_URL,
}
