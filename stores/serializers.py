from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'city', 'state', 'latitude', 'longitude', 'is_approved', 'created_at']
