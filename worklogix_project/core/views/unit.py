from django.shortcuts import render, redirect
from django.contrib import messages
from django.forms import formset_factory
from django.core.paginator import Paginator

from core.forms import UnitForm
from core.models import Unit, Client

import requests
from django.conf import settings



# Define a formset factory for handling multiple UnitForm instances
UnitFormSet = formset_factory(UnitForm, extra=0)

# Dummy address lookup function — to be replaced with a real Eircode API integration
def fake_address_lookup(eircode):
    return {
        'street': '1 Main Street',
        'city': 'Dublin',
        'county': 'Dublin'
    }

def review_units(request):
    client_id = request.session.get('client_id')
    eircode = request.session.get('default_eircode', '')

    if not client_id:
        messages.error(request, "Session expired. Please re-create the client.")
        return redirect('create_client')

    address_data = google_address_lookup(eircode) if eircode else {'street': '', 'city': '', 'county': ''}

    # Get contact info from session
    contact_name = request.session.get('unit_contact_name', '')
    contact_email = request.session.get('unit_contact_email', '')
    contact_number = request.session.get('unit_contact_number', '')

    print("Contact defaults from session:")
    print("Name:", contact_name)
    print("Number:", contact_number)
    print("Email:", contact_email)

    if request.method == 'GET':
        initial = []

        def generate(type_key, count, prefix):
            for i in range(count):
                initial.append({
                    'unit_number': f"{prefix} {i+1}",
                    'unit_type': type_key,
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

        # Preview first unit
        if initial:
            print("Sample unit:", initial[0])

        paginator = Paginator(initial, 20)
        page_number = request.GET.get('page') or 1
        page_obj = paginator.get_page(page_number)
        formset = UnitFormSet(initial=page_obj.object_list)
        print("Sample formset initial contact name:", page_obj.object_list[0].get('unit_contact_name'))


        return render(request, 'core/admin/review_units.html', {
            'formset': formset,
            'page_obj': page_obj
        })

    else:
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
            'page_obj': None
        })


def google_address_lookup(eircode):
    """
    Calls Google Maps Geocoding API to get address details from an Eircode.
    Handles multiple possible address component types to improve accuracy.
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
            components = result["address_components"]
            formatted = result.get("formatted_address", "")

            print("Address components:", components)
            print("Formatted:", formatted)

            street = city = county = ""

            for comp in components:
                if "route" in comp["types"] or "premise" in comp["types"]:
                    street = comp["long_name"]
                elif "locality" in comp["types"] and not city:
                    city = comp["long_name"]

                elif "locality" in comp["types"]:
                    city = comp["long_name"]
                elif "administrative_area_level_1" in comp["types"]:
                    county = comp["long_name"]

            # fallback logic
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