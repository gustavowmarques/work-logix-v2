from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from core.views import CustomLoginView
from django.contrib import messages

urlpatterns = [
    # ====================
    # Authentication
    # ====================
    path('login/', CustomLoginView.as_view(), name='login'),                      # Custom login view
    path('logout/', views.custom_logout, name='logout'),                         # Custom logout handler

    # ====================
    # Post-login Routing
    # ====================
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),  # Redirects user based on role

    # ====================
    # Dashboard Routes
    # ====================
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),                  # Super Admin dashboard
    path('dashboard/pm/', views.pm_dashboard, name='pm_dashboard'),                           # Property Manager dashboard
    path('dashboard/contractor/', views.contractor_dashboard, name='contractor_dashboard'),   # Contractor dashboard
    path('dashboard/assistant/', views.assistant_dashboard, name='assistant_dashboard'),      # Assistant dashboard

    # ====================
    # Create Pages (Forms)
    # ====================
    path('dashboard/admin/create-user/', views.create_user, name='create_user'),              # Create new user
    path('dashboard/admin/create-company/', views.create_company, name='create_company'),     # Create new company
    path('dashboard/admin/create-client/', views.create_client, name='create_client'),        # Create new client

    # ====================
    # Manage Pages (Lists)
    # ====================
    path('dashboard/admin/companies/', views.manage_companies, name='manage_companies'),      # List of companies
    path('dashboard/admin/users/', views.manage_users, name='manage_users'),                  # List of users
    path('dashboard/admin/clients/', views.manage_clients, name='manage_clients'),            # List of clients

    # ============================
    # User CRUD (View/Edit/Delete)
    # ============================
    path('dashboard/admin/users/<int:user_id>/view/', views.view_user, name='view_user'),
    path('dashboard/admin/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('dashboard/admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    # =============================
    # Client CRUD (View/Edit/Delete)
    # =============================
    path('dashboard/admin/clients/<int:client_id>/view/', views.view_client, name='view_client'),
    path('dashboard/admin/clients/<int:client_id>/edit/', views.edit_client, name='edit_client'),
    path('dashboard/admin/clients/<int:client_id>/delete/', views.delete_client, name='delete_client'),

    # ===============================
    # Company CRUD (View/Edit/Delete)
    # ===============================
    path('dashboard/admin/companies/<int:company_id>/view/', views.view_company, name='view_company'),
    path('dashboard/admin/companies/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('dashboard/admin/companies/<int:company_id>/delete/', views.delete_company, name='delete_company'),
]
