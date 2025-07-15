"""
This file has been intentionally left nearly empty.

All view logic has been modularized and moved to dedicated files:
- admin.py: Admin-only views (e.g., dashboard, user/company/client CRUD)
- dashboard.py: Role-based dashboards for PMs, contractors, assistants
- auth.py: Login, logout, and post-login redirect views
- client.py: Client creation, viewing, editing, deleting
- unit.py: Unit creation and review
- work_order.py: Work order creation and contractor interactions

This structure keeps the codebase organized and easier to maintain.

You can keep this file for legacy compatibility or remove it entirely
if nothing imports from `core.views` directly.
"""
