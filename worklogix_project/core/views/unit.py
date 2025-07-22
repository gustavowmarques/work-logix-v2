from django.shortcuts import render, redirect
from django.contrib import messages
from django.forms import formset_factory
from core.forms import UnitForm
from core.models import Unit, Client
from django.conf import settings
import requests

# Create a formset for multiple UnitForm entries
UnitFormSet = formset_factory(UnitForm, extra=0)

def review_units(request):
    """
    Handles the unit review and confirmation step.
    GET: Prepares initial unit data based on session variables.
    POST: Saves all submitted units to the database.
    """
    # Session validation
    client_id = request.session.get('client_id')
    eircode = request.session.get('default_eircode', '')
    if not client_id:
        messages.error(request, "Session expired. Please re-create the client.")
        return redirect('create_client')

    # Address resolution
    address_data = google_address_lookup(eircode) if eircode else {'street': '', 'city': '', 'county': ''}

    # Contact info from session
    contact_name = request.session.get('unit_contact_name', '')
    contact_email = request.session.get('unit_contact_email', '')
    contact_number = request.session.get('unit_contact_number', '')

    print("Contact defaults from session:")
    print("Name:", contact_name)
    print("Number:", contact_number)
    print("Email:", contact_email)

    if request.method == 'GET':
        # Build initial formset data
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

        if initial:
            print("Sample unit:", initial[0])

        # Render all units at once (pagination removed)
        formset = UnitFormSet(initial=initial)

        return render(request, 'core/admin/review_units.html', {
            'formset': formset,
            'page_obj': None  # no pagination used
        })

    else:  # POST
        formset = UnitFormSet(request.POST)

        if formset.is_valid():
            client = Client.objects.get(id=client_id)
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
        else:
            print("Formset errors:", formset.errors)

        return render(request, 'core/admin/review_units.html', {
            'formset': formset,
            'page_obj': None  # keep template logic clean
        })

def google_address_lookup(eircode):
    """
    Uses Google Maps Geocoding API to fetch address details from Eircode.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": eircode,
        "key": settings.GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get("status") == "OK":
            result = data["results"][0]
            components = result.get("address_components", [])
            formatted = result.get("formatted_address", "")

            print("Address components:", components)
            print("Formatted:", formatted)

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
                if len(parts) > 1:
                    street = parts[0].strip()

            return {
                "street": street or "Unknown Street",
                "city": city or "Unknown City",
                "county": county or "Unknown County"
            }

    except Exception as e:
        print("Geocoding failed:", e)

    return {'street': '', 'city': '', 'county': ''}
