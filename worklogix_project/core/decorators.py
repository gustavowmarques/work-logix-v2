from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth.decorators import user_passes_test

def role_required(required_role):
    """
    Returns a decorator that checks if the logged-in user has the specified role.
    """
    def decorator(view_func):
        return user_passes_test(
            lambda user: user.is_authenticated and user.role == required_role
        )(view_func)
    return decorator

# Shorthand decorators for each role
property_manager_required = role_required('pm')
contractor_required = role_required('contractor')
assistant_required = role_required('assistant')
admin_required = role_required('admin')
