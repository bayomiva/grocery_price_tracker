from django.contrib import admin
from .models import ScrapingJob, ScrapedPrice


class ScrapedPriceInline(admin.TabularInline):
    model = ScrapedPrice
    extra = 0
    readonly_fields = ['raw_item_name', 'raw_store_name', 'raw_price', 'raw_city', 'matched_item', 'matched_store', 'is_imported']
    can_delete = False


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'state', 'source', 'status', 'items_found', 'items_imported', 'created_by', 'created_at']
    list_filter = ['status', 'source', 'state']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'items_found', 'items_imported', 'log_text']
    inlines = [ScrapedPriceInline]


@admin.register(ScrapedPrice)
class ScrapedPriceAdmin(admin.ModelAdmin):
    list_display = ['raw_item_name', 'raw_store_name', 'raw_price', 'matched_item', 'is_imported']
    list_filter = ['is_imported', 'job__state', 'job__source']
    search_fields = ['raw_item_name', 'raw_store_name']
