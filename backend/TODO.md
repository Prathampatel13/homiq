# Customer Profile Module - Implementation Steps ✅

- [x] Step 1: Update `app/core/config.py` - Add UPLOAD_DIR setting + BASE_DIR
- [x] Step 2: Update `app/models/users.py` - Enhance Customer model + add CustomerAddress model
- [x] Step 3: Create `app/schemas/customer.py` - Pydantic schemas
- [x] Step 4: Create `app/crud/customer.py` - CRUD layer
- [x] Step 5: Create `app/services/customer.py` - Service layer with image upload
- [x] Step 6: Create `app/api/customer/__init__.py` - Empty init
- [x] Step 7: Create `app/api/customer/router.py` - All customer endpoints
- [x] Step 8: Update `app/main.py` - Include customer router + static mount
- [x] Step 9: Create Alembic migration for new tables/columns

## Files Created (5)
- `app/schemas/customer.py`
- `app/crud/customer.py`
- `app/services/customer.py`
- `app/api/customer/__init__.py`
- `app/api/customer/router.py`
- `app/security/deps.py` (JWT dependency shared for future modules)
- `alembic/versions/72afc9621d89_initial_schema.py` (Fresh initial migration — Alembic fully reset)

## Files Modified (3)
- `app/core/config.py` - Added UPLOAD_DIR, BASE_DIR
- `app/models/users.py` - Enhanced Customer + added CustomerAddress
- `app/main.py` - Included customer router + static mount

## Alembic Reset (Completed)
- [x] Removed `Base.metadata.create_all(bind=engine)` from `main.py`
- [x] Dropped `alembic_version` table and all app tables from PostgreSQL
- [x] Generated fresh initial migration covering all models
- [x] Applied migration successfully (`72afc9621d89` is now head)

> **Important**: Always use `alembic upgrade head` for schema changes. Do not rely on `Base.metadata.create_all()`.

