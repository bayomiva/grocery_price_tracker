from django.core.management.base import BaseCommand
from items.models import GroceryItem

ITEM_IMAGES = {
    'Garri (1kg)':        'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&q=80&fit=crop',
    'Rice (1kg)':         'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400&q=80&fit=crop',
    'Semovita (1kg)':     'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80&fit=crop',
    'Beans (1kg)':        'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=400&q=80&fit=crop',
    'Yam (1 tuber)':      'https://images.unsplash.com/photo-1618170027586-d5cc8c3d2b45?w=400&q=80&fit=crop',
    'Tomatoes (basket)':  'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400&q=80&fit=crop',
    'Onions (1kg)':       'https://images.unsplash.com/photo-1508747703725-719777637510?w=400&q=80&fit=crop',
    'Plantain (bunch)':   'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400&q=80&fit=crop',
    'Palm Oil (1 litre)': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&q=80&fit=crop',
    'Groundnut Oil (1L)': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&q=80&fit=crop',
    'Indomie x40 pack':   'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80&fit=crop',
    'Milo (400g)':        'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400&q=80&fit=crop',
    'Peak Milk (400g)':   'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80&fit=crop',
    'Eggs (crate of 30)': 'https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=400&q=80&fit=crop',
    'Bread (600g loaf)':  'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80&fit=crop',
}

CATEGORY_FALLBACKS = {
    'Staples':   'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400&q=80&fit=crop',
    'Vegetables':'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&q=80&fit=crop',
    'Fruits':    'https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?w=400&q=80&fit=crop',
    'Oils':      'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&q=80&fit=crop',
    'Noodles':   'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80&fit=crop',
    'Beverages': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80&fit=crop',
    'Dairy':     'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80&fit=crop',
    'Bakery':    'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80&fit=crop',
}


class Command(BaseCommand):
    help = 'Populate GroceryItem.image_url with curated Unsplash images.'

    def handle(self, *args, **options):
        updated = 0
        skipped = 0
        for item in GroceryItem.objects.all():
            url = ITEM_IMAGES.get(item.name) or CATEGORY_FALLBACKS.get(item.category, '')
            if url and item.image_url != url:
                item.image_url = url
                item.save(update_fields=['image_url'])
                self.stdout.write(f'  ✓ {item.name}')
                updated += 1
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {updated} updated, {skipped} already set or no match.'
        ))
