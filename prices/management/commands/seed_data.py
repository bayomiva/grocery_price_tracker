import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts.models import User
from stores.models import Store
from items.models import GroceryItem
from prices.models import Price


STORES = [
    {"name": "Mile 12 Market",       "address": "Mile 12, Lagos Mainland, Lagos",       "latitude": 6.6019, "longitude": 3.3795},
    {"name": "Oyingbo Market",       "address": "Oyingbo, Lagos Island, Lagos",          "latitude": 6.4716, "longitude": 3.3874},
    {"name": "Wuse Market",          "address": "Wuse Zone 5, Abuja FCT",               "latitude": 9.0643, "longitude": 7.4892},
    {"name": "Garki Market",         "address": "Garki Area 1, Abuja FCT",              "latitude": 9.0238, "longitude": 7.4901},
    {"name": "Bodija Market",        "address": "Bodija Estate, Ibadan, Oyo State",     "latitude": 7.4167, "longitude": 3.8975},
    {"name": "Dugbe Market",         "address": "Dugbe, Ibadan, Oyo State",             "latitude": 7.3756, "longitude": 3.8976},
    {"name": "Mile 1 Market Diobu",  "address": "Mile 1, Diobu, Port Harcourt, Rivers","latitude": 4.8396, "longitude": 7.0135},
    {"name": "Oil Mill Market",      "address": "Oil Mill, Port Harcourt, Rivers State","latitude": 4.8156, "longitude": 7.0498},
    {"name": "Ogbete Main Market",   "address": "Ogbete, Enugu, Enugu State",           "latitude": 6.4421, "longitude": 7.4983},
    {"name": "New Market Enugu",     "address": "New Market Road, Enugu, Enugu State",  "latitude": 6.4597, "longitude": 7.5013},
    {"name": "Onitsha Main Market",  "address": "Onitsha, Anambra State",               "latitude": 6.1333, "longitude": 6.7833},
    {"name": "Bridgehead Market",    "address": "Bridgehead, Onitsha, Anambra State",   "latitude": 6.1501, "longitude": 6.7958},
]

ITEMS = [
    {"name": "Garri (1kg)",         "category": "Staples"},
    {"name": "Rice (1kg)",          "category": "Staples"},
    {"name": "Semovita (1kg)",      "category": "Staples"},
    {"name": "Beans (1kg)",         "category": "Staples"},
    {"name": "Tomatoes (basket)",   "category": "Vegetables"},
    {"name": "Onions (1kg)",        "category": "Vegetables"},
    {"name": "Plantain (bunch)",    "category": "Fruits"},
    {"name": "Yam (1 tuber)",       "category": "Staples"},
    {"name": "Palm Oil (1 litre)",  "category": "Oils"},
    {"name": "Groundnut Oil (1L)",  "category": "Oils"},
    {"name": "Indomie x40 pack",    "category": "Noodles"},
    {"name": "Milo (400g)",         "category": "Beverages"},
    {"name": "Peak Milk (400g)",    "category": "Dairy"},
    {"name": "Bread (600g loaf)",   "category": "Bakery"},
    {"name": "Eggs (crate of 30)",  "category": "Dairy"},
]

BASE_PRICES = {
    "Garri (1kg)": 700, "Rice (1kg)": 1200, "Semovita (1kg)": 900,
    "Beans (1kg)": 1500, "Tomatoes (basket)": 3000, "Onions (1kg)": 600,
    "Plantain (bunch)": 2000, "Yam (1 tuber)": 2500, "Palm Oil (1 litre)": 1800,
    "Groundnut Oil (1L)": 2200, "Indomie x40 pack": 5000, "Milo (400g)": 3500,
    "Peak Milk (400g)": 2800, "Bread (600g loaf)": 800, "Eggs (crate of 30)": 4500,
}

USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "admin123",
     "is_superuser": True, "is_staff": True},
    {"username": "alice", "email": "alice@example.com", "password": "user123"},
    {"username": "bob",   "email": "bob@example.com",   "password": "user123"},
]


class Command(BaseCommand):
    help = "Seed the database with Nigerian grocery market data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding users...")
        users = []
        for u in USERS:
            user, created = User.objects.get_or_create(
                email=u['email'],
                defaults={
                    'username': u['username'],
                    'is_superuser': u.get('is_superuser', False),
                    'is_staff': u.get('is_staff', False),
                }
            )
            if created:
                user.set_password(u['password'])
                user.save()
            Token.objects.get_or_create(user=user)
            users.append(user)
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {user.username}")

        self.stdout.write("Seeding stores...")
        stores = []
        for s in STORES:
            store, created = Store.objects.get_or_create(
                name=s['name'],
                defaults={'address': s['address'], 'latitude': s['latitude'],
                          'longitude': s['longitude'], 'is_approved': True}
            )
            stores.append(store)
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {store.name}")

        self.stdout.write("Seeding grocery items...")
        items = []
        for i in ITEMS:
            item, created = GroceryItem.objects.get_or_create(
                name=i['name'], defaults={'category': i['category']}
            )
            items.append(item)
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {item.name}")

        self.stdout.write("Seeding prices...")
        submitters = [u for u in users if not u.is_superuser]
        now = timezone.now()
        random.seed(42)
        count = 0
        for item in items:
            base = BASE_PRICES.get(item.name, 1000)
            for store in stores:
                if not Price.objects.filter(store=store, item=item).exists():
                    variation = random.uniform(-0.15, 0.20)
                    price_val = round(base * (1 + variation) / 50) * 50
                    days_ago = random.randint(0, 30)
                    Price.objects.create(
                        store=store, item=item,
                        user=random.choice(submitters),
                        price=price_val, is_approved=True,
                        created_at=now - timedelta(days=days_ago,
                                                   hours=random.randint(0, 23)),
                    )
                    count += 1

        for user in submitters:
            sub_count = Price.objects.filter(user=user).count()
            user.points = sub_count * 10
            user.save(update_fields=['points'])

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Seeded {len(stores)} stores, {len(items)} items, {count} prices."
        ))
