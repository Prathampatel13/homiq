from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.services import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ServiceCreate,
    ServiceImageResponse,
    ServiceListResponse,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.service import ServiceService

router = APIRouter(prefix="/services", tags=["Services"])


# ==========================
# CATEGORY ROUTES
# ==========================

@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
def list_categories(db: Session = Depends(get_db)):
    return ServiceService(db).list_categories()


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return ServiceService(db).get_category(category_id)


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).create_category(current_user, payload)


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).update_category(
        current_user,
        category_id,
        payload,
    )


@router.delete(
    "/categories/{category_id}",
)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).delete_category(
        current_user,
        category_id,
    )


# ==========================
# SERVICE ROUTES
# ==========================

@router.get(
    "/",
    response_model=ServiceListResponse,
)
def list_services(
    search: str | None = None,
    category_id: int | None = None,
    category_name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_duration: int | None = None,
    max_duration: int | None = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    return ServiceService(db).list_services(
        search=search,
        category_id=category_id,
        category_name=category_name,
        min_price=min_price,
        max_price=max_price,
        min_duration=min_duration,
        max_duration=max_duration,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    return ServiceService(db).get_service(service_id)


@router.post(
    "/",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).create_service(
        current_user,
        payload,
    )


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).update_service(
        current_user,
        service_id,
        payload,
    )


@router.delete(
    "/{service_id}",
)
def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).delete_service(
        current_user,
        service_id,
    )


@router.post(
    "/{service_id}/image",
    response_model=ServiceImageResponse,
)
async def upload_service_image(
    service_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await ServiceService(db).upload_service_image(
        current_user,
        service_id,
        file,
    )