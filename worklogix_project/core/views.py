# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .decorators import property_manager_required, contractor_required, assistant_required, admin_required
from .models import Client, Company

@admin_required
def admin_dashboard(request):
    """
    View for Admin dashboard.
    Only accessible by users with the 'admin' role.
    Admins can see all companies by type
    """
    contractors = Company.objects.filter(is_contractor=True)
    clients = Company.objects.filter(is_client=True)
    managers = Company.objects.filter(is_property_manager=True)
    return render(request, 'core/dashboards/admin_dashboard.html', {
        'contractors': contractors,
        'clients': clients,
        'managers': managers,
    })

@property_manager_required
def pm_dashboard(request):
    """
    Property Manager dashboard view.
    Property Managers can see all assigned clients and contractors
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
    View for Contractor dashboard.
    Only accessible by users with the 'contractor' role.
    Contractors may only see their own company info for now
    """
    my_company = request.user.company
    return render(request, 'core/dashboards/contractor_dashboard.html', {
        'my_company': my_company,
    })

@assistant_required
def assistant_dashboard(request):
    """
    View for Assistant dashboard.
    Only accessible by users with the 'assistant' role.
    Assistants may see a read-only list of clients/contractors
    """
    clients = Company.objects.filter(is_client=True)
    contractors = Company.objects.filter(is_contractor=True)
    return render(request, 'core/dashboards/assistant_dashboard.html', {
        'clients': clients,
        'contractors': contractors,
    })

def redirect_after_login(request):
    """
    Redirects the user to the appropriate dashboard based on their role.
    Assistants may see a read-only list of clients/contractors
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
    
def custom_login(request):
    """
    Handles user login and redirects to the appropriate dashboard.
    """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('redirect_after_login')  # Defined already
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'core/login.html')

class CustomLoginView(LoginView):
    """
    Custom login view that uses Django’s built-in auth system
    but redirects using LOGIN_REDIRECT_URL.
    """
    template_name = 'core/login.html'