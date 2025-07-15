from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages

class CustomLoginView(LoginView):
    """
    Custom login view.
    """
    template_name = 'core/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('redirect_after_login')
        return super().dispatch(request, *args, **kwargs)
    
def custom_logout(request):
    """
    Logs out user and redirects to login page.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

def redirect_after_login(request):
    """
    Redirects users to the appropriate dashboard after login.
    """
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'property_manager':
        return redirect('pm_dashboard')
    elif user.role == 'contractor':
        return redirect('contractor_dashboard')
    elif user.role == 'assistant':
        return redirect('assistant_dashboard')
    return redirect('login')  # fallback
