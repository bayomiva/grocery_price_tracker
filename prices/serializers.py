from rest_framework import serializers
from .models import Price


class PriceSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_category = serializers.CharField(source='item.category', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Price
        fields = [
            'id', 'store', 'store_name', 'item', 'item_name',
            'item_category', 'user', 'username', 'price',
            'is_approved', 'created_at',
        ]
        read_only_fields = ['user', 'is_approved']
