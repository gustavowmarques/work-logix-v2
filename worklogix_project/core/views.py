# core/views.py
from django.shortcuts import render, redirect
from .decorators import property_manager_required, contractor_required, assistant_required, admin_required

@admin_required
def admin_dashboard(request):
    return render(request, 'core/dashboards/admin_dashboard.html')

@property_manager_required
def pm_dashboard(request):
    return render(request, 'core/dashboards/pm_dashboard.html')

@contractor_required
def contractor_dashboard(request):
    return render(request, 'core/dashboards/contractor_dashboard.html')

@assistant_required
def assistant_dashboard(request):
    return render(request, 'core/dashboards/assistant_dashboard.html')

def redirect_after_login(request):
    """
    Redirects the user to the appropriate dashboard based on their role.
    """
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'pm':
        return redirect('pm_dashboard')
    elif user.role == 'contractor':
        return redirect('contractor_dashboard')
    elif user.role == 'assistant':
        return redirect('assistant_dashboard')
    else:
        return redirect('admin:index')  # fallback