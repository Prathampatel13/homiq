from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.schemas.customer import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerAddressUpdate,
    CustomerProfileResponse,
    CustomerProfileUpdate,
    ProfileImageResponse,
)
from app.security.deps import get_current_user
from app.services.customer import CustomerService

router = APIRouter(prefix="/customer", tags=["Customer Profile"])


# ── Profile Endpoints ─────────────────────────────────────────────────


@router.get(
    "/profile",
    response_model=CustomerProfileResponse,
    summary="Get customer profile",
    description="Returns the authenticated customer's profile information including all saved addresses.",
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch the authenticated customer's profile with addresses."""
    service = CustomerService(db)
    return service.get_profile(current_user)


@router.put(
    "/profile",
    response_model=CustomerProfileResponse,
    summary="Update customer profile",
    description="Update profile fields such as name, phone, address, language, etc. Only provided fields are updated.",
)
def update_profile(
    payload: CustomerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the customer's profile. Omitting a field leaves it unchanged."""
    service = CustomerService(db)
    return service.update_profile(current_user, payload)


@router.post(
    "/profile/image",
    response_model=ProfileImageResponse,
    summary="Upload profile image",
    description="Upload a profile image (JPEG, PNG, GIF, WebP). Max file size: 5 MB.",
)
async def upload_profile_image(
    file: UploadFile = File(..., description="Profile image file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a new profile image for the authenticated customer."""
    service = CustomerService(db)
    return await service.upload_profile_image(current_user, file)


# ── Address Endpoints ─────────────────────────────────────────────────


@router.get(
    "/addresses",
    response_model=list[CustomerAddressResponse],
    summary="List all addresses",
    description="Returns all saved addresses for the authenticated customer, with default address first.",
)
def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all addresses for the authenticated customer."""
    service = CustomerService(db)
    return service.get_addresses(current_user)


@router.post(
    "/addresses",
    response_model=CustomerAddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new address",
    description="Create a new address for the authenticated customer. Supports lat/lng and marking as default.",
)
def create_address(
    payload: CustomerAddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new address to the customer's profile."""
    service = CustomerService(db)
    return service.create_address(current_user, payload)


@router.get(
    "/addresses/{address_id}",
    response_model=CustomerAddressResponse,
    summary="Get address by ID",
    description="Returns a specific address by its ID, scoped to the authenticated customer.",
)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single address by ID."""
    service = CustomerService(db)
    return service.get_address(current_user, address_id)


@router.put(
    "/addresses/{address_id}",
    response_model=CustomerAddressResponse,
    summary="Update an address",
    description="Update specific fields of an existing address. Only provided fields are updated.",
)
def update_address(
    address_id: int,
    payload: CustomerAddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing address by ID."""
    service = CustomerService(db)
    return service.update_address(current_user, address_id, payload)


@router.delete(
    "/addresses/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an address",
    description="Deletes an address by its ID. Returns a confirmation message.",
)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an address by ID."""
    service = CustomerService(db)
    return service.delete_address(current_user, address_id)


@router.put(
    "/addresses/{address_id}/default",
    response_model=CustomerAddressResponse,
    summary="Set address as default",
    description="Marks a specific address as the default shipping/contact address.",
)
def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set an address as the default address for the customer."""
    service = CustomerService(db)
    return service.set_default_address(current_user, address_id)

