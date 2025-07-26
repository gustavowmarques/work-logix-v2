from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import Company, BusinessType
from core.forms import CompanyForm  

def create_company(request):
    business_types = BusinessType.objects.all()

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            # Save selected business type
            business_type_id = request.POST.get('business_type_id')
            if business_type_id:
                company.business_type_id = business_type_id
            company.save()
            messages.success(request, "Company created successfully.")
            return redirect('admin_dashboard') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CompanyForm()

    return render(request, 'create_company.html', {
        'form': form,
        'business_types': business_types
    })
