from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from core.models.work_order import WorkOrder
from core.models import CustomUser, Company, Client

# --- Admin Dashboard ---
@login_required
def admin_dashboard(request):
    # Work Orders
    open_work_count = WorkOrder.objects.filter(status__in=['new', 'assigned']).count()
    in_progress_count = WorkOrder.objects.filter(status='accepted').count()
    completed_work_count = WorkOrder.objects.filter(status='completed').count()

    # Users
    users = CustomUser.objects.all()

    # Companies
    managers = Company.objects.filter(is_property_manager=True) 
    contractors = Company.objects.filter(is_contractor=True)

    # Clients
    clients = Client.objects.all()

    return render(request, 'core/admin/admin_dashboard.html', {
        'open_work_count': open_work_count,
        'in_progress_count': in_progress_count,
        'completed_work_count': completed_work_count,
        'users': users,
        'managers': managers,
        'contractors': contractors,
        'clients': clients,
    })


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


