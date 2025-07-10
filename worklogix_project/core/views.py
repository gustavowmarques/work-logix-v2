from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .decorators import property_manager_required, contractor_required, assistant_required, admin_required
from .models import Client, Company, WorkOrder, CustomUser, BusinessType, Unit
from .forms import CustomUserCreationForm, CompanyCreationForm, ClientCreationForm, WorkOrderForm
from django.utils.timezone import now

User = get_user_model()

# ============================================================
# Dashboard Views
# ============================================================

@admin_required
def admin_dashboard(request):
    """
    Admin dashboard view showing company/user/work order metrics.
    """
    contractors = Company.objects.filter(is_contractor=True)
    managers = Company.objects.filter(is_property_manager=True)
    clients = Company.objects.filter(is_client=True)
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
    Property Manager dashboard (assigned contractors & clients).
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
    Contractor dashboard (company-specific view).
    """
    my_company = request.user.company
    return render(request, 'core/dashboards/contractor_dashboard.html', {
        'my_company': my_company,
    })

@assistant_required
def assistant_dashboard(request):
    """
    Assistant dashboard (read-only overview).
    """
    clients = Company.objects.filter(is_client=True)
    contractors = Company.objects.filter(is_contractor=True)
    return render(request, 'core/dashboards/assistant_dashboard.html', {
        'clients': clients,
        'contractors': contractors,
    })

# ============================================================
# Login / Logout / Redirect
# ============================================================

def redirect_after_login(request):
    """
    Redirect user to appropriate dashboard after login.
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
    return redirect('admin:index')  # fallback

class CustomLoginView(LoginView):
    """
    Login form using Django’s built-in system with custom template.
    """
    template_name = 'core/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('redirect_after_login')
        return super().dispatch(request, *args, **kwargs)

def custom_logout(request):
    """
    Logs the user out and redirects to login page with message.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# ============================================================
# Creation Views (Add)
# ============================================================

@admin_required
def create_user(request):
    """
    Admins can create users and assign to a company and role.
    """
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "User created successfully.")
        return redirect('manage_users')

    return render(request, 'core/create_user.html', {
        'form': form,
        'companies': Company.objects.all()
    })

@admin_required
def create_company(request):
    """
    Admins can create companies.
    """
    form = CompanyCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Company created successfully.")
        return redirect('manage_companies')

    return render(request, 'core/create_company.html', {'form': form})

@admin_required
def create_client(request):
    """
    Admins can create client sites and assign PM company.
    """
    form = ClientCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Client created successfully.")
        return redirect('manage_clients')

    return render(request, 'core/create_client.html', {'form': form})

@property_manager_required
def my_work_orders(request):
    """
    Property Managers see only work orders they created.
    """
    work_orders = WorkOrder.objects.filter(created_by=request.user)
    return render(request, 'core/property_manager/my_work_orders.html', {
        'work_orders': work_orders
    })

@login_required
def create_work_order(request):
    """
    Allows Admins or Property Managers to create a work order.
    Filters contractors based on selected business type.
    """
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.created_by = request.user
            work_order.status = 'new'
            work_order.save()
            messages.success(request, "Work order created successfully.")
            return redirect('admin_dashboard' if request.user.role == 'admin' else 'pm_dashboard')
    else:
        form = WorkOrderForm()

    # Filter contractors dynamically based on business type (optional: JS later)
    contractors = Company.objects.filter(is_contractor=True)
    form.fields['preferred_contractor'].queryset = contractors
    form.fields['second_contractor'].queryset = contractors

    return render(request, 'core/create_work_order.html', {'form': form})

# ============================================================
# Manage Views (List/Overview)
# ============================================================

@admin_required
def manage_users(request):
    users = CustomUser.objects.select_related('company').all()
    return render(request, 'core/admin/manage_users.html', {'users': users})

@admin_required
def manage_companies(request):
    companies = Company.objects.all()
    return render(request, 'core/admin/manage_companies.html', {'companies': companies})

@admin_required
def manage_clients(request):
    clients = Client.objects.select_related('company').all()
    return render(request, 'core/admin/manage_clients.html', {'clients': clients})

# ============================================================
# CRUD: Users
# ============================================================

@admin_required
def view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'core/admin/view_user.html', {'user': user})

@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    form = CustomUserCreationForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, "User updated successfully.")
        return redirect('manage_users')
    return render(request, 'core/admin/edit_user.html', {'form': form})

@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('manage_users')

# ============================================================
# CRUD: Clients
# ============================================================

@admin_required
def view_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'core/admin/view_client.html', {'client': client})

@admin_required
def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    form = ClientCreationForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, "Client updated successfully.")
        return redirect('manage_clients')
    return render(request, 'core/admin/edit_client.html', {'form': form})

@admin_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    messages.success(request, "Client deleted.")
    return redirect('manage_clients')

# ============================================================
# CRUD: Companies
# ============================================================

@admin_required
def view_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'core/admin/view_company.html', {'company': company})

@admin_required
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    form = CompanyCreationForm(request.POST or None, instance=company)
    if form.is_valid():
        form.save()
        messages.success(request, "Company updated successfully.")
        return redirect('manage_companies')
    return render(request, 'core/admin/edit_company.html', {'form': form})

@admin_required
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, "Company deleted.")
    return redirect('manage_companies')
