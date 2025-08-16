# seed_users.py  — create 1 user per role + 1 contractor per company

from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import Company

HQ_COMPANY = "Bohan Hyland Holdings Limited"

# Non-contractor roles -> all attached to HQ_COMPANY
NON_CONTRACTOR_USERS = [
    ("admin_bohan",     "admin@bohanhyland.ie",     "admin"),
    ("assistant_bohan", "assistant@bohanhyland.ie", "assistant"),
    ("pm_bohan",        "pm@bohanhyland.ie",        "property_manager"),
]

# Contractor users -> each attached to its own company (names EXACTLY as in DB)
CONTRACTOR_COMPANIES = {
    "Blueflow Plumbing Ltd":          ("ctr_blueflow",       "liam@blueflowplumbing.ie"),
    "SparkRight Electrical Ltd":      ("ctr_sparkrightelect", "aoife@sparkrightelectrical.ie"),
    "Oak & Beam Carpentry":           ("ctr_oakbeam",        "conor@oakandbeam.ie"),
    "PrimeCoat Painters":             ("ctr_primecoat",      "maria@primecoat.ie"),
    "BrightSweep Cleaning Services":  ("ctr_brightsweep",    "daniel@brightsweep.ie"),
    "PolarAir Mechanical":            ("ctr_polarair",       "niamh@polarair.ie"),
    "GreenScape Grounds":             ("ctr_greenscape",     "patrick@greenscape.ie"),
    "ShieldGuard Pest Control":       ("ctr_shieldguard",    "emma@shieldguard.ie"),
    "Sentinel Security Services":     ("ctr_sentinelsec",    "brian@sentinelsecurity.ie"),
    "Vertex Build Ltd":               ("ctr_vertexbuild",    "sarah@vertexbuild.ie"),
    "FlexHand Facilities":            ("ctr_flexhand",       "mark@flexhand.ie"),
}

DEFAULT_PASSWORD = "ChangeMe!2025"  # change after login

def upsert_user(username, email, role, company):
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    user.email = email
    user.role = role
    user.company = company
    if hasattr(user, "is_staff"):
        user.is_staff = (role == "admin")
    if hasattr(user, "is_superuser"):
        user.is_superuser = False
    user.set_password(DEFAULT_PASSWORD)
    user.is_active = True
    user.save()
    return created

@transaction.atomic
def run():
    # HQ company for non-contractor roles
    try:
        hq = Company.objects.get(name=HQ_COMPANY)
    except Company.DoesNotExist:
        raise SystemExit(f"Company '{HQ_COMPANY}' not found. Create it first.")

    # Admin / Assistant / Property Manager
    for username, email, role in NON_CONTRACTOR_USERS:
        created = upsert_user(username, email, role, hq)
        print(("CREATED" if created else "UPDATED"), username, "->", role, "@", hq.name)

    # One contractor per company
    for company_name, (username, email) in CONTRACTOR_COMPANIES.items():
        try:
            c = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            print(f"SKIP {username}: company '{company_name}' not found.")
            continue
        created = upsert_user(username, email, "contractor", c)
        print(("CREATED" if created else "UPDATED"), username, "-> contractor @", c.name)

# Execute when this file is exec()'d by the Django shell
run()
