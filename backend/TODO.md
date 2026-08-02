# HomiQ Backend Fix Plan — Phase 1 (Auth, Customer, Address, Booking)

## Steps

- [x] Analyze codebase (models, schemas, CRUD, services, routers, integrations, migrations)
- [x] Add missing `__init__.py` files to all packages
- [x] Fix `app/security/passwords.py` — replace passlib+bcrypt 4.x incompatibility with direct bcrypt
- [x] Fix `app/integrations/__init__.py` — lazy imports to avoid uninstalled `cloudinary` breaking `app.main`
- [x] Merge duplicate Address schemas — canonical in `schemas/addresses.py`, re-export from `schemas/customer.py`
- [x] Remove dead `app/services/address.py` (CustomerService is canonical; imported nonexistent `app.crud.address`)
- [x] Consolidate Address CRUD into `app/crud/customer.py` (deleted dead `app/crud/address.py`)
- [x] Fix `CustomerAddress.bookings` relationship — add `passive_deletes=True` so DB `ON DELETE CASCADE` is used instead of ORM NULL-ing a NOT NULL column
- [x] Add delete-address guard in `CustomerService.delete_address` — reject deleting addresses linked to bookings (avoids silent booking-history loss)
- [x] Auto-create Customer/Technician profile during registration (fixes User↔Customer mapping)
- [x] Add role-aware top-level `GET /dashboard`
- [x] Fix `POST /payments/create-order` to fall back to `estimated_price` (no longer rejects `final_price`-less bookings)
- [x] Fix dashboard `payment_status` enum comparisons (string vs SAEnum member)
- [x] Enforce customer role on `/customer/*` endpoints via `get_current_customer`
- [x] Verify syntax + imports + routes — ALL CHECKS PASSED (101 files, `app.main` imports, all routes register)
- [x] Smoke tests green — customer (15/15), admin policy, phase 2 (booking/payment/dashboard/invoice)
- [x] Generate final report (modified/removed/merged files, remaining issues, test sequence)

