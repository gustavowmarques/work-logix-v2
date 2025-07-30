from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models.work_order import WorkOrder

@login_required
def admin_dashboard(request):
    return render(request, 'core/admin/admin_dashboard.html')

@login_required
def pm_dashboard(request):
    return render(request, 'core/property_manager/pm_dashboard.html')

@login_required
def assistant_dashboard(request):
    return render(request, 'core/assistant/assistant_dashboard.html')

@login_required
def contractor_dashboard(request):
    contractor_company = getattr(request.user, 'company', None)

    if not contractor_company:
        return redirect('login')

    # Filter relevant work orders
    work_orders = WorkOrder.objects.filter(
        preferred_contractor=contractor_company,
        assigned_contractor__isnull=True,
        rejected_by_first=False,
        returned_to_creator=False
    )

    return render(request, 'core/contractor/contractor_dashboard.html', {
        'my_company': contractor_company,
        'my_assigned_orders': work_orders,
    })
