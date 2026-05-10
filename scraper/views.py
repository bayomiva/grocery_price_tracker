from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from items.models import GroceryItem
from stores.models import Store
from prices.models import Price
from .models import ScrapingJob, ScrapedPrice, NIGERIAN_STATES, SCRAPER_SOURCES
from .serializers import ScrapingJobSerializer, ScrapingJobListSerializer
from .scrapers.runner import start_job

# Approximate lat/lng for state capitals (used when creating new stores)
STATE_COORDS = {
    'Abia': (5.4527, 7.5248), 'Adamawa': (9.3265, 12.3984),
    'Akwa Ibom': (5.0077, 7.8537), 'Anambra': (6.2104, 6.9876),
    'Bauchi': (10.3158, 9.8442), 'Bayelsa': (4.7719, 6.0699),
    'Benue': (7.7337, 8.5374), 'Borno': (11.8333, 13.1500),
    'Cross River': (4.9517, 8.3220), 'Delta': (5.8904, 5.6801),
    'Ebonyi': (6.2649, 8.0137), 'Edo': (6.3350, 5.6037),
    'Ekiti': (7.6190, 5.2210), 'Enugu': (6.4584, 7.5464),
    'FCT': (9.0579, 7.4951), 'Gombe': (10.2791, 11.1670),
    'Imo': (5.4922, 7.0251), 'Jigawa': (12.2280, 9.5616),
    'Kaduna': (10.5264, 7.4382), 'Kano': (12.0022, 8.5920),
    'Katsina': (12.9886, 7.6006), 'Kebbi': (12.4539, 4.1975),
    'Kogi': (7.7337, 6.6906), 'Kwara': (8.4966, 4.5421),
    'Lagos': (6.5244, 3.3792), 'Nasarawa': (8.5380, 8.3212),
    'Niger': (9.0579, 6.5571), 'Ogun': (7.1600, 3.3491),
    'Ondo': (7.2500, 5.1950), 'Osun': (7.5629, 4.5200),
    'Oyo': (7.3775, 3.9470), 'Plateau': (9.2182, 9.5179),
    'Rivers': (4.8156, 7.0498), 'Sokoto': (13.0059, 5.2476),
    'Taraba': (7.9693, 11.3706), 'Yobe': (12.2939, 11.7465),
    'Zamfara': (12.1702, 6.6614),
}


class ScraperMetaView(APIView):
    """GET /api/scraper/ — returns available states and sources."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            'states': [{'value': v, 'label': l} for v, l in NIGERIAN_STATES],
            'sources': [{'value': v, 'label': l} for v, l in SCRAPER_SOURCES],
        })


class ScrapingJobListCreateView(APIView):
    """
    GET  /api/scraper/jobs/  — recent jobs (newest first, max 50)
    POST /api/scraper/jobs/  — create + start a new job
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        jobs = ScrapingJob.objects.select_related('created_by')[:50]
        return Response(ScrapingJobListSerializer(jobs, many=True).data)

    def post(self, request):
        state = request.data.get('state', '').strip()
        source = request.data.get('source', 'jiji').strip()

        valid_states = [s[0] for s in NIGERIAN_STATES]
        valid_sources = [s[0] for s in SCRAPER_SOURCES]

        if state not in valid_states:
            return Response({'detail': f'Invalid state: {state}'}, status=400)
        if source not in valid_sources:
            return Response({'detail': f'Invalid source: {source}'}, status=400)

        job = ScrapingJob.objects.create(
            state=state,
            source=source,
            status='pending',
            created_by=request.user,
        )
        start_job(job.id)
        return Response(ScrapingJobListSerializer(job).data, status=201)


class ScrapingJobDetailView(APIView):
    """
    GET    /api/scraper/jobs/<id>/  — job detail + all scraped results
    DELETE /api/scraper/jobs/<id>/  — delete job + results
    """
    permission_classes = [IsAdminUser]

    def _get_job(self, pk):
        try:
            return ScrapingJob.objects.prefetch_related('results__matched_item', 'results__matched_store').get(pk=pk)
        except ScrapingJob.DoesNotExist:
            return None

    def get(self, request, pk):
        job = self._get_job(pk)
        if not job:
            return Response({'detail': 'Not found.'}, status=404)
        return Response(ScrapingJobSerializer(job).data)

    def delete(self, request, pk):
        job = self._get_job(pk)
        if not job:
            return Response({'detail': 'Not found.'}, status=404)
        if job.status == 'running':
            return Response({'detail': 'Cannot delete a running job.'}, status=400)
        job.delete()
        return Response(status=204)


class ImportResultsView(APIView):
    """POST /api/scraper/jobs/<id>/import/ — import selected scraped prices."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            job = ScrapingJob.objects.get(pk=pk)
        except ScrapingJob.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if job.status != 'done':
            return Response({'detail': 'Job must be completed before importing.'}, status=400)

        ids = request.data.get('ids')  # list of ScrapedPrice IDs, or null/empty for all
        qs = job.results.filter(is_imported=False, matched_item__isnull=False)
        if ids:
            qs = qs.filter(id__in=ids)

        imported_count = 0
        admin_user = request.user

        for sp in qs.select_related('matched_item', 'matched_store'):
            # Resolve store — use existing matched store or create one
            if sp.matched_store:
                store = sp.matched_store
            else:
                store = _find_or_create_store(sp.raw_store_name, sp.raw_city or job.state, job.state)
                sp.matched_store = store

            Price.objects.create(
                store=store,
                item=sp.matched_item,
                user=admin_user,
                price=sp.raw_price,
                is_approved=True,
            )
            sp.is_imported = True
            sp.save(update_fields=['is_imported', 'matched_store'])
            imported_count += 1

        job.items_imported = ScrapedPrice.objects.filter(job=job, is_imported=True).count()
        job.save(update_fields=['items_imported'])

        return Response({'imported': imported_count, 'total_imported': job.items_imported})


def _find_or_create_store(name: str, city: str, state: str) -> Store:
    """Look up a store by name+state, or create a new approved one."""
    existing = Store.objects.filter(name__iexact=name, state__iexact=state).first()
    if existing:
        return existing
    lat, lng = STATE_COORDS.get(state, (9.0579, 7.4951))
    import random
    # Add tiny random offset so stores don't all stack on the exact same point
    rng = random.Random(hash(name + state))
    lat += rng.uniform(-0.05, 0.05)
    lng += rng.uniform(-0.05, 0.05)
    return Store.objects.create(
        name=name,
        address=f'{city}, {state}',
        city=city,
        state=state,
        latitude=round(lat, 5),
        longitude=round(lng, 5),
        is_approved=True,
    )
