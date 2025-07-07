from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .decorators import property_manager_required, contractor_required, assistant_required, admin_required
from .models import Client, Company, WorkOrder
from .forms import CustomUserCreationForm, CompanyCreationForm, ClientCreationForm

User = get_user_model()

@admin_required
def admin_dashboard(request):
    """
    View for Admin dashboard.
    Admins can see counts for companies, users, and work orders.
    """
    # Company counts by type
    contractors = Company.objects.filter(is_contractor=True)
    managers = Company.objects.filter(is_property_manager=True)
    clients = Company.objects.filter(is_client=True)

    # Add users and work orders to context
    users = User.objects.all()
    open_work_orders = WorkOrder.objects.filter(status='open')
    completed_work_orders = WorkOrder.objects.filter(status='completed')

    return render(request, 'core/dashboards/admin_dashboard.html', {
        'contractors': contractors,
        'managers': managers,
        'clients': clients,
        'users': users,
        'open_work_orders': open_work_orders,
        'completed_work_orders': completed_work_orders,
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
    elif user.role == 'property_manager':
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

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@admin_required
def create_user(request):
    """
    Allows Admins to create new users with specific roles and companies.
    Handles both GET (show form) and POST (form submission) requests.
    """
    if request.method == 'POST':
        # Bind form with POST data
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save new user to the database
            messages.success(request, "User created successfully.")
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()  # Show empty form for GET request

    # Ensure companies are passed
    companies = Company.objects.all()

    return render(request, 'core/create_user.html', {'form': form, 'companies': companies})

@admin_required
def create_company(request):
    """
    Allows Admins to create a new company (contractor, PM, or client).
    """
    if request.method == 'POST':
        form = CompanyCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Company created successfully.")
            return redirect('admin_dashboard')
    else:
        form = CompanyCreationForm()

    return render(request, 'core/create_company.html', {'form': form})

@admin_required
def create_client(request):
    """
    Allows Admins to create new client sites and assign them to a property manager agency.
    """
    if request.method == 'POST':
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client created successfully.")
            return redirect('admin_dashboard')
    else:
        form = ClientCreationForm()

    return render(request, 'core/create_client.html', {'form': form})