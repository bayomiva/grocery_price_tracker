"""Base scraper class and shared utilities."""
import re
from decimal import Decimal, InvalidOperation

# Maps lowercase keywords → canonical item name (must match GroceryItem.name exactly)
ITEM_KEYWORDS = {
    'Garri': ['garri', 'gari', 'eba'],
    'Rice': ['rice', 'ofada', 'parboil', 'basmati', 'local rice', 'long grain'],
    'Beans': ['beans', 'cowpea', 'black eye', 'black-eye', 'honey beans', 'oloyin'],
    'Tomatoes': ['tomato', 'plum tomato', 'fresh tomato'],
    'Palm Oil': ['palm oil', 'red oil', 'crude palm'],
    'Onions': ['onion', 'red onion', 'white onion', 'bulb onion'],
    'Groundnut Oil': ['groundnut oil', 'peanut oil', 'groundnut'],
    'Yam': ['yam', 'white yam', 'pounded yam', 'tuber'],
    'Plantain': ['plantain', 'unripe plantain', 'ripe plantain'],
    'Bread': ['bread', 'agege bread', 'sliced bread', 'loaf'],
    'Sugar': ['sugar', 'table sugar', 'granulated sugar'],
    'Salt': ['salt', 'iodized salt', 'table salt', 'refined salt'],
    'Pepper': ['pepper', 'chilli', 'tatashe', 'scotch bonnet', 'shombo', 'cayenne'],
    'Vegetable Oil': ['vegetable oil', 'sunflower oil', 'canola oil', 'soya oil'],
    'Semovita': ['semovita', 'semolina', 'semo', 'semovida'],
}


def match_item_name(raw_name: str) -> str | None:
    """Return the canonical item name that best matches the raw scraped name."""
    lowered = raw_name.lower()
    for canonical, keywords in ITEM_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered:
                return canonical
    return None


def parse_price(raw: str) -> Decimal | None:
    """Extract a Decimal price from a string like '₦1,500' or '2500.00'."""
    cleaned = re.sub(r'[₦,\s]', '', raw)
    # take the first number-like group
    m = re.search(r'\d+(?:\.\d+)?', cleaned)
    if not m:
        return None
    try:
        val = Decimal(m.group())
        # Sanity-check: Nigerian grocery prices should be ₦50 – ₦200,000
        if val < 50 or val > 200_000:
            return None
        return val
    except InvalidOperation:
        return None


class BaseScraper:
    source_name: str = 'base'

    def __init__(self, job):
        self.job = job
        self.logs: list[str] = []

    def log(self, msg: str):
        self.logs.append(msg)

    def get_logs(self) -> str:
        return '\n'.join(self.logs)

    def scrape(self) -> list[dict]:
        """Return list of dicts: {item_name, store_name, price, city, url}"""
        raise NotImplementedError
