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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import WorkOrder  # adjust import as needed

@login_required
def contractor_dashboard(request):
    # Defensive check: Ensure user is linked to a company
    if not request.user.company:
        messages.error(request, "Your user account is not linked to a company.")
        return redirect('dashboard_home')  # 🔁 Replace with your actual safe fallback route name

    # Reference to the user's company
    contractor = request.user.company

    # Optional: If the company has a nested 'company' relationship (e.g., a profile model)
    company = contractor.company if hasattr(contractor, 'company') else contractor

    # Get all active work orders assigned to this contractor (not completed)
    active_work_orders = WorkOrder.objects.filter(
        assigned_contractor=contractor
    ).exclude(status='completed').order_by('due_date')

    # Render contractor dashboard with company info and relevant work orders
    return render(request, 'core/contractor/contractor_dashboard.html', {
        'company': company,
        'work_orders': active_work_orders
    })

