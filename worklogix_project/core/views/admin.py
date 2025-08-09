from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from core.decorators import admin_required
from core.models import Company, CustomUser, WorkOrder, Unit, UnitGroup
from django.http import HttpResponseForbidden
from core.forms import (
    CustomUserCreationForm,
    CompanyCreationForm,
    UnitCreationForm,
    UnitGroupCreationForm,
    CustomUserEditForm
)

# ==========================
# Admin Dashboard
# ==========================

@admin_required
def admin_dashboard(request):
    """
    Admin dashboard displaying metrics and entities.
    """
    context = {
        'contractors': Company.objects.filter(is_contractor=True),
        'managers': Company.objects.filter(is_property_manager=True),
        'clients': Company.objects.filter(is_client=True),
        'users': CustomUser.objects.all(),
        'open_work_orders': WorkOrder.objects.filter(status='open'),
        'completed_work_orders': WorkOrder.objects.filter(status='completed'),
    }
    return render(request, 'core/admin/admin_dashboard.html', context)

# ==========================
# User Management
# ==========================

@admin_required
def create_user(request):
    """
    Admin view to create a new user.
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
def manage_users(request):
    """
    Admin view listing all users with company relation.
    """
    users = CustomUser.objects.select_related('company').all()
    return render(request, 'core/admin/manage_users.html', {'users': users})

@admin_required
def view_user(request, user_id):
    """
    Admin view for user detail.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'core/admin/view_user.html', {'user': user})

@admin_required
def edit_user(request, user_id):
    """
    Admin view to edit a user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    form = CustomUserEditForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, "User updated successfully.")
        return redirect('manage_users')
    
    return render(request, 'core/admin/edit_user.html', {'form': form})

@admin_required
def delete_user(request, user_id):
    """
    Admin view to delete a user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('manage_users')

@login_required
def reset_user_password(request, user_id):
    # Only admins should do this
    if getattr(request.user, "role", None) != "admin":
        return HttpResponseForbidden("Not allowed")

    target_user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = SetPasswordForm(user=target_user, data=request.POST)
        if form.is_valid():
            form.save()  # hashes and saves the new password
            messages.success(request, f"Password for '{target_user.username}' was reset successfully.")
            return redirect("manage_users")
    else:
        form = SetPasswordForm(user=target_user)

    return render(request, "core/admin/reset_password.html", {
        "form": form,
        "target_user": target_user,
    })


# ==========================
# Company Management
# ==========================

@admin_required
def create_company(request):
    """
    Admin view to register a new company.
    """
    form = CompanyCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Company created successfully.")
        return redirect('manage_companies')

    return render(request, 'core/create_company.html', {'form': form})

@admin_required
def manage_companies(request):
    """
    Admin view listing all companies.
    """
    companies = Company.objects.all()
    return render(request, 'core/admin/manage_companies.html', {'companies': companies})

@admin_required
def view_company(request, company_id):
    """
    Admin view for company details.
    """
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'core/admin/view_company.html', {'company': company})

@admin_required
def edit_company(request, company_id):
    """
    Admin view to edit a company.
    """
    company = get_object_or_404(Company, id=company_id)
    form = CompanyCreationForm(request.POST or None, instance=company)
    if form.is_valid():
        form.save()
        messages.success(request, "Company updated successfully.")
        return redirect('manage_companies')
    
    return render(request, 'core/admin/edit_company.html', {'form': form})

@admin_required
def delete_company(request, company_id):
    """
    Admin view to delete a company.
    """
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, "Company deleted.")
    return redirect('manage_companies')

# ==========================
# Unit & UnitGroup Creation
# ==========================

@admin_required
def create_unit(request):
    """
    Admin view to manually create a single unit and assign it to a client.
    """
    form = UnitCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Unit created successfully.")
        return redirect('admin_dashboard')
    
    return render(request, 'core/admin/create_unit.html', {'form': form})

@admin_required
def create_unit_group(request):
    """
    Admin view to create a UnitGroup and auto-generate associated units.
    """
    form = UnitGroupCreationForm(request.POST or None)
    if form.is_valid():
        unit_group = form.save(commit=False)
        unit_group.created_by = request.user
        unit_group.save()

        # Helper: Bulk create units based on counts
        def create_units(prefix, count, unit_type):
            for i in range(1, count + 1):
                Unit.objects.create(
                    client=unit_group.client,
                    name=f"{prefix} {i}",
                    unit_type=unit_type,
                    group=unit_group
                )

        # Create units by type
        create_units("Apartment", unit_group.num_apartments, "apartment")
        create_units("Duplex", unit_group.num_duplexes, "duplex")
        create_units("House", unit_group.num_houses, "house")
        create_units("Commercial Unit", unit_group.num_commercial_units, "commercial")

        messages.success(request, "Unit group and units created successfully.")
        return redirect('admin_dashboard')

    return render(request, 'core/create_unit_group.html', {'form': form})
