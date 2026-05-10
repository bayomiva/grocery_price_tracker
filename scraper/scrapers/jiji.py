"""Jiji.ng food classifieds scraper — scrapes by Nigerian state."""
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, match_item_name, parse_price

# Jiji.ng URL slug for each Nigerian state
JIJI_SLUGS = {
    'Abia': 'abia', 'Adamawa': 'adamawa', 'Akwa Ibom': 'akwa-ibom',
    'Anambra': 'anambra', 'Bauchi': 'bauchi', 'Bayelsa': 'bayelsa',
    'Benue': 'benue', 'Borno': 'borno', 'Cross River': 'cross-river',
    'Delta': 'delta', 'Ebonyi': 'ebonyi', 'Edo': 'edo',
    'Ekiti': 'ekiti', 'Enugu': 'enugu', 'FCT': 'abuja',
    'Gombe': 'gombe', 'Imo': 'imo', 'Jigawa': 'jigawa',
    'Kaduna': 'kaduna', 'Kano': 'kano', 'Katsina': 'katsina',
    'Kebbi': 'kebbi', 'Kogi': 'kogi', 'Kwara': 'kwara',
    'Lagos': 'lagos', 'Nasarawa': 'nasarawa', 'Niger': 'niger-state',
    'Ogun': 'ogun', 'Ondo': 'ondo', 'Osun': 'osun',
    'Oyo': 'oyo', 'Plateau': 'plateau', 'Rivers': 'rivers-state',
    'Sokoto': 'sokoto', 'Taraba': 'taraba', 'Yobe': 'yobe',
    'Zamfara': 'zamfara',
}

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

MAX_PAGES = 3


class JijiScraper(BaseScraper):
    source_name = 'jiji'

    def scrape(self) -> list[dict]:
        state = self.job.state
        slug = JIJI_SLUGS.get(state)
        if not slug:
            self.log(f'No Jiji slug found for state: {state}')
            return []

        results = []
        for page in range(1, MAX_PAGES + 1):
            url = f'https://jiji.ng/{slug}/food-agriculture-items?page={page}'
            self.log(f'Fetching page {page}: {url}')
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
            except Exception as exc:
                self.log(f'Request failed (page {page}): {exc}')
                break

            soup = BeautifulSoup(resp.text, 'lxml')
            items = self._parse_page(soup, state, url)
            self.log(f'Page {page}: parsed {len(items)} items')
            results.extend(items)
            if len(items) < 10:
                break  # last page

        self.log(f'Total scraped: {len(results)}')
        return results

    def _parse_page(self, soup: BeautifulSoup, state: str, page_url: str) -> list[dict]:
        results = []
        # Try multiple selector strategies (Jiji sometimes changes their markup)
        cards = (
            soup.select('article.b-list-advert__item-wrapper') or
            soup.select('div.b-list-advert__item-wrapper') or
            soup.select('[data-cy="advert-list-item"]') or
            soup.select('.qa-advert-list-item') or
            soup.select('li.b-list-advert-item-wrapper')
        )

        for card in cards:
            title_el = (
                card.select_one('[data-cy="advert-title"]') or
                card.select_one('.qa-advert-title') or
                card.select_one('.b-advert-title-inner span') or
                card.select_one('h3') or
                card.select_one('h2')
            )
            price_el = (
                card.select_one('[data-cy="price"]') or
                card.select_one('.qa-advert-price') or
                card.select_one('.b-advert-price') or
                card.select_one('[class*="price"]')
            )
            location_el = (
                card.select_one('[data-cy="location"]') or
                card.select_one('.b-list-advert__item-location') or
                card.select_one('.qa-advert-location')
            )

            if not title_el or not price_el:
                continue

            raw_name = title_el.get_text(strip=True)
            matched = match_item_name(raw_name)
            if not matched:
                continue  # skip non-grocery items

            price = parse_price(price_el.get_text(strip=True))
            if not price:
                continue

            city = ''
            if location_el:
                city = location_el.get_text(strip=True).split(',')[0].strip()

            link_el = card.select_one('a[href]')
            source_url = ''
            if link_el:
                href = link_el['href']
                source_url = href if href.startswith('http') else f'https://jiji.ng{href}'

            results.append({
                'item_name': matched,
                'raw_item_name': raw_name,
                'store_name': f'Jiji Seller — {city or state}',
                'price': price,
                'city': city,
                'url': source_url,
            })

        return results
