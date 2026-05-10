"""Jumia Nigeria grocery scraper."""
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, match_item_name, parse_price

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

GROCERY_URLS = [
    'https://www.jumia.com.ng/groceries/',
    'https://www.jumia.com.ng/staple-food/',
    'https://www.jumia.com.ng/cooking-ingredients/',
]


class JumiaScraper(BaseScraper):
    source_name = 'jumia'

    def scrape(self) -> list[dict]:
        state = self.job.state
        results = []

        for url in GROCERY_URLS:
            self.log(f'Fetching: {url}')
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
            except Exception as exc:
                self.log(f'Request failed: {exc}')
                continue

            soup = BeautifulSoup(resp.text, 'lxml')
            items = self._parse_page(soup, state, url)
            self.log(f'Parsed {len(items)} items from {url}')
            results.extend(items)

        self.log(f'Total scraped: {len(results)}')
        return results

    def _parse_page(self, soup: BeautifulSoup, state: str, page_url: str) -> list[dict]:
        results = []
        # Jumia product cards
        cards = (
            soup.select('article.prd') or
            soup.select('[data-id]') or
            soup.select('.c-prd') or
            soup.select('article[class*="prd"]')
        )

        for card in cards:
            name_el = (
                card.select_one('.name') or
                card.select_one('h3.name') or
                card.select_one('[class*="name"]') or
                card.select_one('h3')
            )
            price_el = (
                card.select_one('.prc') or
                card.select_one('[class*="prc"]') or
                card.select_one('[class*="price"]')
            )

            if not name_el or not price_el:
                continue

            raw_name = name_el.get_text(strip=True)
            matched = match_item_name(raw_name)
            if not matched:
                continue

            price = parse_price(price_el.get_text(strip=True))
            if not price:
                continue

            link_el = card.select_one('a[href]')
            source_url = ''
            if link_el:
                href = link_el.get('href', '')
                source_url = href if href.startswith('http') else f'https://www.jumia.com.ng{href}'

            results.append({
                'item_name': matched,
                'raw_item_name': raw_name,
                'store_name': f'Jumia Nigeria ({state})',
                'price': price,
                'city': '',
                'url': source_url,
            })

        return results
