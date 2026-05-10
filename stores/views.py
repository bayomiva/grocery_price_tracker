import math
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Store
from .serializers import StoreSerializer


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


class StoreListView(generics.ListCreateAPIView):
    serializer_class = StoreSerializer

    def get_queryset(self):
        qs = Store.objects.filter(is_approved=True)
        state = self.request.query_params.get('state')
        if state:
            qs = qs.filter(state=state)
        return qs

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(is_approved=False)


class StatesListView(APIView):
    """Return unique states and their store counts, ordered alphabetically."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db.models import Count, Avg
        rows = (
            Store.objects
            .filter(is_approved=True)
            .exclude(state='')
            .values('state')
            .annotate(
                store_count=Count('id'),
                center_lat=Avg('latitude'),
                center_lng=Avg('longitude'),
            )
            .order_by('state')
        )
        return Response([{
            'state': r['state'],
            'storeCount': r['store_count'],
            'centerLat': round(r['center_lat'], 4),
            'centerLng': round(r['center_lng'], 4),
        } for r in rows])


class NearbyStoresView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params['lat'])
            lng = float(request.query_params['lng'])
        except (KeyError, TypeError, ValueError):
            return Response(
                {'detail': 'lat and lng query parameters are required.'},
                status=400,
            )

        radius = float(request.query_params.get('radius', 200))

        results = []
        for s in Store.objects.filter(is_approved=True):
            dist = haversine(lat, lng, s.latitude, s.longitude)
            if dist <= radius:
                results.append({
                    'id': s.id,
                    'name': s.name,
                    'address': s.address,
                    'latitude': s.latitude,
                    'longitude': s.longitude,
                    'distanceKm': round(dist, 1),
                })

        results.sort(key=lambda x: x['distanceKm'])
        return Response(results)
