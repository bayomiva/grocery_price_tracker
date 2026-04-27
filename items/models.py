from django.db import models


class GroceryItem(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
