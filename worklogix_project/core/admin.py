from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register the CustomUser model using Django's built-in UserAdmin layout
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Displayed in the user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    
    # Fields used in the user form
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
