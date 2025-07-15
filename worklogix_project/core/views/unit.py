from django.shortcuts import render, redirect
from django.contrib import messages
from core.forms import UnitForm
from core.models import Unit, Client

# Placeholder function — later replace with real Eircode lookup
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

    address_data = fake_address_lookup(eircode) if eircode else {'street': '', 'city': '', 'county': ''}

    if request.method == 'GET':
        initial = []

        def generate(type_key, count, prefix):
            for i in range(count):
                initial.append({
                    'unit_number': f"{prefix} {i+1}",
                    'unit_type': type_key,
                    'eircode': eircode,
                    **address_data
                })

        generate('apartment', request.session.get('num_apartments', 0), 'Apartment')
        generate('duplex', request.session.get('num_duplexes', 0), 'Duplex')
        generate('house', request.session.get('num_houses', 0), 'House')
        generate('commercial', request.session.get('num_commercial_units', 0), 'Commercial')

        formset = UnitFormSet(initial=initial)

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
                    county=form.cleaned_data['county']
                )
            messages.success(request, "Units created successfully.")
            return redirect('manage_clients')

    return render(request, 'core/admin/review_units.html', {'formset': formset})
