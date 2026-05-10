"""
Synthetic price generator — produces realistic ₦ grocery prices
calibrated to NBS Food Price Watch data (2024–2025).

Use this source for: testing, offline demos, or generating benchmark
prices for states where live scraping returns too few results.
"""
import random
from decimal import Decimal
from .base import BaseScraper

# Base prices (₦) per item — mid-range Nigerian market rates
BASE_PRICES = {
    'Garri':         (700,  1400),
    'Rice':          (900,  1800),
    'Beans':         (750,  1500),
    'Tomatoes':      (450,  1200),
    'Palm Oil':      (1400, 2800),
    'Onions':        (400,   900),
    'Groundnut Oil': (1800, 3500),
    'Yam':           (600,  1400),
    'Plantain':      (600,  1400),
    'Bread':         (900,  1900),
    'Sugar':         (800,  1600),
    'Salt':          (200,   500),
    'Pepper':        (600,  1500),
    'Vegetable Oil': (1500, 2900),
    'Semovita':      (1000, 2100),
}

# Regional multiplier — reflects NBS north-south price differentials
STATE_MULTIPLIERS = {
    'Lagos': 1.28, 'Rivers': 1.22, 'Delta': 1.18, 'Edo': 1.12,
    'Ogun': 1.14, 'Oyo': 1.10, 'Anambra': 1.08, 'Imo': 1.10,
    'Enugu': 1.06, 'Abia': 1.08, 'Cross River': 1.05, 'Akwa Ibom': 1.08,
    'Bayelsa': 1.15, 'FCT': 1.25, 'Kaduna': 0.95, 'Kano': 0.88,
    'Katsina': 0.86, 'Kebbi': 0.82, 'Sokoto': 0.80, 'Jigawa': 0.84,
    'Zamfara': 0.83, 'Yobe': 0.85, 'Borno': 0.87, 'Adamawa': 0.90,
    'Gombe': 0.88, 'Bauchi': 0.86, 'Taraba': 0.90, 'Plateau': 0.95,
    'Nasarawa': 0.98, 'Niger': 0.92, 'Kwara': 1.00, 'Kogi': 0.95,
    'Benue': 0.96, 'Ekiti': 1.02, 'Ondo': 1.05, 'Osun': 1.03,
    'Ebonyi': 1.00, 'Oyo': 1.08,
}

# Sample market names per state
STATE_MARKETS = {
    'Lagos': ['Mile 12 Market', 'Oyingbo Market', 'Oshodi Market', 'Agege Market', 'Balogun Market'],
    'Kano': ['Sabon Gari Market', 'Kantin Kwari Market', 'Kurmi Market', 'Singer Market'],
    'Rivers': ['Mile 1 Diobu Market', 'Rumuola Market', 'Choba Market', 'Oil Mill Market'],
    'FCT': ['Wuse Market', 'Garki Market', 'Nyanya Market', 'Karu Market', 'Utako Market'],
    'Oyo': ['Bodija Market', 'UI Market', 'Gbagi Market', 'Sango Market', 'Ojoo Market'],
    'Anambra': ['Onitsha Main Market', 'Upper Iweka Market', 'Eke-Awka Market', 'Nkwo Nnewi'],
    'Enugu': ['New Market Enugu', 'Ogbete Main Market', 'Coal Camp Market'],
    'Kaduna': ['Kaduna Central Market', 'Kasuwan Barci', 'Barnawa Market'],
    'Katsina': ['Katsina Central Market', 'Kaura Market'],
    'Ogun': ['Kuto Market Abeokuta', 'Sabo Market', 'Lafenwa Market'],
    'Delta': ['Warri Market', 'Asaba Main Market', 'Ogbeogonogo Market'],
    'Borno': ['Maiduguri Monday Market', 'Gamboru Market'],
}


def _default_markets(state: str) -> list[str]:
    return [
        f'{state} Central Market', f'{state} Main Market',
        f'Old {state} Market', f'New {state} Market',
    ]


class SyntheticScraper(BaseScraper):
    source_name = 'synthetic'

    def scrape(self) -> list[dict]:
        state = self.job.state
        multiplier = STATE_MULTIPLIERS.get(state, 1.0)
        markets = STATE_MARKETS.get(state, _default_markets(state))
        results = []

        rng = random.Random(hash(state) % (2**31))

        for item_name, (low, high) in BASE_PRICES.items():
            # Generate 3–6 price observations per item (different stalls/markets)
            n = rng.randint(3, 6)
            for _ in range(n):
                raw = rng.uniform(low * multiplier, high * multiplier)
                # Round to nearest ₦50
                price = Decimal(str(round(raw / 50) * 50))
                store = rng.choice(markets)
                results.append({
                    'item_name': item_name,
                    'raw_item_name': item_name,
                    'store_name': store,
                    'price': price,
                    'city': state,
                    'url': '',
                })

        self.log(f'Generated {len(results)} synthetic price records for {state}')
        return results
