from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import formset_factory, modelformset_factory
from django.conf import settings
import requests

from core.forms import UnitForm, UnitGeneratorForm
from core.models import Unit, Client
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required




# Create a formset for multiple units
UnitFormSet = formset_factory(UnitForm, extra=0)


def review_units(request):
    """
    Review and confirm bulk unit creation via formset.
    Uses session data to prepopulate unit entries.
    """
    client_id = request.session.get('client_id')
    eircode = request.session.get('default_eircode', '')

    if not client_id:
        messages.error(request, "Session expired. Please re-create the client.")
        return redirect('create_client')

    # Lookup address data from Google API (optional)
    address_data = google_address_lookup(eircode) if eircode else {'street': '', 'city': '', 'county': ''}

    # Default contact info from session
    contact_name = request.session.get('unit_contact_name', '')
    contact_email = request.session.get('unit_contact_email', '')
    contact_number = request.session.get('unit_contact_number', '')

    if request.method == 'GET':
        initial = []

        def generate(unit_type, count, prefix):
            for i in range(count):
                initial.append({
                    'unit_number': f"{prefix} {i + 1}",
                    'unit_type': unit_type,
                    'eircode': eircode,
                    'street': address_data.get('street', ''),
                    'city': address_data.get('city', ''),
                    'county': address_data.get('county', ''),
                    'unit_contact_name': contact_name,
                    'unit_contact_email': contact_email,
                    'unit_contact_number': contact_number,
                })

        generate('apartment', request.session.get('num_apartments', 0), 'Apartment')
        generate('duplex', request.session.get('num_duplexes', 0), 'Duplex')
        generate('house', request.session.get('num_houses', 0), 'House')
        generate('commercial', request.session.get('num_commercial_units', 0), 'Commercial')

        formset = UnitFormSet(initial=initial)
        return render(request, 'core/admin/review_units.html', {'formset': formset})

    else:
        formset = UnitFormSet(request.POST)
        if formset.is_valid():
            client = get_object_or_404(Client, id=client_id)
            for form in formset:
                Unit.objects.create(
                    client=client,
                    name=form.cleaned_data['unit_number'],
                    unit_type=form.cleaned_data['unit_type'],
                    eircode=form.cleaned_data['eircode'],
                    street=form.cleaned_data['street'],
                    city=form.cleaned_data['city'],
                    county=form.cleaned_data['county'],
                    unit_contact_name=form.cleaned_data['unit_contact_name'],
                    unit_contact_email=form.cleaned_data['unit_contact_email'],
                    unit_contact_number=form.cleaned_data['unit_contact_number'],
                )
            messages.success(request, "Units created successfully.")
            return redirect('manage_clients')

        return render(request, 'core/admin/review_units.html', {'formset': formset})


def unit_generator(request):
    """
    Bulk unit generator: create sequentially numbered units for a selected client.
    Accepts ?client_id= to prefill form.
    """
    client_id = request.GET.get('client_id')
    initial = {}

    if client_id:
        try:
            client = Client.objects.get(id=client_id)
            initial['client'] = client
        except Client.DoesNotExist:
            messages.warning(request, "Client not found. Please select a valid client.")

    if request.method == 'POST':
        form = UnitGeneratorForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            prefix = form.cleaned_data['prefix']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']

            existing_names = set(Unit.objects.filter(client=client).values_list('name', flat=True))
            created = 0
            for i in range(start, end + 1):
                name = f"{prefix} {i}"
                if name not in existing_names:
                    Unit.objects.create(client=client, name=name)
                    created += 1
                else:
                    messages.warning(request, f"Skipped duplicate unit: {name}")

            messages.success(request, f"{created} units created for {client.name}.")
            return redirect('manage_clients')
    else:
        form = UnitGeneratorForm(initial=initial)

    return render(request, 'core/admin/unit_generator.html', {'form': form})

@login_required
def delete_unit(request, unit_id):
    """
    Deletes a single unit by ID and redirects back to the review_units page.
    """
    unit = get_object_or_404(Unit, id=unit_id)
    client_name = unit.client.name

    if request.method == 'POST':
        unit.delete()
        messages.success(request, f"Unit '{unit.name}' deleted from {client_name}.")
    
    return redirect('review_units')

@login_required
def client_units(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    units = client.unit_set.all()

    UnitInlineFormSet = modelformset_factory(Unit, fields=['name', 'unit_type', 'eircode', 'street', 'city', 'county', 'unit_contact_name', 'unit_contact_email', 'unit_contact_number'], extra=1, can_delete=True)

    if request.method == 'POST':
        formset = UnitInlineFormSet(request.POST, queryset=units)
        if formset.is_valid():
            instances = formset.save(commit=False)

            existing_names = set(Unit.objects.filter(client=client).values_list('name', flat=True))

            for unit in instances:
                if unit.name in existing_names and unit.id is None:
                    messages.warning(request, f"Duplicate unit: {unit.name}")
                    continue
                unit.client = client
                unit.save()

            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(request, "Units updated successfully.")
            return redirect('manage_clients')

    else:
        formset = UnitInlineFormSet(queryset=units)

    return render(request, 'core/admin/client_units.html', {
        'client': client,
        'formset': formset
    })


def google_address_lookup(eircode):
    """
    Uses Google Maps API to return address components from Eircode.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": eircode, "key": settings.GOOGLE_MAPS_API_KEY}

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data.get("status") == "OK":
            result = data["results"][0]
            components = result.get("address_components", [])
            formatted = result.get("formatted_address", "")
            street = city = county = ""

            for comp in components:
                if "route" in comp["types"] or "premise" in comp["types"]:
                    street = comp["long_name"]
                elif "locality" in comp["types"] and not city:
                    city = comp["long_name"]
                elif "administrative_area_level_1" in comp["types"]:
                    county = comp["long_name"]

            if not street and formatted:
                parts = formatted.split(",")
                if parts:
                    street = parts[0].strip()

            return {
                "street": street or "Unknown Street",
                "city": city or "Unknown City",
                "county": county or "Unknown County"
            }

    except Exception as e:
        print("Geocoding failed:", e)

    return {'street': '', 'city': '', 'county': ''}
