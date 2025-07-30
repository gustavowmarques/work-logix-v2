from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from core.decorators import contractor_required
from core.models import WorkOrder, Unit, Company
from core.forms import WorkOrderForm


# -------------------------------
# Create Work Order (PM/Admin/Assistant)
# -------------------------------
@login_required
def create_work_order(request):
    if request.user.role not in ['admin', 'property_manager', 'assistant']:
        return HttpResponseForbidden("You are not allowed to create work orders.")
    
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.created_by = request.user
            work_order.status = 'new'
            work_order.assigned_contractor = work_order.preferred_contractor  # initial assignment
            work_order.save()
            messages.success(request, "Work order created successfully.")
            return redirect('redirect_after_login')
    else:
        form = WorkOrderForm()

    contractors = Company.objects.filter(is_contractor=True)
    form.fields['preferred_contractor'].queryset = contractors
    form.fields['second_contractor'].queryset = contractors

    return render(request, 'core/create_work_order.html', {'form': form})


# -------------------------------
# PM/Assistant views their own created work orders
# -------------------------------
@login_required
def my_work_orders(request):
    user = request.user

    if user.role == 'property_manager':
        work_orders = WorkOrder.objects.filter(created_by=user)

    elif user.role == 'assistant':
        work_orders = WorkOrder.objects.filter(created_by=user)

    elif user.role == 'contractor':
        work_orders = WorkOrder.objects.filter(assigned_contractor=user)

    else:
        return HttpResponseForbidden("Not allowed")

    return render(request, 'core/my_work_orders.html', {'work_orders': work_orders})



# -------------------------------
# Contractor accepts a work order
# -------------------------------
@contractor_required
def accept_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)

    if request.user.company != work_order.assigned_contractor:
        return HttpResponseForbidden("Not authorized to accept this work order.")

    work_order.status = 'accepted'
    work_order.save()
    messages.success(request, "You have accepted the work order.")
    return redirect('my_contractor_orders')


# -------------------------------
# Contractor rejects a work order
# -------------------------------
@contractor_required
def reject_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)

    if request.user.company != work_order.assigned_contractor:
        return HttpResponseForbidden("Not authorized to reject this work order.")

    # Reassignment logic
    if work_order.assigned_contractor == work_order.preferred_contractor:
        if work_order.second_contractor:
            work_order.assigned_contractor = work_order.second_contractor
            work_order.status = 'assigned'
        else:
            work_order.assigned_contractor = None
            work_order.status = 'returned'
    elif work_order.assigned_contractor == work_order.second_contractor:
        work_order.assigned_contractor = None
        work_order.status = 'returned'

    work_order.save()
    messages.success(request, "You have rejected the work order.")
    return redirect('my_contractor_orders')


# -------------------------------
# AJAX: Load units for selected client
# -------------------------------
@login_required
def load_units_for_client(request):
    client_id = request.GET.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Missing client ID'}, status=400)
    
    units = Unit.objects.filter(client_id=client_id).order_by('name')
    unit_list = [{'id': unit.id, 'name': unit.name} for unit in units]
    return JsonResponse({'units': unit_list})


# -------------------------------
# View details of a specific work order
# -------------------------------
@login_required
def view_work_order_detail(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)

    if request.user.company not in [work_order.preferred_contractor, work_order.second_contractor]:
        return redirect('contractor_dashboard')  # Prevent unauthorized view

    return render(request, 'contractor/work_order_detail.html', {
        'order': work_order
    })


# -------------------------------
# Contractor: View assigned work orders
# -------------------------------
@login_required
def my_contractor_orders(request):
    """
    Show all work orders where the current user's company is either preferred or second contractor
    and the order is not yet completed.
    """
    contractor = request.user.company

    assigned_orders = WorkOrder.objects.filter(
        Q(preferred_contractor=contractor) | Q(second_contractor=contractor),
        status__in=['new', 'assigned', 'accepted']
    ).order_by('-created_at')

    return render(request, 'contractor/my_work_orders.html', {
        'my_assigned_orders': assigned_orders
    })
