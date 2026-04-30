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
        return Store.objects.filter(is_approved=True)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(is_approved=False)


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
