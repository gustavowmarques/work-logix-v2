from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from core.views import CustomLoginView
from django.contrib import messages

urlpatterns = [
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    
    # Redirect after login
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),


    # Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/create-user/', views.create_user, name='create_user'),
    path('dashboard/pm/', views.pm_dashboard, name='pm_dashboard'),
    path('dashboard/contractor/', views.contractor_dashboard, name='contractor_dashboard'),
    path('dashboard/assistant/', views.assistant_dashboard, name='assistant_dashboard'),
]