"""Background thread runner for scraping jobs."""
import threading
from django.utils import timezone


def _build_item_matcher(items):
    """
    Return a callable that maps a canonical name like 'Garri' → GroceryItem
    even when the DB stores 'Garri (1kg)'.

    Strategy (in order of priority):
      1. Exact match (case-insensitive)
      2. DB item name starts with canonical name (e.g. "Garri (1kg)" starts with "Garri")
      3. Canonical name is contained anywhere in DB item name
    """
    exact = {i.name.lower(): i for i in items}
    # prefix_map: 'garri' → GroceryItem(name='Garri (1kg)')
    prefix_map = {}
    for i in items:
        prefix = i.name.split('(')[0].strip().lower()
        prefix_map.setdefault(prefix, i)

    def match(canonical: str):
        lo = canonical.lower()
        if lo in exact:
            return exact[lo]
        if lo in prefix_map:
            return prefix_map[lo]
        # fallback: canonical appears inside any DB item name
        for db_name, item in exact.items():
            if lo in db_name:
                return item
        return None

    return match


def _do_run(job_id: int):
    from django.db import connection
    connection.close()  # ensure fresh connection in this thread

    from scraper.models import ScrapingJob, ScrapedPrice
    from items.models import GroceryItem
    from stores.models import Store

    try:
        job = ScrapingJob.objects.get(id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at'])

        # Choose scraper
        if job.source == 'jiji':
            from scraper.scrapers.jiji import JijiScraper as Cls
        elif job.source == 'jumia':
            from scraper.scrapers.jumia import JumiaScraper as Cls
        else:
            from scraper.scrapers.synthetic import SyntheticScraper as Cls

        scraper = Cls(job)
        raw_results = scraper.scrape()

        # Build flexible item matcher
        all_items = list(GroceryItem.objects.all())
        match_item = _build_item_matcher(all_items)

        # Pre-load stores for matching (same state)
        stores_qs = Store.objects.filter(state__iexact=job.state)
        stores_map = {s.name.lower(): s for s in stores_qs}

        created = []
        for r in raw_results:
            matched_item = match_item(r['item_name'])
            store_name_lower = r['store_name'].lower()
            matched_store = stores_map.get(store_name_lower)

            created.append(ScrapedPrice(
                job=job,
                raw_item_name=r.get('raw_item_name', r['item_name']),
                raw_store_name=r['store_name'],
                raw_price=r['price'],
                raw_city=r.get('city', ''),
                source_url=r.get('url', ''),
                matched_item=matched_item,
                matched_store=matched_store,
            ))

        ScrapedPrice.objects.bulk_create(created, batch_size=200)

        job.items_found = len(created)
        job.status = 'done'
        job.completed_at = timezone.now()
        job.log_text = scraper.get_logs()
        job.save(update_fields=['items_found', 'status', 'completed_at', 'log_text'])

    except Exception as exc:
        try:
            from scraper.models import ScrapingJob
            ScrapingJob.objects.filter(id=job_id).update(
                status='failed',
                completed_at=timezone.now(),
                log_text=str(exc),
            )
        except Exception:
            pass


def start_job(job_id: int):
    """Spawn background daemon thread for job."""
    t = threading.Thread(target=_do_run, args=(job_id,), daemon=True)
    t.start()
