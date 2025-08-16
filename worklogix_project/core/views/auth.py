from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

class CustomLoginView(LoginView):
    """Login view that skips the form if you're already logged in."""
    template_name = "core/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("redirect_after_login")
        return super().dispatch(request, *args, **kwargs)

def custom_logout(request):
    """Log out and go to login page."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

@login_required
def redirect_after_login(request):
    """
    Send users to the right dashboard.
    IMPORTANT: never redirect authenticated users back to 'login' (that causes a loop).
    """
    user = request.user
    role = getattr(user, "role", None)

    # Superusers/staff: treat as admin
    if user.is_superuser or user.is_staff or role == "admin":
        return redirect("admin_dashboard")

    mapping = {
        "property_manager": "pm_dashboard",
        "contractor": "contractor_dashboard",
        "assistant": "assistant_dashboard",
    }
    if role in mapping:
        return redirect(mapping[role])

    # Safe fallback: log out with a message (or send to a neutral page)
    messages.warning(request, "Your account has no role assigned. Please contact an administrator.")
    return redirect("logout")
