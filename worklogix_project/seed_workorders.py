# seed_workorders.py
from datetime import timedelta
import random
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from core.models import BusinessType, Company, Client, Unit, WorkOrder

User = get_user_model()

# Map Business Type -> preferred contractor company name
BT_TO_CONTRACTOR = {
    "Plumbing": "Blueflow Plumbing Ltd",
    "Electrical": "SparkRight Electrical Ltd",
    "Carpentry": "Oak & Beam Carpentry",
    "Painting": "PrimeCoat Painters",
    "Cleaning": "BrightSweep Cleaning Services",
    "HVAC": "PolarAir Mechanical",
    "Landscaping": "GreenScape Grounds",
    "Pest Control": "ShieldGuard Pest Control",
    "Security": "Sentinel Security Services",
    "General Contractor": "Vertex Build Ltd",
    "Other": "FlexHand Facilities",
}

def field_names(model):
    # concrete DB fields only
    return {f.name for f in model._meta.fields}

def choose_priority():
    """Return a priority value that matches your model choices if present."""
    try:
        pf = WorkOrder._meta.get_field("priority")
        choices = [c[0] for c in (pf.choices or ())]
        if choices:
            # try to match common spellings irrespective of case
            for want in ("medium", "MEDIUM", "Medium"):
                if want in choices:
                    return want
            return choices[0]
    except Exception:
        pass
    return "medium"

def status_value():
    try:
        sf = WorkOrder._meta.get_field("status")
        choices = [c[0] for c in (sf.choices or ())]
        if choices:
            for want in ("NEW", "new", "New"):
                if want in choices:
                    return want
            return choices[0]
    except Exception:
        pass
    return "NEW"

def run():
    fset = field_names(WorkOrder)

    # Which bool field to use for common area?
    common_area_field = "is_common_area" if "is_common_area" in fset else (
        "common_area" if "common_area" in fset else None
    )

    creator = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not creator:
        raise SystemExit("No users exist; create at least one user.")

    bt_by_name = {bt.name: bt for bt in BusinessType.objects.all()}
    if not bt_by_name:
        raise SystemExit("No Business Types found; seed those first.")

    clients = list(Client.objects.all())
    if not clients:
        raise SystemExit("No Clients found; create/seed some clients first.")

    today = timezone.now().date()
    prio = choose_priority()
    st = status_value()

    created = updated = errors = 0
    print(f"Using creator: {creator.username}")

    for client in clients:
        # pick a business type (slightly bias to General Contractor)
        names = list(bt_by_name.keys())
        if "General Contractor" in names:
            names += ["General Contractor"]
        bt_name = random.choice(names)
        bt = bt_by_name[bt_name]

        preferred = Company.objects.filter(
            name=BT_TO_CONTRACTOR.get(bt_name, "")
        ).first()

        # 30% common area, or if the client has no units
        units_qs = Unit.objects.filter(client=client)
        unit = None
        make_common = (not units_qs.exists()) or (random.random() < 0.30)
        if not make_common:
            unit = units_qs.order_by("?").first()

        title = f"{bt_name} job at {client.name}"
        desc = f"Auto-seeded work order for {client.name}. Generated for testing."
        due_date = today + timedelta(days=random.randint(3, 14))

        # Build kwargs only with fields that actually exist
        kwargs = {
            "title": title,
            "description": desc,
            "status": st,
            "business_type": bt,
            "client": client,
            "due_date": due_date,
            "priority": prio,
            "created_by": creator,
        }
        if "updated_by" in fset:
            kwargs["updated_by"] = creator
        if "unit" in fset:
            kwargs["unit"] = None if (make_common and unit is not None) else unit
        if "preferred_contractor" in fset:
            kwargs["preferred_contractor"] = preferred
        if "second_contractor" in fset:
            # 40% chance of a second contractor
            kwargs["second_contractor"] = (
                Company.objects.filter(is_contractor=True)
                .exclude(id=getattr(preferred, "id", None))
                .order_by("?")
                .first()
                if random.random() < 0.4 else None
            )
        if "company" in fset:
            # if WorkOrder has a company FK, set to the client's PM company
            kwargs["company"] = getattr(client, "company", None)
        if common_area_field:
            kwargs[common_area_field] = bool(make_common)

        try:
            with transaction.atomic():
                wo, was_created = WorkOrder.objects.update_or_create(
                    client=client, title=title, defaults=kwargs
                )
            created += int(was_created)
            updated += int(not was_created)
            where = "Common Area" if (common_area_field and kwargs.get(common_area_field)) else (getattr(unit, "name", "—"))
            print(("CREATED" if was_created else "UPDATED"),
                  f"{wo.id} | {client.name} | {bt_name} | {where}")
        except Exception as ex:
            errors += 1
            print("ERROR:", client.name, "|", bt_name, "->", ex)

    print(f"\nDone. Created: {created}, Updated: {updated}, Errors: {errors}")
