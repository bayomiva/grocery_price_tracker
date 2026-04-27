from rest_framework import generics, permissions
from .models import GroceryItem
from .serializers import GroceryItemSerializer


class ItemListView(generics.ListAPIView):
    serializer_class = GroceryItemSerializer
    permission_classes = [permissions.AllowAny]
    queryset = GroceryItem.objects.all()
