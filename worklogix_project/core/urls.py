from django.urls import path
from django.shortcuts import redirect
from core.views.unit import unit_generator, delete_unit, client_units, review_units
from . import views


# ============================
# API Views
# ============================
from core.views.api import (
    get_contractors_by_business_type,
    get_units_by_client,
)

# ============================
# Auth + Routing Views
# ============================
from core.views.auth import CustomLoginView, custom_logout, redirect_after_login

# ============================
# Admin Dashboard + CRUD Views
# ============================
from core.views.admin import (
    admin_dashboard, create_user, create_company,
    manage_users, manage_companies,
    view_user, edit_user, delete_user,
    view_company, edit_company, delete_company,
    create_unit
)

# ============================
# Client Views
# ============================
from core.views.client import (
    create_client, manage_clients,
    view_client, edit_client, delete_client
)

# ============================
# Work Order Views
# ============================
from core.views.work_order import (
    create_work_order, my_work_orders,
    accept_work_order, reject_work_order,
    load_units_for_client
)

# ============================
# Dashboard Role Views
# ============================
from core.views.dashboard import (
    pm_dashboard, contractor_dashboard, assistant_dashboard
)

# ============================
# URL Patterns
# ============================
urlpatterns = [
    # Root Redirect
    path('', lambda request: redirect('login', permanent=False)),

    # ====================
    # Authentication
    # ====================
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),

    # ====================
    # Post-login Redirect
    # ====================
    path('redirect-after-login/', redirect_after_login, name='redirect_after_login'),

    # ====================
    # Dashboards
    # ====================
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/pm/', pm_dashboard, name='pm_dashboard'),
    path('dashboard/contractor/', contractor_dashboard, name='contractor_dashboard'),
    path('dashboard/assistant/', assistant_dashboard, name='assistant_dashboard'),

    # ====================
    # Create Forms
    # ====================
    path('dashboard/admin/create-user/', create_user, name='create_user'),
    path('dashboard/admin/create-company/', create_company, name='create_company'),
    path('dashboard/admin/create-client/', create_client, name='create_client'),  # Internal
    path('clients/create/', create_client, name='create_client_public'),          # Public
    path('dashboard/admin/units/create/', create_unit, name='create_unit'),

    # ====================
    # Unit Management
    # ====================
    path('clients/units/review/', review_units, name='review_units'),
    path('dashboard/admin/units/generator/', unit_generator, name='unit_generator'),
    path('dashboard/admin/units/generator/<int:client_id>/', unit_generator, name='unit_generator_for_client'),
    path('dashboard/admin/units/delete/<int:unit_id>/', delete_unit, name='delete_unit'),
    path('dashboard/admin/clients/<int:client_id>/units/', client_units, name='client_units'),
   
    # ====================
    # Company Management
    # ====================
    path('dashboard/admin/companies/', manage_companies, name='manage_companies'),
    path('dashboard/admin/companies/<int:company_id>/view/', view_company, name='view_company'),
    path('dashboard/admin/companies/<int:company_id>/edit/', edit_company, name='edit_company'),
    path('dashboard/admin/companies/<int:company_id>/delete/', delete_company, name='delete_company'),

    # ====================
    # User Management
    # ====================
    path('dashboard/admin/users/', manage_users, name='manage_users'),
    path('dashboard/admin/users/<int:user_id>/view/', view_user, name='view_user'),
    path('dashboard/admin/users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('dashboard/admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),

    # ====================
    # Client Management
    # ====================
    path('dashboard/admin/clients/', manage_clients, name='manage_clients'),
    path('dashboard/admin/clients/<int:client_id>/view/', view_client, name='view_client'),
    path('dashboard/admin/clients/<int:client_id>/edit/', edit_client, name='edit_client'),
    path('dashboard/admin/clients/<int:client_id>/delete/', delete_client, name='delete_client'),

    # ====================
    # Work Orders
    # ====================
    path('dashboard/work-orders/create/', create_work_order, name='create_work_order'),
    path('pm/work-orders/', my_work_orders, name='my_work_orders'),

    # Work order actions for contractors
    path('work-orders/<int:work_order_id>/accept/', accept_work_order, name='accept_work_order'),
    path('work-orders/<int:work_order_id>/reject/', reject_work_order, name='reject_work_order'),

    # ====================
    # AJAX/API Endpoints
    # ====================
    path('api/contractors/<int:business_type_id>/', get_contractors_by_business_type, name='get_contractors_by_business_type'),
    path('api/units/<int:client_id>/', get_units_by_client, name='get_units_by_client'),

    # (Optional: Legacy AJAX call from jQuery forms if needed)
    path('ajax/load-units/', load_units_for_client, name='ajax_load_units'),
]
