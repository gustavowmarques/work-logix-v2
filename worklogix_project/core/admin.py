from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company, Client, WorkOrder, BusinessType

# Register Business Types (e.g., Plumbing, Electrical, etc.)
@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Register Work Orders
@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'assigned_contractor', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

# Register Companies
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_contractor', 'is_client', 'is_property_manager']
    list_filter = ['is_contractor', 'is_client', 'is_property_manager']
    search_fields = ['name', 'email']

# Register Clients
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'address')
    search_fields = ('name', 'address')

# Register Custom Users
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_staff', 'is_active'
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'company')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role', 'company')}),
    )
