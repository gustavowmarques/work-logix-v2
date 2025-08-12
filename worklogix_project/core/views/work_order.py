from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from core.decorators import contractor_required
from core.models import WorkOrder, Unit, Company
from core.forms import WorkOrderForm
from django.urls import reverse

# -------------------------------
# Create Work Order (PM/Admin/Assistant)
# -------------------------------
@login_required
def create_work_order(request):
    if request.user.role not in ['admin', 'property_manager', 'assistant']:
        return HttpResponseForbidden("You are not allowed to create work orders.")
    
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


# -------------------------------
# PM/Assistant views their own created work orders
# -------------------------------
@login_required
def my_work_orders(request):
    user = request.user

    if user.role == 'property_manager':
        work_orders = WorkOrder.objects.filter(created_by=user)

    elif user.role == 'assistant':
        work_orders = WorkOrder.objects.filter(created_by=user)

    elif user.role == 'contractor':
        work_orders = WorkOrder.objects.filter(assigned_contractor=user.company)

    else:
        return HttpResponseForbidden("Not allowed")

    return render(request, 'core/my_work_orders.html', {'work_orders': work_orders})



# -------------------------------
# Contractor accepts a work order
# -------------------------------
@login_required
@require_POST
def accept_work_order(request, work_order_id):
    order = get_object_or_404(WorkOrder, pk=work_order_id)

    if request.user.role != 'contractor' or not request.user.company:
        return HttpResponseForbidden("Not allowed")

    contractor_company = request.user.company
    if contractor_company not in [order.preferred_contractor, order.second_contractor]:
        return HttpResponseForbidden("Not authorized for this order.")

    order.status = 'accepted'
    order.assigned_contractor = contractor_company
    order.save()

    messages.success(request, "Work order accepted.")
    return redirect('view_work_order_detail', work_order_id=order.id)

# -------------------------------
# Contractor rejects a work order
# -------------------------------
@contractor_required
@require_POST
def reject_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    contractor_company = request.user.company

    if contractor_company not in [work_order.preferred_contractor, work_order.second_contractor]:
        return HttpResponseForbidden("Not authorized to reject this work order.")

    # keep your existing “return/assign second contractor” logic
    if work_order.status in ['new', 'assigned']:
        if contractor_company == work_order.preferred_contractor and work_order.second_contractor:
            work_order.assigned_contractor = work_order.second_contractor
            work_order.status = 'assigned'
        else:
            work_order.assigned_contractor = None
            work_order.status = 'returned'
        work_order.save(update_fields=['assigned_contractor', 'status'])

    messages.success(request, "You have rejected the work order.")
    return redirect('view_work_order_detail', work_order_id=work_order.id)


@contractor_required
@require_POST
def complete_work_order(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    contractor = request.user.company

    if work_order.status != 'accepted' or work_order.assigned_contractor != contractor:
        return HttpResponseForbidden("You are not authorized to complete this work order.")

    uploaded_file = request.FILES.get('file')
    notes = request.POST.get('notes')

    if not uploaded_file or not notes:
        messages.error(request, "Both file and notes are required.")
        return redirect('view_work_order_detail', work_order_id=work_order.id)

    work_order.attachment = uploaded_file
    work_order.completion_notes = notes
    work_order.completed_at = timezone.now()
    work_order.status = 'completed'
    work_order.save()

    messages.success(request, "Work order marked as completed.")
    return redirect('view_work_order_detail', work_order_id=work_order.id)

# -------------------------------
# AJAX: Load units for selected client
# -------------------------------
@login_required
def load_units_for_client(request):
    client_id = request.GET.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Missing client ID'}, status=400)
    
    units = Unit.objects.filter(client_id=client_id).order_by('name')
    unit_list = [{'id': unit.id, 'name': unit.name} for unit in units]
    return JsonResponse({'units': unit_list})


# -------------------------------
# View details of a specific work order
# -------------------------------
@login_required
def view_work_order_detail(request, work_order_id):
    order = get_object_or_404(WorkOrder, id=work_order_id)

    user = request.user
    role = getattr(user, "role", "")
    company = getattr(user, "company", None)

    # --- Authorization ---
    if role == "admin":
        allowed = True
    else:
        allowed = (
            order.created_by_id == user.id
            or (
                company is not None
                and company in [order.preferred_contractor,
                                order.second_contractor,
                                order.assigned_contractor]
            )
        )

    if not allowed:
        return HttpResponseForbidden("Not allowed")

    # --- Role-aware back URL ---
    if role == "admin":
        back_url = reverse("admin_work_orders")  # your /work-orders/admin/ list
    elif role == "contractor":
        back_url = reverse("contractor_dashboard")  # or 'my_contractor_orders'
    elif role == "property_manager":
        back_url = reverse("admin_dashboard")  # or your PM dashboard url
    else:
        back_url = reverse("redirect_after_login")

    # --- Contractor-only action flags (unchanged logic) ---
    can_accept_or_reject = (
        role == 'contractor'
        and order.status == 'new'
        and company in [order.preferred_contractor, order.second_contractor]
    )

    can_mark_complete = (
        role == 'contractor'
        and order.status == 'accepted'
        and order.assigned_contractor == company
    )

    return render(
        request,
        'core/work_order_detail.html',  # keep your existing template
        {
            'order': order,
            'can_accept_or_reject': can_accept_or_reject,
            'can_mark_complete': can_mark_complete,
            'back_url': back_url,   # <-- use this in the template
        }
    )

@login_required
def admin_work_orders_view(request):
    if not request.user.role == 'admin':
        return redirect('dashboard') 

    work_orders = WorkOrder.objects.all().order_by('-created_at')
    return render(request, 'core/admin/work_orders_list.html', {
        'work_orders': work_orders
    })

# -------------------------------
# Contractor: View assigned work orders
# -------------------------------
@login_required
def my_contractor_orders(request):
    if request.user.role != 'contractor':
        return HttpResponseForbidden("Not allowed")
    
    contractor_company = request.user.company
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    # Only show accepted, rejected, or completed work orders assigned to this contractor
    assigned_orders = WorkOrder.objects.filter(
        assigned_contractor=contractor_company,
        status__in=['accepted', 'rejected', 'completed']
    )

    # Apply search
    if query:
        assigned_orders = assigned_orders.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Apply status filter
    VALID_STATUSES = ['accepted', 'rejected', 'completed']
    if status_filter in VALID_STATUSES:
        assigned_orders = assigned_orders.filter(status=status_filter)

    assigned_orders = assigned_orders.order_by('-created_at')

    return render(request, 'core/contractor/my_work_orders.html', {
        'work_orders': assigned_orders,
        'query': query,
        'status_filter': status_filter,
    })


