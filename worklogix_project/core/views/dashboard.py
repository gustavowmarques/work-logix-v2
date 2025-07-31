from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q

from core.models.work_order import WorkOrder

# --- Admin Dashboard ---
@login_required
def admin_dashboard(request):
    return render(request, 'core/admin/admin_dashboard.html')


# --- Property Manager Dashboard ---
@login_required
def pm_dashboard(request):
    return render(request, 'core/property_manager/pm_dashboard.html')


# --- Assistant Dashboard ---
@login_required
def assistant_dashboard(request):
    return render(request, 'core/assistant/assistant_dashboard.html')


# --- Contractor Dashboard ---
@login_required
def contractor_dashboard(request):
    contractor = request.user.company
    print("Contractor ID:", contractor.id)
    print("Contractor Name:", contractor.name)

    active_work_orders = WorkOrder.objects.filter(
        Q(status='new', preferred_contractor=contractor) |
        Q(status='new', second_contractor=contractor) |
        Q(status='accepted', assigned_contractor=contractor)
    ).exclude(status='completed').order_by('due_date')

    print("Active Work Orders:", active_work_orders)

    return render(request, 'core/contractor/contractor_dashboard.html', {
        'company': contractor,
        'work_orders': active_work_orders
    })


