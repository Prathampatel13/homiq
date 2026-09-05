from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import app.models

from app.api.auth.router import router as auth_router, users_router
from app.api.bookings.router import router as booking_router
from app.api.customer.router import router as customer_router
from app.api.services.router import router as services_router
from app.api.technician.router import router as technician_router, technicians_router
from app.api.payments.router import router as payment_router
from app.api.coupons.router import router as coupons_router
from app.api.invoices.router import router as invoices_router
from app.api.reviews.router import router as reviews_router
from app.api.notifications.router import router as notifications_router
from app.api.admin.router import router as admin_router
from app.api.company.router import router as company_router, companies_router
from app.api.jobs.router import router as jobs_router
from app.api.media.router import router as media_router
from app.api.reports.router import router as reports_router
from app.api.search.router import router as search_router
from app.api.tasks.router import router as tasks_router
from app.api.websocket.router import router as websocket_router
from app.api.security.router import router as security_router
from app.api.monitoring.router import router as monitoring_router
from app.middleware.security import SecurityHeadersMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import BASE_DIR, settings
from app.database.base import Base
from app.database.session import engine, get_db
from app.models.auth import User
from app.security.deps import get_current_user

Base.metadata.create_all(bind=engine)

def seed_initial_data():
    from app.database.session import SessionLocal
    from app.models.auth import Role
    db = SessionLocal()
    try:
        roles_data = [
            ("customer", "Customer account"),
            ("technician", "Technician account"),
            ("company", "Service Company account"),
            ("admin", "System Administrator"),
        ]
        for r_name, r_desc in roles_data:
            existing = db.query(Role).filter(Role.name == r_name).first()
            if not existing:
                db.add(Role(name=r_name, description=r_desc))
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning(f"Initial data auto-seeding skipped: {exc}")
    finally:
        db.close()

seed_initial_data()

app = FastAPI(
    title="HomiQ Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
async def startup_event():
    import asyncio
    from app.core.websockets import manager
    try:
        manager.loop = asyncio.get_running_loop()
    except Exception:
        pass

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded profile images
upload_dir = Path(BASE_DIR) / settings.UPLOAD_DIR
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=str(upload_dir)), name="uploads")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(booking_router)
app.include_router(customer_router)
app.include_router(technician_router)
app.include_router(technicians_router)
app.include_router(services_router)
app.include_router(payment_router)
app.include_router(coupons_router)
app.include_router(invoices_router)
app.include_router(reviews_router)
app.include_router(notifications_router)
app.include_router(admin_router)
app.include_router(company_router)
app.include_router(companies_router)
app.include_router(jobs_router)
app.include_router(media_router)
app.include_router(reports_router)
app.include_router(search_router)
app.include_router(tasks_router)
app.include_router(websocket_router)
app.include_router(security_router)
app.include_router(monitoring_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dashboard")
def role_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Role-aware dashboard.

    - Superuser  -> /admin/dashboard data
    - Customer   -> /customer/dashboard data
    - Technician -> /technician/dashboard data
    """
    from app.services.admin_dashboard import AdminDashboardService
    from app.services.customer_dashboard import CustomerDashboardService
    from app.services.technician_dashboard import TechnicianDashboardService

    if current_user.is_superuser:
        result = AdminDashboardService(db).get_dashboard()
    elif current_user.role and current_user.role.name.lower() == "technician":
        result = TechnicianDashboardService(db).get_dashboard(current_user)
    else:
        result = CustomerDashboardService(db).get_dashboard(current_user)
    return result

