from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.utils.timezone import now

from .decorators import property_manager_required, contractor_required, assistant_required, admin_required
from .models import Client, Company, WorkOrder, CustomUser, BusinessType, Unit
from .forms import CustomUserCreationForm, CompanyCreationForm, ClientCreationForm, WorkOrderForm

User = get_user_model()

# ============================================================
# Dashboard Views (Role-based)
# ============================================================

@admin_required
def admin_dashboard(request):
    """
    Admin dashboard showing company/user/work order metrics.
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

# ============================================================
# Authentication and Routing
# ============================================================

def redirect_after_login(request):
    """
    Redirects users to the appropriate dashboard after login.
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
    return redirect('login')  # fallback

class CustomLoginView(LoginView):
    """
    Custom login view.
    """
    template_name = 'core/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('redirect_after_login')
        return super().dispatch(request, *args, **kwargs)

def custom_logout(request):
    """
    Logs out user and redirects to login page.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# ============================================================
# Work Order Views
# ============================================================

@login_required
def create_work_order(request):
    """
    Allows Admins, PMs, or Assistants to create a Work Order.
    """
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.created_by = request.user
            work_order.status = 'new'
            work_order.save()
            messages.success(request, "Work order created successfully.")
            return redirect('redirect_after_login')
    else:
        form = WorkOrderForm()

    contractors = Company.objects.filter(is_contractor=True)
    form.fields['preferred_contractor'].queryset = contractors
    form.fields['second_contractor'].queryset = contractors

    return render(request, 'core/create_work_order.html', {'form': form})

@login_required
def my_work_orders(request):
    """
    Property Managers and Assistants can view only work orders they created.
    """
    if request.user.role not in ['property_manager', 'assistant']:
        return HttpResponseForbidden("Not allowed")

    work_orders = WorkOrder.objects.filter(created_by=request.user)
    return render(request, 'core/my_work_orders.html', {'work_orders': work_orders})

@contractor_required
def accept_work_order(request, work_order_id):
    """
    Allows contractor to accept a work order.
    """
    work_order = get_object_or_404(WorkOrder, id=work_order_id)

    if request.user.company != work_order.assigned_contractor:
        return HttpResponseForbidden("Not authorized to accept this work order.")

    work_order.status = 'accepted'
    work_order.save()
    messages.success(request, "You have accepted the work order.")
    return redirect('contractor_dashboard')

@contractor_required
def reject_work_order(request, work_order_id):
    """
    Allows contractor to reject a work order and handles reassignment logic.
    """
    work_order = get_object_or_404(WorkOrder, id=work_order_id)

    if request.user.company != work_order.assigned_contractor:
        return HttpResponseForbidden("Not authorized to reject this work order.")

    if work_order.assigned_contractor == work_order.preferred_contractor:
        if work_order.second_contractor:
            work_order.assigned_contractor = work_order.second_contractor
            work_order.status = 'assigned'
        else:
            work_order.assigned_contractor = None
            work_order.status = 'returned'
    elif work_order.assigned_contractor == work_order.second_contractor:
        work_order.assigned_contractor = None
        work_order.status = 'returned'

    work_order.save()
    messages.success(request, "You have rejected the work order.")
    return redirect('contractor_dashboard')

# ============================================================
# User/Company/Client Creation & Management
# ============================================================

@admin_required
def create_user(request):
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "User created successfully.")
        return redirect('manage_users')
    return render(request, 'core/create_user.html', {'form': form, 'companies': Company.objects.all()})

@admin_required
def create_company(request):
    form = CompanyCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Company created successfully.")
        return redirect('manage_companies')
    return render(request, 'core/create_company.html', {'form': form})

@admin_required
def create_client(request):
    form = ClientCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Client created successfully.")
        return redirect('manage_clients')
    return render(request, 'core/create_client.html', {'form': form})

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
# CRUD: Users, Clients, Companies
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
