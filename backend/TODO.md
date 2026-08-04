# HomiQ Backend — Module Implementation Plan

## Module 1: Company Module

- [x] Analyze codebase (models, schemas, CRUD, services, routers, deps, migrations) — Company
- [x] Create `app/crud/company.py` — CompanyCRUD
- [x] Create `app/schemas/company.py` — Company schemas
- [x] Create `app/services/company.py` — CompanyService
- [x] Create `app/api/company/router.py` — company endpoints
- [x] Add `get_current_company` dependency in `app/security/deps.py`
- [x] Auto-create Company profile on registration in `app/crud/user.py`
- [x] Register company router in `app/main.py`
- [x] Export `CompanyService` in `app/services/__init__.py`
- [x] Verify syntax (AST parse passed for all modified/created files)
- [x] Generate API documentation + testing guide

## Module 2: Technician Remaining Module

### Plan Steps
- [x] Add `get_technician_jobs` CRUD method in `app/crud/technician.py`
- [x] Add technician job/earnings/availability schemas in `app/schemas/technician.py`
- [x] Add service methods (get_my_jobs, earnings, availability) in `app/services/technician.py`
- [x] Add endpoints in `app/api/technician/router.py` (jobs, earnings, availability)
- [x] Enforce technician role on technician-scoped endpoints
- [x] Verify syntax (AST parse)
- [x] Verify full app import + route registration (all technician routes present)
- [x] End-to-end technician smoke test passed (8/8)
- [x] Create `technician_smoke_test.py`
- [x] Update TODO.md — mark Module 2 complete

## Module 3: Jobs Module
## Module 4: Notifications Module
## Module 5: QR Verification Module
## Module 6: Coupon Module
## Module 7: Invoice Module
## Module 8: Reports & Analytics
## Module 9: Final End-to-End Testing
