from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models

from app.api.auth.router import router as auth_router
from app.api.customer.router import router as customer_router
from app.api.address.router import router as address_router
from app.api.services.router import router as services_router
from app.api.technician.router import router as technician_router

from app.core.config import BASE_DIR, settings

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
app.include_router(customer_router)
app.include_router(address_router)
app.include_router(technician_router)
app.include_router(services_router)


@app.get("/health")
def health():
    return {"status": "ok"}
