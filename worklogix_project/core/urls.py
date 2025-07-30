from django.urls import path
from django.shortcuts import redirect

# ========================
# AUTHENTICATION VIEWS
# ========================
from core.views.auth import (
    CustomLoginView,
    custom_logout,
    redirect_after_login,
)

# ========================
# DASHBOARD VIEWS
# ========================
from core.views.dashboard import (
    admin_dashboard,
    pm_dashboard,
    contractor_dashboard,
    assistant_dashboard,
)

# ========================
# WORK ORDER VIEWS
# ========================
from core.views.work_order import (
    create_work_order,
    view_work_order_detail,
    accept_work_order,
    reject_work_order,
    my_contractor_orders,
    my_work_orders,
)

# ========================
# UNIT VIEWS
# ========================
from core.views.unit import (
    client_units,
    review_units,
    delete_unit,
    unit_generator,
)

# ========================
# CLIENT VIEWS
# ========================
from core.views.client import (
    create_client,
    manage_clients,
    view_client,
    edit_client,
    delete_client,
)

# ========================
# COMPANY VIEWS
# ========================
from core.views.company import (
    create_company,
    manage_companies,
    view_company,
    edit_company,
    delete_company,
)

# ========================
# USER VIEWS (Admin)
# ========================
from core.views.admin import (
    create_user,
    manage_users,
    view_user,
    edit_user,
    delete_user,
    create_unit,  # Only this function needed here from admin for routing
)

# ========================
# AJAX / API ENDPOINTS
# ========================
from core.views.api import (
    get_contractors_by_business_type,
    get_units_by_client,
)

# ========================
# URL PATTERNS
# ========================
urlpatterns = [
    # --------------------
    # AUTHENTICATION
    # --------------------
    path('', lambda request: redirect('login', permanent=False)),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('redirect-after-login/', redirect_after_login, name='redirect_after_login'),

    # --------------------
    # DASHBOARDS
    # --------------------
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/pm/', pm_dashboard, name='pm_dashboard'),
    path('dashboard/contractor/', contractor_dashboard, name='contractor_dashboard'),
    path('dashboard/assistant/', assistant_dashboard, name='assistant_dashboard'),

    # --------------------
    # WORK ORDERS
    # --------------------
    path('work-orders/create/', create_work_order, name='create_work_order'),
    path('work-orders/<int:work_order_id>/', view_work_order_detail, name='view_work_order_detail'),
    path('work-orders/<int:work_order_id>/accept/', accept_work_order, name='accept_work_order'),
    path('work-orders/<int:work_order_id>/reject/', reject_work_order, name='reject_work_order'),
    path('contractor/work-orders/', my_contractor_orders, name='my_contractor_orders'),
    path('my-work-orders/', my_work_orders, name='my_work_orders'),

    # --------------------
    # UNITS
    # --------------------
    path('units/create/', create_unit, name='create_unit'),
    path('clients/<int:client_id>/units/', client_units, name='client_units'),
    path('units/review/', review_units, name='review_units'),
    path('units/delete/<int:unit_id>/', delete_unit, name='delete_unit'),
    path('units/generator/', unit_generator, name='unit_generator'),

    # --------------------
    # CLIENTS
    # --------------------
    path('clients/', manage_clients, name='manage_clients'),
    path('clients/create/', create_client, name='create_client'),
    path('clients/<int:client_id>/view/', view_client, name='view_client'),
    path('clients/<int:client_id>/edit/', edit_client, name='edit_client'),
    path('clients/<int:client_id>/delete/', delete_client, name='delete_client'),

    # --------------------
    # COMPANIES
    # --------------------
    path('companies/', manage_companies, name='manage_companies'),
    path('companies/create/', create_company, name='create_company'),
    path('companies/<int:company_id>/view/', view_company, name='view_company'),
    path('companies/<int:company_id>/edit/', edit_company, name='edit_company'),
    path('companies/<int:company_id>/delete/', delete_company, name='delete_company'),

    # --------------------
    # USERS (Admin)
    # --------------------
    path('users/', manage_users, name='manage_users'),
    path('users/create/', create_user, name='create_user'),
    path('users/<int:user_id>/view/', view_user, name='view_user'),
    path('users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),

    # --------------------
    # AJAX / API ENDPOINTS
    # --------------------
    path('api/contractors/<int:business_type_id>/', get_contractors_by_business_type, name='get_contractors_by_business_type'),
    path('api/units/<int:client_id>/', get_units_by_client, name='get_units_by_client'),
]
