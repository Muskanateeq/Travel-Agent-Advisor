import aiohttp
import re
from personalized_agent.config import COUNTRY_CURRENCY, EXCHANGE_RATE_API

async def get_exchange_rate(base_currency: str):
    """Get real-time exchange rates from free API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{EXCHANGE_RATE_API}{base_currency}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("result") == "success":
                    return data["rates"]
    return None

async def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Convert currency using real-time rates"""
    if from_currency == to_currency:
        return amount
    
    rates = await get_exchange_rate(from_currency)
    if rates and to_currency in rates:
        return round(amount * rates[to_currency], 2)
    return None

def get_currency(country_name):
    """Map country name to currency code"""
    country_lower = country_name.strip().lower()
    for country, currency in COUNTRY_CURRENCY.items():
        if country in country_lower:
            return currency
    return "USD"

def parse_budget(budget_str: str):
    """Extract numerical value from budget string"""
    try:
        return float(re.search(r"[\d.,]+", budget_str).group().replace(",", ""))
    except (ValueError, TypeError, AttributeError):
        return None