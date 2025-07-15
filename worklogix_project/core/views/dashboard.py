from django.shortcuts import render
from core.decorators import property_manager_required, contractor_required, assistant_required
from core.models import Company, WorkOrder


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
    Contractor dashboard showing company info and assigned work orders.
    """
    my_company = request.user.company
    my_assigned_orders = WorkOrder.objects.filter(
        assigned_contractor=my_company
    ).exclude(status='completed')

    return render(request, 'core/dashboards/contractor_dashboard.html', {
        'my_company': my_company,
        'my_assigned_orders': my_assigned_orders,
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
