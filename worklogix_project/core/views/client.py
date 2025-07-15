# Decorators and Django utilities
from core.decorators import admin_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Models and forms
from core.models import Client, Company, CustomUser, Unit, UnitGroup
from core.forms import ClientCreationForm

@admin_required
def create_client(request):
    """
    Admin view to create a new Client and optionally pre-generate UnitGroup data.
    Stores initial unit values in session for the next step.
    """
    form = ClientCreationForm(request.POST or None)

    if form.is_valid():
        # 1. Save the client instance
        client = form.save()

        # 2. Store unit creation info in the session for use in the next step
        request.session['client_id'] = client.id
        request.session['default_eircode'] = form.cleaned_data['default_eircode']
        request.session['num_apartments'] = form.cleaned_data['num_apartments']
        request.session['num_duplexes'] = form.cleaned_data['num_duplexes']
        request.session['num_houses'] = form.cleaned_data['num_houses']
        request.session['num_commercial_units'] = form.cleaned_data['num_commercial_units']

        # 3. OPTIONAL: create UnitGroup for grouped tracking (can skip if not needed)
        UnitGroup.objects.create(
            client=client,
            num_apartments=form.cleaned_data['num_apartments'],
            num_duplexes=form.cleaned_data['num_duplexes'],
            num_houses=form.cleaned_data['num_houses'],
            num_commercial_units=form.cleaned_data['num_commercial_units'],
            created_by=request.user
        )

        # 4. Redirect to unit review/confirmation page
        messages.info(request, "Client created. Please review and confirm the units.")
        return redirect('review_units')  # This should match your URL name for the next view

    # On GET or invalid POST, render the form again
    return render(request, 'core/create_client.html', {'form': form})

@admin_required
def manage_clients(request):
    clients = Client.objects.select_related('company').all()
    return render(request, 'core/admin/manage_clients.html', {'clients': clients})

@admin_required
def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    form = ClientCreationForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, "Client updated successfully.")
        return redirect('manage_clients')
    return render(request, 'core/admin/edit_client.html', {'form': form})

@admin_required
def view_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'core/admin/view_client.html', {'client': client})

@admin_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    messages.success(request, "Client deleted.")
    return redirect('manage_clients')