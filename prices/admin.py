from django.contrib import admin
from django.utils.html import format_html
from .models import Price


@admin.action(description='✅ Approve selected submissions (award +10 pts each)')
def approve_prices(modeladmin, request, queryset):
    approved = 0
    for price in queryset.filter(is_approved=False).select_related('user'):
        price.is_approved = True
        price.save(update_fields=['is_approved'])
        price.user.points += 10
        price.user.save(update_fields=['points'])
        approved += 1
    modeladmin.message_user(request, f'{approved} submission(s) approved and points awarded.')


@admin.action(description='❌ Reject and delete selected submissions')
def reject_prices(modeladmin, request, queryset):
    count, _ = queryset.delete()
    modeladmin.message_user(request, f'{count} submission(s) rejected and removed.')


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['item', 'store', 'formatted_price', 'user', 'status_badge', 'created_at']
    list_filter = ['is_approved', 'item__category', 'store']
    search_fields = ['item__name', 'store__name', 'user__username']
    date_hierarchy = 'created_at'
    ordering = ['is_approved', '-created_at']
    actions = [approve_prices, reject_prices]
    readonly_fields = ['created_at']

    @admin.display(description='Price')
    def formatted_price(self, obj):
        return f'₦{obj.price:,.0f}'

    @admin.display(description='Status', ordering='is_approved')
    def status_badge(self, obj):
        if obj.is_approved:
            return format_html('<span style="color:#16a34a;font-weight:bold">✅ Approved</span>')
        return format_html('<span style="color:#dc2626;font-weight:bold">⏳ Pending</span>')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('item', 'store', 'user')
