from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from core.models import Company, BusinessType
from core.forms import CompanyCreationForm


# -------------------------------
# View all companies (Admin only)
# -------------------------------
@login_required
def manage_companies(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to view this page.")

    companies = Company.objects.all()
    return render(request, 'core/admin/manage_companies.html', {'companies': companies})


# -------------------------------
# Create a new company (Admin only)
# -------------------------------
@login_required
def create_company(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to create companies.")

    business_types = BusinessType.objects.all()

    if request.method == 'POST':
        form = CompanyCreationForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            # Save selected business type from dropdown
            business_type_id = request.POST.get('business_type_id')
            if business_type_id:
                company.business_type_id = business_type_id
            company.save()
            messages.success(request, "Company created successfully.")
            return redirect('manage_companies')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CompanyCreationForm()

    return render(request, 'core/create_company.html', {
        'form': form,
        'business_types': business_types
    })


# -------------------------------
# View company details
# -------------------------------
@login_required
def view_company(request, company_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to view this company.")

    company = get_object_or_404(Company, id=company_id)
    return render(request, 'core/admin/view_company.html', {'company': company})


# -------------------------------
# Edit a company
# -------------------------------
@login_required
def edit_company(request, company_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to edit this company.")

    company = get_object_or_404(Company, id=company_id)
    business_types = BusinessType.objects.all()

    if request.method == 'POST':
        form =CompanyCreationForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save(commit=False)
            business_type_id = request.POST.get('business_type_id')
            if business_type_id:
                company.business_type_id = business_type_id
            company.save()
            messages.success(request, "Company updated successfully.")
            return redirect('manage_companies')
    else:
        form =CompanyCreationForm(instance=company)

    return render(request, 'core/admin/edit_company.html', {
        'form': form,
        'company': company,
        'business_types': business_types
    })


# -------------------------------
# Delete a company
# -------------------------------
@login_required
def delete_company(request, company_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to delete this company.")

    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, "Company deleted successfully.")
    return redirect('manage_companies')
