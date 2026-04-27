from django.conf import settings
from django.db import models


class Price(models.Model):
    store = models.ForeignKey(
        'stores.Store', on_delete=models.CASCADE, related_name='prices'
    )
    item = models.ForeignKey(
        'items.GroceryItem', on_delete=models.CASCADE, related_name='prices'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prices'
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='price_photos/', null=True, blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item.name} @ {self.store.name}: ₦{self.price}"
