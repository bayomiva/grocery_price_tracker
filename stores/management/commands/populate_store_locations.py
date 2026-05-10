"""
Parses city and state from the existing address field on every Store.
Address format used throughout this project:
  "Area, City, State"   e.g. "Bodija Estate, Ibadan, Oyo State"
  "Area, Abuja FCT"     e.g. "Wuse Zone 5, Abuja FCT"
"""
from django.core.management.base import BaseCommand
from stores.models import Store

FCT_ALIASES = {'Abuja FCT', 'FCT', 'Federal Capital Territory'}

# Normalise bare state names to their "X State" form
STATE_NORMALIZE = {
    'Lagos':  'Lagos State',
    'Rivers': 'Rivers State',
    'Ogun':   'Ogun State',
    'Kano':   'Kano State',
    'Edo':    'Edo State',
    'Ekiti':  'Ekiti State',
}


def _parse(address: str):
    parts = [p.strip() for p in address.split(',')]
    raw_state = parts[-1]

    # Normalise FCT variants
    for alias in FCT_ALIASES:
        if alias in raw_state:
            city = 'Abuja'
            state = 'FCT'
            return city, state

    state = STATE_NORMALIZE.get(raw_state, raw_state)
    city = parts[-2] if len(parts) >= 2 else parts[0]
    return city, state


class Command(BaseCommand):
    help = 'Populate Store.city and Store.state from the address field.'

    def handle(self, *args, **options):
        updated = 0
        for store in Store.objects.all():
            city, state = _parse(store.address)
            if store.city != city or store.state != state:
                store.city = city
                store.state = state
                store.save(update_fields=['city', 'state'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'Done. {updated} stores updated with city/state.'
        ))
