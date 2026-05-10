"""
Management command: seed_nigeria_stores
Adds well-known local grocery / open markets for every one of Nigeria's
36 states + FCT.  Existing stores (matched by name) are skipped so the
command is safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from stores.models import Store

STORES = [
    # ── ABIA ───────────────────────────────────────────────────────────────
    {"name": "Ariaria International Market",  "address": "Ariaria, Aba, Abia State",            "lat": 5.1170,  "lng": 7.3656},
    {"name": "Umuahia Central Market",        "address": "Market Rd, Umuahia, Abia State",       "lat": 5.5262,  "lng": 7.4836},

    # ── ADAMAWA ────────────────────────────────────────────────────────────
    {"name": "Monday Market Yola",            "address": "Jimeta, Yola, Adamawa State",           "lat": 9.2888,  "lng": 12.4620},
    {"name": "Jimeta Modern Market",          "address": "Jimeta, Yola, Adamawa State",           "lat": 9.2821,  "lng": 12.4533},

    # ── AKWA IBOM ──────────────────────────────────────────────────────────
    {"name": "Itam Market",                   "address": "Itam, Uyo, Akwa Ibom State",            "lat": 5.0073,  "lng": 7.9261},
    {"name": "Akpan Andem Market",            "address": "Akpan Andem, Uyo, Akwa Ibom State",    "lat": 5.0388,  "lng": 7.9135},

    # ── ANAMBRA (top-up — Awka capital) ────────────────────────────────────
    {"name": "Eke Awka Market",               "address": "Zik Ave, Awka, Anambra State",          "lat": 6.2100,  "lng": 7.0720},

    # ── BAUCHI ─────────────────────────────────────────────────────────────
    {"name": "Muda Lawal Market",             "address": "Muda Lawal Rd, Bauchi, Bauchi State",   "lat": 10.3132, "lng": 9.8466},
    {"name": "Wunti Market",                  "address": "Wunti, Bauchi, Bauchi State",            "lat": 10.3205, "lng": 9.8358},

    # ── BAYELSA ────────────────────────────────────────────────────────────
    {"name": "Swali Market",                  "address": "Swali, Yenagoa, Bayelsa State",          "lat": 4.9267,  "lng": 6.2676},
    {"name": "Tombia Market",                 "address": "Tombia, Yenagoa, Bayelsa State",         "lat": 4.9002,  "lng": 6.2583},

    # ── BENUE ──────────────────────────────────────────────────────────────
    {"name": "Modern Market Makurdi",         "address": "Modern Market Rd, Makurdi, Benue State","lat": 7.7396,  "lng": 8.5228},
    {"name": "North Bank Market",             "address": "North Bank, Makurdi, Benue State",      "lat": 7.7227,  "lng": 8.5312},

    # ── BORNO ──────────────────────────────────────────────────────────────
    {"name": "Monday Market Maiduguri",       "address": "Monday Market, Maiduguri, Borno State", "lat": 11.8310, "lng": 13.1547},
    {"name": "Baga Road Market",              "address": "Baga Rd, Maiduguri, Borno State",       "lat": 11.8490, "lng": 13.1503},

    # ── CROSS RIVER ────────────────────────────────────────────────────────
    {"name": "Watt Market",                   "address": "Watt Market, Calabar, Cross River State","lat": 4.9500,  "lng": 8.3250},
    {"name": "Uwanse Market",                 "address": "Uwanse, Calabar, Cross River State",    "lat": 4.9557,  "lng": 8.3218},

    # ── DELTA ──────────────────────────────────────────────────────────────
    {"name": "Ogbeogonogo Market",            "address": "Ogbeogonogo, Asaba, Delta State",        "lat": 6.1974,  "lng": 6.7325},
    {"name": "Main Market Warri",             "address": "Warri Main Market, Delta State",         "lat": 5.5165,  "lng": 5.7490},

    # ── EBONYI ─────────────────────────────────────────────────────────────
    {"name": "Abakaliki Rice Mill Market",    "address": "Rice Mill, Abakaliki, Ebonyi State",    "lat": 6.3226,  "lng": 8.1144},
    {"name": "Afikpo Main Market",            "address": "Market Rd, Afikpo, Ebonyi State",       "lat": 5.8895,  "lng": 7.9237},

    # ── EDO ────────────────────────────────────────────────────────────────
    {"name": "New Benin Market",              "address": "New Benin, Benin City, Edo State",      "lat": 6.3392,  "lng": 5.6272},
    {"name": "Oba Market",                    "address": "Oba Market, Benin City, Edo State",     "lat": 6.3150,  "lng": 5.6083},

    # ── EKITI ──────────────────────────────────────────────────────────────
    {"name": "Oja Oba Market Ado Ekiti",      "address": "Oja Oba, Ado Ekiti, Ekiti State",       "lat": 7.6230,  "lng": 5.2220},
    {"name": "Shagari Market Ado Ekiti",      "address": "Shagari, Ado Ekiti, Ekiti State",       "lat": 7.6150,  "lng": 5.2312},

    # ── ENUGU (top-up — Agbani road) ───────────────────────────────────────
    {"name": "Coal Camp Market",              "address": "Coal Camp, Enugu, Enugu State",          "lat": 6.4679,  "lng": 7.5130},

    # ── FCT (top-up) ───────────────────────────────────────────────────────
    {"name": "Nyanya Market",                 "address": "Nyanya, Abuja FCT",                     "lat": 8.9917,  "lng": 7.5276},
    {"name": "Utako Market",                  "address": "Utako, Abuja FCT",                      "lat": 9.0812,  "lng": 7.4554},

    # ── GOMBE ──────────────────────────────────────────────────────────────
    {"name": "Tudun Wada Market",             "address": "Tudun Wada, Gombe, Gombe State",        "lat": 10.2897, "lng": 11.1673},
    {"name": "Pantami Market",                "address": "Pantami, Gombe, Gombe State",            "lat": 10.2963, "lng": 11.1760},

    # ── IMO ────────────────────────────────────────────────────────────────
    {"name": "Eke Ukwu Owerri Market",        "address": "Eke Ukwu, Owerri, Imo State",           "lat": 5.4837,  "lng": 7.0263},
    {"name": "Relief Market Owerri",          "address": "Relief Market, Owerri, Imo State",      "lat": 5.4782,  "lng": 7.0234},

    # ── JIGAWA ─────────────────────────────────────────────────────────────
    {"name": "Dutse Main Market",             "address": "Dutse, Jigawa State",                   "lat": 11.7004, "lng": 9.3468},
    {"name": "Hadejia Market",                "address": "Hadejia, Jigawa State",                 "lat": 12.4535, "lng": 10.0407},

    # ── KADUNA ─────────────────────────────────────────────────────────────
    {"name": "Kaduna Central Market",         "address": "Central Market, Kaduna, Kaduna State",  "lat": 10.5292, "lng": 7.4403},
    {"name": "Kasuwan Barwo Market",          "address": "Kasuwan Barwo, Kaduna, Kaduna State",   "lat": 10.5150, "lng": 7.4350},

    # ── KANO ───────────────────────────────────────────────────────────────
    {"name": "Kurmi Market",                  "address": "Kurmi Market, Kano City, Kano State",   "lat": 11.9916, "lng": 8.5211},
    {"name": "Sabon Gari Market Kano",        "address": "Sabon Gari, Kano, Kano State",          "lat": 12.0007, "lng": 8.5264},

    # ── KATSINA ────────────────────────────────────────────────────────────
    {"name": "Katsina Central Market",        "address": "Central Market, Katsina, Katsina State","lat": 12.9965, "lng": 7.5987},
    {"name": "Yan Kaba Market",               "address": "Yan Kaba, Katsina, Katsina State",      "lat": 13.0033, "lng": 7.5946},

    # ── KEBBI ──────────────────────────────────────────────────────────────
    {"name": "Birnin Kebbi Central Market",   "address": "Birnin Kebbi, Kebbi State",             "lat": 12.4530, "lng": 4.1997},
    {"name": "Argungu Market",                "address": "Argungu, Kebbi State",                  "lat": 12.7399, "lng": 4.5225},

    # ── KOGI ───────────────────────────────────────────────────────────────
    {"name": "Ganaja Market",                 "address": "Ganaja, Lokoja, Kogi State",             "lat": 7.7970,  "lng": 6.7340},
    {"name": "Lokoja Main Market",            "address": "Main Market, Lokoja, Kogi State",        "lat": 7.8026,  "lng": 6.7280},

    # ── KWARA ──────────────────────────────────────────────────────────────
    {"name": "Mandate Market Ilorin",         "address": "Mandate, Ilorin, Kwara State",           "lat": 8.4966,  "lng": 4.5568},
    {"name": "Oja Oba Market Ilorin",         "address": "Oja Oba, Ilorin, Kwara State",           "lat": 8.4918,  "lng": 4.5370},

    # ── LAGOS (top-up) ─────────────────────────────────────────────────────
    {"name": "Balogun Market",                "address": "Balogun, Lagos Island, Lagos",           "lat": 6.4550,  "lng": 3.3965},
    {"name": "Mushin Market",                 "address": "Mushin, Lagos State",                   "lat": 6.5298,  "lng": 3.3567},
    {"name": "Agege Market",                  "address": "Agege, Lagos State",                    "lat": 6.6172,  "lng": 3.3250},

    # ── NASARAWA ───────────────────────────────────────────────────────────
    {"name": "Lafia Modern Market",           "address": "Modern Market, Lafia, Nasarawa State",  "lat": 8.4966,  "lng": 8.5218},
    {"name": "Karu Market",                   "address": "Karu, Nasarawa State",                  "lat": 8.9934,  "lng": 7.5387},

    # ── NIGER ──────────────────────────────────────────────────────────────
    {"name": "Kpakungu Market Minna",         "address": "Kpakungu, Minna, Niger State",           "lat": 9.6139,  "lng": 6.5569},
    {"name": "Terminus Market Minna",         "address": "Terminus, Minna, Niger State",           "lat": 9.6175,  "lng": 6.5534},

    # ── OGUN ───────────────────────────────────────────────────────────────
    {"name": "Kuto Market Abeokuta",          "address": "Kuto, Abeokuta, Ogun State",             "lat": 7.1478,  "lng": 3.3514},
    {"name": "Lafenwa Market",                "address": "Lafenwa, Abeokuta, Ogun State",          "lat": 7.1562,  "lng": 3.3489},

    # ── ONDO ───────────────────────────────────────────────────────────────
    {"name": "Oja Oba Market Akure",          "address": "Oja Oba, Akure, Ondo State",             "lat": 7.2530,  "lng": 5.1950},
    {"name": "Shagari Market Akure",          "address": "Shagari, Akure, Ondo State",             "lat": 7.2604,  "lng": 5.1834},

    # ── OSUN ───────────────────────────────────────────────────────────────
    {"name": "Oja Oba Market Osogbo",         "address": "Oja Oba, Osogbo, Osun State",            "lat": 7.7826,  "lng": 4.5572},
    {"name": "Ataoja Market Osogbo",          "address": "Ataoja, Osogbo, Osun State",             "lat": 7.7762,  "lng": 4.5539},

    # ── OYO (top-up) ───────────────────────────────────────────────────────
    {"name": "Gbagi Market Ibadan",           "address": "Gbagi, New Ife Rd, Ibadan, Oyo State",  "lat": 7.3540,  "lng": 3.9125},

    # ── PLATEAU ────────────────────────────────────────────────────────────
    {"name": "Jos Main Market",               "address": "Main Market, Jos, Plateau State",        "lat": 9.9197,  "lng": 8.8941},
    {"name": "Terminus Market Jos",           "address": "Terminus, Jos, Plateau State",           "lat": 9.9234,  "lng": 8.8885},

    # ── RIVERS (top-up) ────────────────────────────────────────────────────
    {"name": "Rumuola Market",                "address": "Rumuola, Port Harcourt, Rivers State",   "lat": 4.8398,  "lng": 7.0279},
    {"name": "Choba Market",                  "address": "Choba, Rivers State",                   "lat": 4.8905,  "lng": 6.9342},

    # ── SOKOTO ─────────────────────────────────────────────────────────────
    {"name": "Sokoto Central Market",         "address": "Central Market, Sokoto, Sokoto State",  "lat": 13.0059, "lng": 5.2476},
    {"name": "Emir Market Sokoto",            "address": "Emir Market, Sokoto, Sokoto State",     "lat": 13.0620, "lng": 5.2503},

    # ── TARABA ─────────────────────────────────────────────────────────────
    {"name": "Jalingo Main Market",           "address": "Main Market, Jalingo, Taraba State",    "lat": 8.9016,  "lng": 11.3623},
    {"name": "Wukari Market",                 "address": "Wukari, Taraba State",                  "lat": 7.8704,  "lng": 9.7793},

    # ── YOBE ───────────────────────────────────────────────────────────────
    {"name": "Monday Market Damaturu",        "address": "Monday Market, Damaturu, Yobe State",   "lat": 11.7470, "lng": 11.9589},
    {"name": "Potiskum Market",               "address": "Main Market, Potiskum, Yobe State",     "lat": 11.7098, "lng": 11.0777},

    # ── ZAMFARA ────────────────────────────────────────────────────────────
    {"name": "Gusau Central Market",          "address": "Central Market, Gusau, Zamfara State",  "lat": 12.1697, "lng": 6.6618},
    {"name": "Kaura Namoda Market",           "address": "Kaura Namoda, Zamfara State",            "lat": 12.5975, "lng": 6.5881},
]


class Command(BaseCommand):
    help = "Seed well-known local markets for all 36 Nigerian states + FCT."

    def handle(self, *args, **options):
        added = 0
        skipped = 0
        existing_names = set(Store.objects.values_list('name', flat=True))

        for s in STORES:
            if s['name'] in existing_names:
                skipped += 1
                continue
            Store.objects.create(
                name=s['name'],
                address=s['address'],
                latitude=s['lat'],
                longitude=s['lng'],
                is_approved=True,
            )
            self.stdout.write(f"  ✓ {s['name']}")
            added += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {added} stores added, {skipped} already existed."
        ))
