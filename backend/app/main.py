from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import app.models

from app.api.auth.router import router as auth_router
from app.api.bookings.router import router as booking_router
from app.api.customer.router import router as customer_router
from app.api.services.router import router as services_router
from app.api.technician.router import router as technician_router
from app.api.payments.router import router as payment_router
from app.api.coupons.router import router as coupons_router
from app.api.invoices.router import router as invoices_router
from app.api.reviews.router import router as reviews_router
from app.api.notifications.router import router as notifications_router
from app.api.tracking.router import router as tracking_router
from app.api.admin.router import router as admin_router

from app.core.config import BASE_DIR, settings
from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user

app = FastAPI(
    title="HomiQ Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded profile images
upload_dir = Path(BASE_DIR) / settings.UPLOAD_DIR
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=str(upload_dir)), name="uploads")

app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(customer_router)
app.include_router(technician_router)
app.include_router(services_router)
app.include_router(payment_router)
app.include_router(coupons_router)
app.include_router(invoices_router)
app.include_router(reviews_router)
app.include_router(notifications_router)
app.include_router(tracking_router)
app.include_router(admin_router)


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

