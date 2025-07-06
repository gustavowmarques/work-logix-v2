from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company, Client, WorkOrder

# Register the CustomUser model using Django's built-in UserAdmin layout
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Displayed in the user list
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_staff', 'is_active'
    )
    
    # Fields used in the user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'company')}),
    )

    # Fields shown in the "Add user" form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role', 'company')}),
    )

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_contractor', 'is_client', 'is_property_manager']
    list_filter = ['is_contractor', 'is_client', 'is_property_manager']

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'assigned_contractor', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'address')
    search_fields = ('name', 'address')