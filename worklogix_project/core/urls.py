from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from core.views import CustomLoginView

urlpatterns = [
    # ====================
    # Authentication
    # ====================
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # ====================
    # Post-login Routing
    # ====================
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),

    # ====================
    # Dashboard Routes
    # ====================
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/pm/', views.pm_dashboard, name='pm_dashboard'),
    path('dashboard/contractor/', views.contractor_dashboard, name='contractor_dashboard'),
    path('dashboard/assistant/', views.assistant_dashboard, name='assistant_dashboard'),

    # ====================
    # Create Pages (Forms)
    # ====================
    path('dashboard/admin/create-user/', views.create_user, name='create_user'),
    path('dashboard/admin/create-company/', views.create_company, name='create_company'),
    path('dashboard/admin/create-client/', views.create_client, name='create_client'),

    # ====================
    # Manage Pages (Lists)
    # ====================
    path('dashboard/admin/companies/', views.manage_companies, name='manage_companies'),
    path('dashboard/admin/users/', views.manage_users, name='manage_users'),
    path('dashboard/admin/clients/', views.manage_clients, name='manage_clients'),

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

    # ===============================
    # Work Orders
    # ===============================
    path('dashboard/work-orders/create/', views.create_work_order, name='create_work_order'),
    path('pm/work-orders/', views.my_work_orders, name='my_work_orders'),

    # Contractor response to work orders
    path('work-orders/<int:work_order_id>/accept/', views.accept_work_order, name='accept_work_order'),
    path('work-orders/<int:work_order_id>/reject/', views.reject_work_order, name='reject_work_order'),

]
