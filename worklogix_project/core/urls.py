# worklogix_project/urls.py
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

# Auth
from core.views.auth import CustomLoginView, custom_logout, redirect_after_login

# Dashboards
from core.views.dashboard import (
    admin_dashboard, pm_dashboard, contractor_dashboard, assistant_dashboard
)

# Work orders
from core.views.work_order import (
    create_work_order, view_work_order_detail,
    accept_work_order, reject_work_order, complete_work_order,
    my_contractor_orders, my_work_orders, admin_work_orders_view,
)

# Units
from core.views.unit import client_units, review_units, delete_unit, unit_generator

# Clients
from core.views.client import (
    create_client, manage_clients, view_client, edit_client, delete_client
)

# Companies
from core.views.company import (
    create_company, manage_companies, view_company, edit_company, delete_company
)

# Users (admin area)
from core.views.admin import (
    create_user, manage_users, view_user, edit_user, delete_user, reset_user_password
)

# API
from core.views.api import get_contractors_by_business_type, get_units_by_client


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Auth
    path("", lambda request: redirect("login", permanent=False)),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("redirect-after-login/", redirect_after_login, name="redirect_after_login"),

    # Dashboards
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/pm/", pm_dashboard, name="pm_dashboard"),
    path("dashboard/contractor/", contractor_dashboard, name="contractor_dashboard"),
    path("dashboard/assistant/", assistant_dashboard, name="assistant_dashboard"),

    # Work orders
    path("work-orders/create/", create_work_order, name="create_work_order"),
    path("work-orders/<int:work_order_id>/", view_work_order_detail, name="view_work_order_detail"),
    path("work-orders/<int:work_order_id>/accept/", accept_work_order, name="accept_work_order"),
    path("work-orders/<int:work_order_id>/reject/", reject_work_order, name="reject_work_order"),
    path("work-orders/<int:work_order_id>/complete/", complete_work_order, name="complete_work_order"),
    path("contractor/work-orders/", my_contractor_orders, name="my_contractor_orders"),
    path("my-work-orders/", my_work_orders, name="my_work_orders"),
    path("work-orders/admin/", admin_work_orders_view, name="admin_work_orders"),

    # Units
    path("clients/<int:client_id>/units/", client_units, name="client_units"),
    path("units/review/", review_units, name="review_units"),
    path("units/delete/<int:unit_id>/", delete_unit, name="delete_unit"),
    path("units/generator/", unit_generator, name="unit_generator"),

    # Clients
    path("clients/", manage_clients, name="manage_clients"),
    path("clients/create/", create_client, name="create_client"),
    path("clients/<int:client_id>/view/", view_client, name="view_client"),
    path("clients/<int:client_id>/edit/", edit_client, name="edit_client"),
    path("clients/<int:client_id>/delete/", delete_client, name="delete_client"),

    # Companies
    path("companies/", manage_companies, name="manage_companies"),
    path("companies/create/", create_company, name="create_company"),
    path("companies/<int:company_id>/view/", view_company, name="view_company"),
    path("companies/<int:company_id>/edit/", edit_company, name="edit_company"),
    path("companies/<int:company_id>/delete/", delete_company, name="delete_company"),

    # Users
    path("users/", manage_users, name="manage_users"),
    path("users/create/", create_user, name="create_user"),
    path("users/<int:user_id>/view/", view_user, name="view_user"),
    path("users/<int:user_id>/edit/", edit_user, name="edit_user"),
    path("users/<int:user_id>/delete/", delete_user, name="delete_user"),
    path("users/<int:user_id>/reset-password/", reset_user_password, name="reset_user_password"),

    # API
    path("api/contractors/<int:business_type_id>/", get_contractors_by_business_type,
         name="get_contractors_by_business_type"),
    path("api/units/<int:client_id>/", get_units_by_client, name="get_units_by_client"),
]

