from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='custom_login'),
    
    # Redirect after login based on role
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),


    # Role-based dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/pm/', views.pm_dashboard, name='pm_dashboard'),
    path('dashboard/contractor/', views.contractor_dashboard, name='contractor_dashboard'),
    path('dashboard/assistant/', views.assistant_dashboard, name='assistant_dashboard'),
]
