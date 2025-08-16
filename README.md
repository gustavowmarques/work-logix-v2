# Work Logix — Work Order Management Platform

[**Live Demo on Render**](https://work-logix-v2.onrender.com) · [**GitHub Repository**](https://github.com/gustavowmarques/work-logix-v2)

Work Logix is a Django-based work-order and contractor management application designed for property managers. It supports **role-based dashboards** (Admin, Property Manager, Assistant, Contractor), a **clear Work Order lifecycle**, and **domain-first routing** for maintainable, testable URLs. The project is set up for local development with SQLite (or Postgres via `DATABASE_URL`) and is deployment-ready using WhiteNoise and Gunicorn.

> **Demo Credentials (for assessment)**
>
> - **Superuser (Django Admin)**: `superuser / superuser`  
> - **Additional demo users** *(password for all below: `ChangeMe!2025`)*  
>   - **Non-contractor users**  
>     - `admin_bohan` — `admin@bohanhyland.ie` — role: `admin`  
>     - `assistant_bohan` — `assistant@bohanhyland.ie` — role: `assistant`  
>     - `pm_bohan` — `pm@bohanhyland.ie` — role: `property_manager`
>   - **Contractor users**  
>     - `ctr_blueflow` — `liam@blueflowplumbing.ie` — company: *Blueflow Plumbing Ltd*  
>     - `ctr_sparkrightelec` — `aoife@sparkrightelelectrical.ie` — company: *SparkRight Electrical Ltd*  
>     - `ctr_oakbeam` — `conor@oakandbeam.ie` — company: *Oak & Beam Carpentry*  
>     - `ctr_primecoat` — `maria@primecoat.ie` — company: *PrimeCoat Painters*  
>     - `ctr_brightsweep` — `daniel@brightsweep.ie` — company: *BrightSweep Cleaning Services*  
>     - `ctr_polarair` — `niamh@polarair.ie` — company: *PolarAir Mechanical*  
>     - `ctr_greenscape` — `patrick@greenscape.ie` — company: *GreenScape Grounds*  
>     - `ctr_shieldguard` — `emma@shieldguard.ie` — company: *ShieldGuard Pest Control*  
>     - `ctr_sentinelsec` — `brian@sentinelsecurity.ie` — company: *Sentinel Security Services*  
>     - `ctr_vertexbuild` — `sarah@vertexbuild.ie` — company: *Vertex Build Ltd*  
>     - `ctr_flexhand` — `mark@flexhand.ie` — company: *FlexHand Facilities*

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Key Features](#key-features)  
- [Screens & Roles](#screens--roles)  
- [Work Order Lifecycle](#work-order-lifecycle)  
- [Architecture & Code Structure](#architecture--code-structure)  
- [Technology Stack](#technology-stack)  
- [Requirements](#requirements)  
- [Installation & Setup](#installation--setup)  
- [Environment Variables](#environment-variables)  
- [Running Locally](#running-locally)  
- [Seed Data / Demo Accounts](#seed-data--demo-accounts)  
- [Domain-First URLs](#domain-first-urls)  
- [Security Notes](#security-notes)  
- [Design Rationale & Alignment with Feedback](#design-rationale--alignment-with-feedback)  
- [Known Limitations & Future Work](#known-limitations--future-work)  
- [Deployment Notes](#deployment-notes)  
- [License / Academic Use](#license--academic-use)

---

## Project Overview

**Work Logix** helps property managers create, assign, track, and complete maintenance work orders across multiple developments and contractors. It implements:

- **Role-based dashboards** with post-login redirection,  
- **Enum-backed Work Order statuses** for maintainability,  
- **Domain-first URL scheme** (e.g., all Work Order operations live under `/work-orders/...`).

The goal is clarity of domain, reliability of workflow, and a codebase that’s easy to navigate and extend.

---

## Key Features

- **Role-Based Access & Dashboards**
  - Admin, Property Manager, Assistant, and Contractor roles.
  - After login, users are routed to their role-specific dashboard.

- **Work Orders**
  - Create, assign to contractors, accept/reject, complete, or return to creator.
  - Priority, notes, and timestamps for traceability.

- **Companies, Clients & Units**
  - Property Manager companies, contractor companies, client entities.
  - Units and Unit Groups to map portfolio structure.

- **Clean UI**
  - Bootstrap templates with a shared `base.html` and consistent navigation.

- **Deployment-Ready Django**
  - WhiteNoise for static assets, Gunicorn for WSGI, `dj-database-url` for 12-factor DB config.
  - Local SQLite by default; Postgres via `DATABASE_URL` supported.

---

## Screens & Roles

After logging in at `/login/`, users are sent to:

- **Admin dashboard** — user/role administration, high-level oversight.  
- **Property Manager dashboard** — create, assign, and track work orders.  
- **Assistant dashboard** — operational support for PM tasks.  
- **Contractor dashboard** — view assigned orders, accept/reject, complete, or return with notes.

Django Admin is available at `/admin/` (use `superuser/superuser`).

---

## Work Order Lifecycle

Statuses are centralized in an **Enum** to avoid scattered string constants:

- **NEW** → Created by PM/Assistant  
- **ASSIGNED** → Assigned to contractor  
- **ACCEPTED** → Contractor accepts  
- **COMPLETED** → Contractor marks complete  
- **REJECTED** → Contractor declines (optionally with reason)  
- **RETURNED** → Contractor returns to creator for clarification/more info

Using an Enum keeps transitions and validation consistent.

---

## Architecture & Code Structure

```
worklogix_project/
├─ worklogix_project/                # Django project (settings, root urls)
│  ├─ settings.py                    # WhiteNoise, dj-database-url, env-driven config
│  └─ urls.py                        # Root URLConf (includes core.urls)
├─ core/                             # Main app (domain-first)
│  ├─ models/
│  │  ├─ company.py                  # Company (PM/Contractor), BusinessType, etc.
│  │  ├─ client.py                   # Client entity
│  │  ├─ unit.py                     # Unit / UnitGroup
│  │  ├─ work_order.py               # WorkOrder + WorkOrderStatus Enum
│  │  └─ __init__.py
│  ├─ views/
│  │  ├─ auth.py                     # login, redirect_after_login
│  │  ├─ work_order.py               # create/assign/accept/reject/complete/return
│  │  ├─ company.py, client.py, ...  # domain-specific views
│  ├─ templates/
│  │  ├─ core/                       # base.html, dashboards, forms
│  │  └─ ...                         # work order templates
│  ├─ urls.py                        # domain-first routes (/work-orders/... etc.)
│  ├─ forms.py                       # ModelForms (WorkOrderForm, etc.)
│  └─ admin.py                       # Django admin registrations
├─ manage.py
└─ requirements.txt                  # Django 5.x, psycopg, dj-database-url, WhiteNoise, Gunicorn
```

**Why this shape?**
- **Domain-first URLs** → predictable, human-readable endpoints,  
- **Modular view files** → smaller files, easier comprehension,  
- **Enum statuses** → single source of truth for workflow state.

---

## Technology Stack

- **Python** (tested on **3.13**) / **Django 5**  
- **SQLite** (dev) / **Postgres** (via `DATABASE_URL`)  
- **Bootstrap 5** UI  
- **WhiteNoise** (static) & **Gunicorn** (WSGI)  
- **dj-database-url** for environment-based DB config

---

## Requirements

- Python **3.13** (works on 3.11+ with Django 5)  
- pip, virtualenv  
- (Optional) Postgres 14+ if using `DATABASE_URL`  
- Windows/macOS/Linux supported

---

## Installation & Setup

> Works on Windows, macOS, and Linux. Adapt shell commands for PowerShell/CMD as needed.

1) **Clone / Extract**
```bash
# if using zip
unzip "Work Logix v2.zip"
cd "Work Logix v2/worklogix_project"
# or directly from GitHub:
# git clone https://github.com/gustavowmarques/work-logix-v2
# cd work-logix-v2/worklogix_project
```

2) **Create & activate virtualenv**
```bash
python -m venv venv
# Windows:
venv\Scriptsctivate
# macOS/Linux:
source venv/bin/activate
```

3) **Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4) **Environment (create `.env` in project root)**
```env
# .env
DEBUG=1
SECRET_KEY=dev-secret-key-change-me
ALLOWED_HOSTS=127.0.0.1,localhost
# Optional Postgres:
# DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB_NAME
```

5) **Migrate**
```bash
python manage.py migrate
```

6) **Create or use demo users**
- Use provided credentials (see top) or:
```bash
python manage.py createsuperuser
```

7) **Run**
```bash
python manage.py runserver
# http://127.0.0.1:8000/
```

8) **Static files (prod)**
```bash
python manage.py collectstatic --noinput
```

---

## Environment Variables

- `DEBUG` — `1` (dev) or `0`/unset (prod)  
- `SECRET_KEY` — **strong secret in prod**  
- `ALLOWED_HOSTS` — comma-separated hostnames for prod  
- `DATABASE_URL` — optional; enables Postgres automatically  
- Optional email (if enabling password reset):  
  - `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`

---

## Running Locally

- **Login** at `/login/` with any of the demo credentials.  
- **Role-based redirect** sends you to the correct dashboard.  
- **Work Orders**:  
  - Create via `/work-orders/create/`  
  - Assign to a contractor  
  - Contractor accepts/rejects/returns  
  - Contractor completes → PM verifies closure  
- **Admin Site**: `/admin/` with `superuser/superuser`.

---

## Seed Data / Demo Accounts

If a fixtures file is included, you can load it:

```bash
python manage.py loaddata <fixture-name>.json
```

Otherwise, use the demo credentials above or create users in `/admin/`.

---

## Domain-First URLs

**Auth & Dashboards**
- `/login/` — login  
- `/redirect-after-login/` — role-based router  
- `/dashboard/admin/` — Admin dashboard  
- `/dashboard/pm/` — Property Manager dashboard  
- `/dashboard/assistant/` — Assistant dashboard  
- `/dashboard/contractor/` — Contractor dashboard  
- `/admin/` — Django admin

**Work Orders**
- `/work-orders/` — list (role-aware filtering)  
- `/work-orders/create/` — create work order  
- `/work-orders/<int:id>/` — detail  
- `/work-orders/<int:id>/assign/` — assign to contractor  
- `/work-orders/<int:id>/accept/` — contractor accepts  
- `/work-orders/<int:id>/reject/` — contractor rejects  
- `/work-orders/<int:id>/complete/` — contractor completes  
- `/work-orders/<int:id>/return/` — contractor returns to creator

**Companies / Clients / Units**
- `/companies/`, `/clients/`, `/units/` (typical CRUD views)

---

## Security Notes

- **Auth & Roles** — Critical endpoints wrapped by login + role checks.  
- **Status Integrity** — Enum-backed statuses prevent invalid values and reduce duplication.  
- **Secrets** — Always set `SECRET_KEY`, `ALLOWED_HOSTS`, and `DATABASE_URL` in production.  
- **Passwords** — Demo passwords are for marking only; rotate before public deployment.

---

## Design Rationale & Alignment with Feedback

- **Enum for `WorkOrder.status`** to avoid scattered string literals and ensure consistent transitions.  
- **Domain-first routing** (`/work-orders/...`) rather than role-first, improving clarity and testability.  
- **Modular views** (by domain) reflect the spirit of Flask Blueprints while following Django conventions.  
- **Company vs Client** modeled separately to reduce ambiguity; contractor vs PM roles captured at the company/user level.  
- **First-time user context**: dashboards and navigational cues guide core tasks per role.

---

## Known Limitations & Future Work

- **Public Registration & Password Reset** — Disabled for the demo; accounts are admin-provisioned. Django’s built-in `PasswordResetView` and email backend can be enabled quickly for production.  
- **Internal Messaging/Inbox** — Not included in this submission. A simple `Message` model with sender/recipient/subject/body and soft-delete flags can be added later.  
- **Extended Audit & Attachments** — Basic audit is via timestamps/status; file attachments can be introduced with a storage backend if required.

---

## Deployment Notes

- **Live Demo**: https://work-logix-v2.onrender.com  
- **Repository**: https://github.com/gustavowmarques/work-logix-v2

**Environment**
- Set `DEBUG=0`, `SECRET_KEY`, `ALLOWED_HOSTS`, and (optionally) `DATABASE_URL` for Postgres.

**Static Files**
- `python manage.py collectstatic --noinput`  
- Ensure WhiteNoise is enabled in `MIDDLEWARE` and `STATIC_ROOT` is configured.

**Server**
- Typical start command:  
  `gunicorn worklogix_project.wsgi:application --bind 0.0.0.0:$PORT`

**Render / Heroku / Fly.io**
- Add a start command using Gunicorn.  
- Configure `DATABASE_URL` and secrets in the dashboard.  
- Enable auto-deploy from GitHub (optional).

---

## License / Academic Use

This codebase is submitted for academic assessment. Demo credentials are provided solely for marking and must not be used in production. If re-using the code publicly, remove demo accounts, rotate secrets, and harden configuration before deployment.

---

### Quick Start (TL;DR)

```bash
# 1) venv
python -m venv venv
venv\Scriptsctivate   # Windows
# source venv/bin/activate  # macOS/Linux

# 2) deps
pip install -r requirements.txt

# 3) env
copy NUL .env           # Windows quick create
# echo commands or edit .env with DEBUG=1, SECRET_KEY=..., etc.

# 4) db
python manage.py migrate

# 5) run
python manage.py runserver

# 6) log in
# /login  -> superuser/superuser   OR   gdasilva/LabPass1!
```
