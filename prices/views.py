import math
from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max, Avg, Count
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from stores.models import Store
from items.models import GroceryItem
from accounts.models import User
from .models import Price
from .serializers import PriceSerializer


# ── HTML page views ────────────────────────────────────────────────────────────

def index_page(request):
    return render(request, 'index.html')

def submit_price_page(request):
    return render(request, 'submit_price.html')

def compare_prices_page(request):
    return render(request, 'compare_prices.html')

def admin_dashboard_page(request):
    return render(request, 'admin_dashboard.html')


# ── Price REST API ─────────────────────────────────────────────────────────────

class PriceListCreateView(generics.ListCreateAPIView):
    serializer_class = PriceSerializer

    def get_queryset(self):
        return Price.objects.filter(is_approved=True).select_related('store', 'item', 'user')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Saved as pending — points are awarded when an admin approves
        serializer.save(user=self.request.user, is_approved=False)


class ComparePricesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        item_id = request.query_params.get('item')
        if not item_id:
            return Response({'detail': 'item parameter required.'}, status=400)

        prices = (
            Price.objects
            .filter(item_id=item_id, is_approved=True)
            .select_related('store')
            .order_by('price')
        )
        if not prices.exists():
            return Response([])

        min_price = prices.first().price
        return Response([{
            'storeId': p.store.id,
            'storeName': p.store.name,
            'storeAddress': p.store.address,
            'price': float(p.price),
            'isCheapest': p.price == min_price,
            'submittedAt': p.created_at.isoformat(),
        } for p in prices])


class PriceStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        item_id = request.query_params.get('item')
        if not item_id:
            return Response({'detail': 'item parameter required.'}, status=400)

        agg = Price.objects.filter(item_id=item_id, is_approved=True).aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            total=Count('id'),
        )
        return Response({
            'lowestPrice': float(agg['min_price'] or 0),
            'highestPrice': float(agg['max_price'] or 0),
            'averagePrice': float(agg['avg_price'] or 0),
            'totalSubmissions': agg['total'],
        })


class RecentPricesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        prices = (
            Price.objects.filter(is_approved=True)
            .select_related('store', 'item', 'user')
            .order_by('-created_at')[:20]
        )
        return Response([{
            'id': p.id,
            'itemName': p.item.name,
            'itemCategory': p.item.category,
            'storeName': p.store.name,
            'price': float(p.price),
            'username': p.user.username,
            'createdAt': p.created_at.isoformat(),
        } for p in prices])


class MySubmissionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        prices = (
            Price.objects.filter(user=request.user)
            .select_related('store', 'item')
            .order_by('-created_at')
        )
        return Response([{
            'id': p.id,
            'itemName': p.item.name,
            'storeName': p.store.name,
            'price': float(p.price),
            'isApproved': p.is_approved,
            'createdAt': p.created_at.isoformat(),
        } for p in prices])


class LeaderboardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = User.objects.filter(points__gt=0).order_by('-points')[:10]
        return Response([{
            'userId': u.id,
            'username': u.username,
            'points': u.points,
            'submissionsCount': Price.objects.filter(user=u, is_approved=True).count(),
        } for u in users])


# ── Admin approval API ─────────────────────────────────────────────────────────

class PendingPricesView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        prices = (
            Price.objects.filter(is_approved=False)
            .select_related('store', 'item', 'user')
            .order_by('-created_at')
        )
        return Response([{
            'id': p.id,
            'itemName': p.item.name,
            'itemCategory': p.item.category,
            'storeName': p.store.name,
            'price': float(p.price),
            'username': p.user.username,
            'userId': p.user.id,
            'createdAt': p.created_at.isoformat(),
        } for p in prices])


class AdminAllSubmissionsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 50))
        prices = (
            Price.objects.all()
            .select_related('store', 'item', 'user')
            .order_by('-created_at')[:limit]
        )
        return Response([{
            'id': p.id,
            'itemName': p.item.name,
            'itemCategory': p.item.category,
            'storeName': p.store.name,
            'price': float(p.price),
            'username': p.user.username,
            'userId': p.user.id,
            'isApproved': p.is_approved,
            'createdAt': p.created_at.isoformat(),
        } for p in prices])


class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.db.models.functions import TruncDate
        from django.utils import timezone
        import datetime

        # Submissions per day (last 14 days)
        since = timezone.now() - datetime.timedelta(days=14)
        daily = (
            Price.objects
            .filter(created_at__gte=since)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # Per-category breakdown (approved only)
        by_category = (
            Price.objects
            .filter(is_approved=True)
            .values('item__category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'dailyActivity': [{'date': str(d['day']), 'count': d['count']} for d in daily],
            'byCategory': [{'category': d['item__category'], 'count': d['count']} for d in by_category],
        })


class PriceApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        price = get_object_or_404(Price, pk=pk)
        if not price.is_approved:
            price.is_approved = True
            price.save(update_fields=['is_approved'])
            # Award +10 points to the submitter
            price.user.points += 10
            price.user.save(update_fields=['points'])
        return Response({
            'id': price.id,
            'is_approved': True,
            'username': price.user.username,
            'newPoints': price.user.points,
        })


class PriceRejectView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        price = get_object_or_404(Price, pk=pk)
        info = {
            'id': price.id,
            'itemName': price.item.name,
            'storeName': price.store.name,
        }
        price.delete()
        return Response({'detail': 'Price submission rejected and removed.', **info})


# ── Dashboard summary ──────────────────────────────────────────────────────────

class DashboardSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = {
            'totalStores': Store.objects.filter(is_approved=True).count(),
            'totalItems': GroceryItem.objects.count(),
            'totalPriceSubmissions': Price.objects.filter(is_approved=True).count(),
            'totalUsers': User.objects.count(),
        }
        # Include pending count for admin users
        if request.user.is_authenticated and request.user.is_staff:
            data['pendingSubmissions'] = Price.objects.filter(is_approved=False).count()
        return Response(data)
