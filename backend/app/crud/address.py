from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.addresses import CustomerAddress


class AddressCRUD:
    def __init__(self, db: Session):
        self.db = db

    def list_addresses(self, customer_id: int) -> list[CustomerAddress]:
        result = self.db.execute(
            select(CustomerAddress)
            .where(CustomerAddress.customer_id == customer_id)
            .order_by(CustomerAddress.is_default.desc(), CustomerAddress.id)
        )
        return result.scalars().all()

    def get_address(
        self, customer_id: int, address_id: int
    ) -> Optional[CustomerAddress]:
        return self.db.scalar(
            select(CustomerAddress).where(
                CustomerAddress.id == address_id,
                CustomerAddress.customer_id == customer_id,
            )
        )

    def create_address(
        self, customer_id: int, data: dict[str, Any]
    ) -> CustomerAddress:
        if data.get("is_default"):
            self._unset_default_addresses(customer_id)
        elif not self._has_default_address(customer_id):
            data["is_default"] = True

        address = CustomerAddress(customer_id=customer_id, **data)
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        return address

    def update_address(
        self, customer_id: int, address_id: int, data: dict[str, Any]
    ) -> Optional[CustomerAddress]:
        address = self.get_address(customer_id, address_id)
        if not address:
            return None

        if data.get("is_default"):
            self._unset_default_addresses(customer_id)

        for key, value in data.items():
            setattr(address, key, value)

        self.db.commit()
        self.db.refresh(address)
        return address

    def delete_address(self, customer_id: int, address_id: int) -> bool:
        address = self.get_address(customer_id, address_id)
        if not address:
            return False

        self.db.delete(address)
        self.db.commit()
        return True

    def set_default_address(
        self, customer_id: int, address_id: int
    ) -> Optional[CustomerAddress]:
        address = self.get_address(customer_id, address_id)
        if not address:
            return None

        self._unset_default_addresses(customer_id)
        address.is_default = True
        self.db.commit()
        self.db.refresh(address)
        return address

    def _unset_default_addresses(self, customer_id: int) -> None:
        stmt = (
            update(CustomerAddress)
            .where(
                CustomerAddress.customer_id == customer_id,
                CustomerAddress.is_default == True,
            )
            .values(is_default=False)
        )
        self.db.execute(stmt)
        self.db.flush()

    def _has_default_address(self, customer_id: int) -> bool:
        return self.db.scalar(
            select(CustomerAddress)
            .where(
                CustomerAddress.customer_id == customer_id,
                CustomerAddress.is_default == True,
            )
            .limit(1)
        ) is not None
