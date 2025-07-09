import os
from dotenv import load_dotenv

load_dotenv()

# ====== API CONFIG =======
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL = "gemini-2.0-flash"
EXCHANGE_RATE_API = "https://open.er-api.com/v6/latest/"

# ====== CURRENCY MAPPING =======
COUNTRY_CURRENCY = {
    "pakistan": "PKR",
    "india": "INR",
    "usa": "USD",
    "united states": "USD",
    "uk": "GBP",
    "united kingdom": "GBP",
    "uae": "AED",
    "canada": "CAD",
    "australia": "AUD",
    "germany": "EUR",
    "france": "EUR",
    "spain": "EUR",
    "italy": "EUR",
    "china": "CNY",
    "japan": "JPY",
    "saudi arabia": "SAR",
    "qatar": "QAR",
    "singapore": "SGD",
    "malaysia": "MYR",
    "thailand": "THB",
    "indonesia": "IDR",
    "vietnam": "VND",
    "philippines": "PHP",
    "south korea": "KRW",
}

MOOD_OPTIONS = [
    {"mood": "Relaxing", "label": "🧘 Relaxing"},
    {"mood": "Adventurous", "label": "⛰️ Adventurous"},
    {"mood": "Cultural", "label": "🏛️ Cultural"},
    {"mood": "Party", "label": "🎉 Party"},
    {"mood": "Romantic", "label": "❤️ Romantic"},
    {"mood": "Family", "label": "👨‍👩‍👧‍👦 Family"},
    {"mood": "Foodie", "label": "🍕 Foodie"},
    {"mood": "Sightseeing", "label": "🏙️ Sightseeing"},
    {"mood": "Historical", "label": "🏺 Historical"},
    {"mood": "Nature", "label": "🌳 Nature"},
    {"mood": "Luxury", "label": "💎 Luxury"},
    {"mood": "Budget", "label": "💰 Budget"},
    {"mood": "Backpacking", "label": "🎒 Backpacking"},
    {"mood": "Business", "label": "💼 Business"},
    {"mood": "Spiritual", "label": "🕉️ Spiritual"},
    {"mood": "Sports", "label": "⚽ Sports"},
    {"mood": "Shopping", "label": "🛍️ Shopping"},
    {"mood": "Custom", "label": "✨ Custom"},
]