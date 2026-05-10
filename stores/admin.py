from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'latitude', 'longitude', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    search_fields = ['name', 'address']
