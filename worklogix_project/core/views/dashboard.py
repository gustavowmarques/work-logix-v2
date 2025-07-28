from django.shortcuts import render
from core.decorators import property_manager_required, contractor_required, assistant_required
from core.models import Company, WorkOrder
from django.db.models import Q


@property_manager_required
def pm_dashboard(request):
    """
    Property Manager dashboard with linked clients and contractors.
    """
    contractors = Company.objects.filter(is_contractor=True)
    clients = Company.objects.filter(is_client=True)
    return render(request, 'core/dashboards/pm_dashboard.html', {
        'contractors': contractors,
        'clients': clients,
    })


@contractor_required
def contractor_dashboard(request):
    """
    Contractor dashboard showing company info and all related work orders.
    Displays:
    - New work orders where the company is preferred or second contractor
    - Assigned work orders where the company is actively working on it
    """
    contractor_company = request.user.company

    # All work orders where the company is either preferred or second
    related_work_orders = WorkOrder.objects.filter(
        Q(preferred_contractor=contractor_company) |
        Q(second_contractor=contractor_company)
    ).distinct()

    return render(request, 'core/dashboards/contractor_dashboard.html',{
        'my_company': contractor_company,
        'my_assigned_orders': related_work_orders,
    })


@assistant_required
def assistant_dashboard(request):
    """
    Assistant dashboard (read-only view of clients/contractors).
    """
    clients = Company.objects.filter(is_client=True)
    contractors = Company.objects.filter(is_contractor=True)
    return render(request, 'core/dashboards/assistant_dashboard.html', {
        'clients': clients,
        'contractors': contractors,
    })
