# Expose key models for external imports
from .user import CustomUser            # Custom user model with extended fields
from .company import Company            # Company model (contractor, PM, etc.)
from .client import Client              # Client entity (e.g. OMC, RMC, etc.)
from .unit import Unit, UnitGroup       # Physical units (apartments, houses), and groups
from .work_order import WorkOrder       # Work order/request model
from .business_type import BusinessType # Enum-like model for contractor specialization
