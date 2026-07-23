from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.schemas.addresses import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerAddressUpdate,
)
from app.security.deps import get_current_customer
from app.services.address import AddressService

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get(
    "/",
    response_model=list[CustomerAddressResponse],
    summary="List customer addresses",
    description="Returns all addresses belonging to the authenticated customer.",
)
def list_addresses(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    service = AddressService(db)
    return service.list_addresses(current_user)


@router.post(
    "/",
    response_model=CustomerAddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a customer address",
    description="Create a new delivery or service address for the authenticated customer.",
)
def create_address(
    payload: CustomerAddressCreate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    service = AddressService(db)
    return service.create_address(current_user, payload)


@router.get(
    "/{address_id}",
    response_model=CustomerAddressResponse,
    summary="Get an address by ID",
    description="Returns a single address owned by the authenticated customer.",
)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    service = AddressService(db)
    return service.get_address(current_user, address_id)


@router.put(
    "/{address_id}",
    response_model=CustomerAddressResponse,
    summary="Update a customer address",
    description="Update one or more fields for a customer address.",
)
def update_address(
    address_id: int,
    payload: CustomerAddressUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    service = AddressService(db)
    return service.update_address(current_user, address_id, payload)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a customer address",
    description="Delete an address belonging to the authenticated customer.",
)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    service = AddressService(db)
    return service.delete_address(current_user, address_id)


@router.put(
    "/{address_id}/default",
    response_model=CustomerAddressResponse,
    summary="Mark an address as default",
    description="Mark the selected address as the customer's default address.",
)
def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    service = AddressService(db)
    return service.set_default_address(current_user, address_id)
