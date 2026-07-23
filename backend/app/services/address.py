from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.address import AddressCRUD
from app.crud.customer import CustomerCRUD
from app.models.auth import User
from app.schemas.addresses import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerAddressUpdate,
)


class AddressService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = AddressCRUD(db)
        self.customer_crud = CustomerCRUD(db)

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            customer = self.customer_crud.create(current_user.id)
        return customer.id

    def list_addresses(self, current_user: User) -> List[CustomerAddressResponse]:
        customer_id = self._get_customer_id(current_user)
        addresses = self.crud.list_addresses(customer_id)
        return [CustomerAddressResponse.model_validate(address) for address in addresses]

    def get_address(
        self, current_user: User, address_id: int
    ) -> CustomerAddressResponse:
        customer_id = self._get_customer_id(current_user)
        address = self.crud.get_address(customer_id, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return CustomerAddressResponse.model_validate(address)

    def create_address(
        self, current_user: User, payload: CustomerAddressCreate
    ) -> CustomerAddressResponse:
        customer_id = self._get_customer_id(current_user)
        data = payload.model_dump()
        address = self.crud.create_address(customer_id, data)
        return CustomerAddressResponse.model_validate(address)

    def update_address(
        self,
        current_user: User,
        address_id: int,
        payload: CustomerAddressUpdate,
    ) -> CustomerAddressResponse:
        customer_id = self._get_customer_id(current_user)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        address = self.crud.update_address(customer_id, address_id, data)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return CustomerAddressResponse.model_validate(address)

    def delete_address(self, current_user: User, address_id: int) -> dict[str, str]:
        customer_id = self._get_customer_id(current_user)
        deleted = self.crud.delete_address(customer_id, address_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return {"message": "Address deleted successfully"}

    def set_default_address(
        self, current_user: User, address_id: int
    ) -> CustomerAddressResponse:
        customer_id = self._get_customer_id(current_user)
        address = self.crud.set_default_address(customer_id, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return CustomerAddressResponse.model_validate(address)
