"""
Management command: load_sample_data

Populates the database with a representative set of Nigerian grocery stores,
common grocery items, and realistic ₦ prices for every store-item pair.

All operations are idempotent — running the command multiple times is safe;
existing records are never duplicated or overwritten.

Usage:
    python manage.py load_sample_data
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from stores.models import Store
from items.models import GroceryItem
from prices.models import Price


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

STORES = [
    # Lagos
    {
        "name": "Shoprite (Ikeja City Mall)",
        "address": "Obafemi Awolowo Way, Ikeja, Lagos",
        "city": "Lagos",
        "state": "Lagos State",
        "latitude": 6.6018,
        "longitude": 3.3515,
    },
    {
        "name": "Shoprite (Surulere)",
        "address": "Adeniran Ogunsanya St, Surulere, Lagos",
        "city": "Lagos",
        "state": "Lagos State",
        "latitude": 6.4969,
        "longitude": 3.3538,
    },
    {
        "name": "Justrite Superstore (Ikorodu)",
        "address": "Lagos-Ikorodu Rd, Ikorodu, Lagos",
        "city": "Lagos",
        "state": "Lagos State",
        "latitude": 6.6194,
        "longitude": 3.5063,
    },
    {
        "name": "Ebeano Supermarket (Lekki)",
        "address": "Admiralty Way, Lekki Phase 1, Lagos",
        "city": "Lagos",
        "state": "Lagos State",
        "latitude": 6.4317,
        "longitude": 3.4734,
    },
    # Abuja
    {
        "name": "Shoprite (Jabi Lake Mall)",
        "address": "Jabi Lake Mall, Jabi, Abuja FCT",
        "city": "Abuja",
        "state": "FCT",
        "latitude": 9.0726,
        "longitude": 7.4302,
    },
    {
        "name": "Hubmart Superstore (Wuse 2)",
        "address": "Aminu Kano Crescent, Wuse 2, Abuja FCT",
        "city": "Abuja",
        "state": "FCT",
        "latitude": 9.0726,
        "longitude": 7.4892,
    },
    # Port Harcourt
    {
        "name": "Shoprite (Port Harcourt Mall)",
        "address": "Woji Rd, Port Harcourt, Rivers State",
        "city": "Port Harcourt",
        "state": "Rivers State",
        "latitude": 4.8396,
        "longitude": 7.0135,
    },
    {
        "name": "Spar (Port Harcourt)",
        "address": "Stadium Rd, Port Harcourt, Rivers State",
        "city": "Port Harcourt",
        "state": "Rivers State",
        "latitude": 4.8156,
        "longitude": 7.0498,
    },
    # Ibadan
    {
        "name": "Shoprite (Palms Mall Ibadan)",
        "address": "Palms Shopping Mall, Ring Rd, Ibadan, Oyo State",
        "city": "Ibadan",
        "state": "Oyo State",
        "latitude": 7.3775,
        "longitude": 3.9470,
    },
    {
        "name": "Spar (Ibadan)",
        "address": "Challenge, Ibadan, Oyo State",
        "city": "Ibadan",
        "state": "Oyo State",
        "latitude": 7.3756,
        "longitude": 3.8976,
    },
]

ITEMS = [
    # Staples
    {"name": "Garri (1kg)",        "category": "Staples"},
    {"name": "Rice (1kg)",         "category": "Staples"},
    {"name": "Semovita (1kg)",     "category": "Staples"},
    {"name": "Beans (1kg)",        "category": "Staples"},
    {"name": "Yam (1 tuber)",      "category": "Staples"},
    {"name": "Wheat Flour (1kg)",  "category": "Staples"},
    # Vegetables & Fruits
    {"name": "Tomatoes (basket)",  "category": "Vegetables"},
    {"name": "Onions (1kg)",       "category": "Vegetables"},
    {"name": "Pepper (1kg)",       "category": "Vegetables"},
    {"name": "Plantain (bunch)",   "category": "Fruits"},
    {"name": "Banana (bunch)",     "category": "Fruits"},
    # Proteins
    {"name": "Eggs (crate of 30)", "category": "Proteins"},
    {"name": "Chicken (1kg)",      "category": "Proteins"},
    {"name": "Beef (1kg)",         "category": "Proteins"},
    {"name": "Catfish (1kg)",      "category": "Proteins"},
    {"name": "Stockfish (500g)",   "category": "Proteins"},
    # Oils & Condiments
    {"name": "Palm Oil (1 litre)", "category": "Oils"},
    {"name": "Groundnut Oil (1L)", "category": "Oils"},
    {"name": "Vegetable Oil (1L)", "category": "Oils"},
    {"name": "Seasoning Cubes (50-pack)", "category": "Condiments"},
    {"name": "Tomato Paste (70g tin)",    "category": "Condiments"},
    # Dairy & Beverages
    {"name": "Peak Milk (400g)",   "category": "Dairy"},
    {"name": "Milo (400g)",        "category": "Beverages"},
    {"name": "Lipton Tea (100 bags)", "category": "Beverages"},
    # Packaged / Bakery
    {"name": "Indomie x40 pack",   "category": "Noodles"},
    {"name": "Bread (600g loaf)",  "category": "Bakery"},
    {"name": "Spaghetti (500g)",   "category": "Staples"},
]

# Base prices in Naira (₦) — mid-2024 market estimates
BASE_PRICES = {
    "Garri (1kg)":              700,
    "Rice (1kg)":              1400,
    "Semovita (1kg)":           950,
    "Beans (1kg)":             1600,
    "Yam (1 tuber)":           2500,
    "Wheat Flour (1kg)":        900,
    "Tomatoes (basket)":       3500,
    "Onions (1kg)":             700,
    "Pepper (1kg)":            1200,
    "Plantain (bunch)":        2200,
    "Banana (bunch)":          1500,
    "Eggs (crate of 30)":      5000,
    "Chicken (1kg)":           3500,
    "Beef (1kg)":              4500,
    "Catfish (1kg)":           3000,
    "Stockfish (500g)":        4000,
    "Palm Oil (1 litre)":      2000,
    "Groundnut Oil (1L)":      2500,
    "Vegetable Oil (1L)":      2200,
    "Seasoning Cubes (50-pack)": 600,
    "Tomato Paste (70g tin)":   350,
    "Peak Milk (400g)":        3000,
    "Milo (400g)":             3800,
    "Lipton Tea (100 bags)":   1800,
    "Indomie x40 pack":        5500,
    "Bread (600g loaf)":        900,
    "Spaghetti (500g)":         800,
}

# Seed user created solely to satisfy the Price.user FK requirement
SEED_USER = {
    "username": "sample_data_bot",
    "email": "sample_data_bot@internal.local",
    "password": "sample_data_bot_!nternalOnly",
}


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Load sample Nigerian grocery stores, items, and prices into the "
        "database. Safe to run multiple times — existing records are skipped."
    )

    def handle(self, *args, **options):
        random.seed(42)  # reproducible price variation

        with transaction.atomic():
            seed_user = self._ensure_seed_user()
            stores = self._load_stores()
            items = self._load_items()
            prices_created = self._load_prices(stores, items, seed_user)

        self._print_summary(stores, items, prices_created)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_seed_user(self):
        """Return the internal seed user, creating it if necessary."""
        user, created = User.objects.get_or_create(
            username=SEED_USER["username"],
            defaults={
                "email": SEED_USER["email"],
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            user.set_password(SEED_USER["password"])
            user.save(update_fields=["password"])
            self.stdout.write(f"  [user]  Created seed user '{user.username}'")
        else:
            self.stdout.write(f"  [user]  Seed user '{user.username}' already exists")
        return user

    def _load_stores(self):
        """Create stores that don't already exist; return all sample stores."""
        self.stdout.write("\nLoading stores...")
        stores = []
        created_count = 0
        skipped_count = 0

        for data in STORES:
            store, created = Store.objects.get_or_create(
                name=data["name"],
                defaults={
                    "address":   data["address"],
                    "city":      data["city"],
                    "state":     data["state"],
                    "latitude":  data["latitude"],
                    "longitude": data["longitude"],
                    "is_approved": True,
                },
            )
            stores.append(store)
            if created:
                created_count += 1
                self.stdout.write(f"  [store] Created  : {store.name}")
            else:
                skipped_count += 1
                self.stdout.write(f"  [store] Exists   : {store.name}")

        self.stdout.write(
            f"  → {created_count} created, {skipped_count} already existed"
        )
        return stores

    def _load_items(self):
        """Create grocery items that don't already exist; return all sample items."""
        self.stdout.write("\nLoading items...")
        items = []
        created_count = 0
        skipped_count = 0

        for data in ITEMS:
            item, created = GroceryItem.objects.get_or_create(
                name=data["name"],
                defaults={"category": data["category"]},
            )
            items.append(item)
            if created:
                created_count += 1
                self.stdout.write(f"  [item]  Created  : {item.name} ({item.category})")
            else:
                skipped_count += 1
                self.stdout.write(f"  [item]  Exists   : {item.name}")

        self.stdout.write(
            f"  → {created_count} created, {skipped_count} already existed"
        )
        return items

    def _load_prices(self, stores, items, seed_user):
        """
        Create one price entry per store-item pair that doesn't already have one.
        Prices are the base price ± up to 20 % variation, rounded to the nearest ₦50.
        """
        self.stdout.write("\nLoading prices...")
        created_count = 0
        skipped_count = 0

        for item in items:
            base = BASE_PRICES.get(item.name, 1000)
            for store in stores:
                if Price.objects.filter(store=store, item=item).exists():
                    skipped_count += 1
                    continue

                variation = random.uniform(-0.15, 0.20)
                price_val = max(50, round(base * (1 + variation) / 50) * 50)

                Price.objects.create(
                    store=store,
                    item=item,
                    user=seed_user,
                    price=price_val,
                    is_approved=True,
                )
                created_count += 1

        self.stdout.write(
            f"  → {created_count} created, {skipped_count} already existed"
        )
        return created_count

    def _print_summary(self, stores, items, prices_created):
        total_possible = len(stores) * len(items)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Sample data loaded successfully.\n"
                f"  Stores : {len(stores)}\n"
                f"  Items  : {len(items)}\n"
                f"  Prices : {prices_created} new "
                f"(up to {total_possible} total combinations)\n"
                f"\n"
                f"  Tip: run 'python manage.py seed_data' for a fuller dataset\n"
                f"  including open markets across all 36 states."
            )
        )
