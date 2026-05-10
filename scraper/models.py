from django.conf import settings
from django.db import models

NIGERIAN_STATES = [
    ('Abia', 'Abia'), ('Adamawa', 'Adamawa'), ('Akwa Ibom', 'Akwa Ibom'),
    ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'),
    ('Benue', 'Benue'), ('Borno', 'Borno'), ('Cross River', 'Cross River'),
    ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'), ('Edo', 'Edo'),
    ('Ekiti', 'Ekiti'), ('Enugu', 'Enugu'), ('FCT', 'FCT (Abuja)'),
    ('Gombe', 'Gombe'), ('Imo', 'Imo'), ('Jigawa', 'Jigawa'),
    ('Kaduna', 'Kaduna'), ('Kano', 'Kano'), ('Katsina', 'Katsina'),
    ('Kebbi', 'Kebbi'), ('Kogi', 'Kogi'), ('Kwara', 'Kwara'),
    ('Lagos', 'Lagos'), ('Nasarawa', 'Nasarawa'), ('Niger', 'Niger'),
    ('Ogun', 'Ogun'), ('Ondo', 'Ondo'), ('Osun', 'Osun'),
    ('Oyo', 'Oyo'), ('Plateau', 'Plateau'), ('Rivers', 'Rivers'),
    ('Sokoto', 'Sokoto'), ('Taraba', 'Taraba'), ('Yobe', 'Yobe'),
    ('Zamfara', 'Zamfara'),
]

SCRAPER_SOURCES = [
    ('jiji', 'Jiji.ng'),
    ('jumia', 'Jumia Nigeria'),
    ('synthetic', 'Synthetic (NBS Data)'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('running', 'Running'),
    ('done', 'Completed'),
    ('failed', 'Failed'),
]


class ScrapingJob(models.Model):
    state = models.CharField(max_length=100)
    source = models.CharField(max_length=20, choices=SCRAPER_SOURCES, default='jiji')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scraping_jobs',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    items_found = models.IntegerField(default=0)
    items_imported = models.IntegerField(default=0)
    log_text = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.source} / {self.state} [{self.status}]'


class ScrapedPrice(models.Model):
    job = models.ForeignKey(ScrapingJob, on_delete=models.CASCADE, related_name='results')
    raw_item_name = models.CharField(max_length=300)
    raw_store_name = models.CharField(max_length=300)
    raw_price = models.DecimalField(max_digits=12, decimal_places=2)
    raw_city = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)
    matched_item = models.ForeignKey(
        'items.GroceryItem', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='scraped_prices',
    )
    matched_store = models.ForeignKey(
        'stores.Store', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='scraped_prices',
    )
    is_imported = models.BooleanField(default=False)
    scraped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['raw_item_name']

    def __str__(self):
        return f'{self.raw_item_name} ₦{self.raw_price} @ {self.raw_store_name}'
