from rest_framework import serializers
from .models import ScrapingJob, ScrapedPrice


class ScrapedPriceSerializer(serializers.ModelSerializer):
    matchedItemId = serializers.IntegerField(source='matched_item_id', read_only=True)
    matchedItemName = serializers.SerializerMethodField()
    matchedStoreId = serializers.IntegerField(source='matched_store_id', read_only=True)
    matchedStoreName = serializers.SerializerMethodField()

    class Meta:
        model = ScrapedPrice
        fields = [
            'id', 'raw_item_name', 'raw_store_name', 'raw_price',
            'raw_city', 'source_url', 'is_imported',
            'matchedItemId', 'matchedItemName',
            'matchedStoreId', 'matchedStoreName',
        ]

    def get_matchedItemName(self, obj):
        return obj.matched_item.name if obj.matched_item else None

    def get_matchedStoreName(self, obj):
        return obj.matched_store.name if obj.matched_store else None


class ScrapingJobSerializer(serializers.ModelSerializer):
    createdBy = serializers.SerializerMethodField()
    sourceLabel = serializers.SerializerMethodField()
    results = ScrapedPriceSerializer(many=True, read_only=True)

    class Meta:
        model = ScrapingJob
        fields = [
            'id', 'state', 'source', 'sourceLabel', 'status',
            'createdBy', 'created_at', 'started_at', 'completed_at',
            'items_found', 'items_imported', 'log_text', 'results',
        ]

    def get_createdBy(self, obj):
        return obj.created_by.username if obj.created_by else 'system'

    def get_sourceLabel(self, obj):
        return dict(obj._meta.get_field('source').choices).get(obj.source, obj.source)


class ScrapingJobListSerializer(ScrapingJobSerializer):
    """Lightweight version — omits results for list endpoints."""
    class Meta(ScrapingJobSerializer.Meta):
        fields = [f for f in ScrapingJobSerializer.Meta.fields if f != 'results']
