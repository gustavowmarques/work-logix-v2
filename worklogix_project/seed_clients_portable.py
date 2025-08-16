import random
from django.core.exceptions import FieldDoesNotExist
from core.models import Company, Client  # adjust app label if needed

HQ_COMPANY = "Bohan Hyland Holdings Limited"

try:
    hq = Company.objects.get(name=HQ_COMPANY)
except Company.DoesNotExist:
    raise SystemExit(f"Company '{HQ_COMPANY}' not found. Create it first.")

def has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return False

def set_first_existing(d: dict, model, value, *candidate_names) -> str | None:
    """
    Add the first field name that exists on `model` to dict `d` with `value`.
    Returns the field name used, or None if none exist.
    """
    for nm in candidate_names:
        if has_field(model, nm):
            d[nm] = value
            return nm
    return None

# --- sample data -----------------------------------------------------------
random.seed(42)
rows = [
    {"name": "Riverpark Apartments",    "address": "Riverpark, Walkinstown, Dublin 12",    "eircode": "D12 RP01"},
    {"name": "Harbour View Residences", "address": "Seafront Road, Bray, Co. Wicklow",     "eircode": "A98 HV32"},
    {"name": "Willow Court",            "address": "Old Bawn, Tallaght, Dublin 24",        "eircode": "D24 WC11"},
    {"name": "Oakfield Estate",         "address": "Forest Rd, Swords, Co. Dublin",        "eircode": "K67 OF20"},
    {"name": "Liffey Quay",             "address": "Thomas Street, Dublin 8",              "eircode": "D08 LQ44"},
    {"name": "Sycamore Grove",          "address": "Esker, Lucan, Co. Dublin",             "eircode": "K78 SG09"},
    {"name": "Cedar Park",              "address": "Crosshaven Rd, Carrigaline, Co. Cork", "eircode": "P43 CP12"},
    {"name": "Granite Square",          "address": "Dock Rd, Galway",                      "eircode": "H91 GS55"},
    {"name": "Elm Terrace",             "address": "Castlecomer Rd, Kilkenny",             "eircode": "R95 ET88"},
    {"name": "The Courtyard",           "address": "Little Island, Co. Cork",              "eircode": "T45 TC33"},
]

first_names = ["Laura", "Tomás", "Niamh", "Conor", "Aoife", "Patrick", "Emma", "Brian", "Sarah", "Daniel"]
last_names  = ["Kelly", "Lynch", "Fitzpatrick", "Walsh", "Byrne", "Nolan", "Dwyer", "Keane", "McGrath", "Murphy"]
areas       = ["1", "21", "61", "91", "56", "71"]  # loose Irish-looking dialing codes

def phone_number():
    return f"+353 {random.choice(areas)} {random.randint(100,999)} {random.randint(1000,9999)}"

created = 0
updated = 0

# Decide which field names actually exist on your Client model
count_map = {
    "apartments":  ("num_apartments", "apartments", "apartment_count", "num_apartment_units"),
    "duplexes":    ("num_duplexes", "duplexes", "duplex_count"),
    "houses":      ("num_houses", "houses", "house_count"),
    "commercials": ("num_commercial_units", "commercial_units", "shops", "retail_units"),
}
contact_map = {
    "name":   ("unit_contact_name", "contact_name", "unit_manager_name"),
    "phone":  ("unit_contact_number", "contact_number", "unit_phone", "phone"),
    "email":  ("unit_contact_email", "contact_email", "unit_email", "email"),
}
eircode_candidates = ("shared_eircode", "eircode", "post_code", "postcode", "zip_code")

for i, row in enumerate(rows):
    # random counts
    num_apts  = random.randint(10, 180)
    num_dups  = random.randint(0, 25)
    num_houses = random.randint(0, 120)
    num_comm  = random.randint(0, 18)

    # contact details
    fn = first_names[i % len(first_names)]
    ln = last_names[i % len(last_names)]
    contact_name  = f"{fn} {ln}"
    contact_phone = phone_number()
    domain = row["name"].lower().replace("&", "and").replace(" ", "").replace("-", "")
    contact_email = f"{fn.lower()}.{ln.lower()}@{domain}.ie"

    # minimal required fields
    defaults = {}
    defaults["address"] = row["address"]

    # set eircode if your model has any of these names
    set_first_existing(defaults, Client, row["eircode"], *eircode_candidates)

    # set counts only if such fields exist on your model
    set_first_existing(defaults, Client, num_apts,  *count_map["apartments"])
    set_first_existing(defaults, Client, num_dups,  *count_map["duplexes"])
    set_first_existing(defaults, Client, num_houses,*count_map["houses"])
    set_first_existing(defaults, Client, num_comm,  *count_map["commercials"])

    # set contact fields if present
    set_first_existing(defaults, Client, contact_name,  *contact_map["name"])
    set_first_existing(defaults, Client, contact_phone, *contact_map["phone"])
    set_first_existing(defaults, Client, contact_email, *contact_map["email"])

    # If your FK isn't called 'company', change it here
    defaults["company"] = hq

    # Use (name, company) as identity if both exist; otherwise just name
    lookup = {"name": row["name"]}
    if has_field(Client, "company"):
        lookup["company"] = hq

    obj, was_created = Client.objects.update_or_create(**lookup, defaults=defaults)
    if was_created:
        created += 1
        print("CREATED:", obj.name)
    else:
        updated += 1
        print("UPDATED:", obj.name)

print(f"\nDone. {created} created, {updated} updated, all under '{hq.name}'.")
