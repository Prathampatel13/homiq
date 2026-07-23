from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.users import Customer
from app.models.addresses import CustomerAddress


class CustomerCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Customer Profile ──────────────────────────────────────────────

    def get_by_user_id(self, user_id: int) -> Optional[Customer]:
        return self.db.scalar(
            select(Customer).where(Customer.user_id == user_id)
        )

    def get_by_customer_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.get(Customer, customer_id)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def create(self, user_id: int) -> Customer:
        customer = Customer(user_id=user_id)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(
        self, customer_id: int, data: dict[str, Any]
    ) -> Optional[Customer]:
        stmt = (
            update(Customer)
            .where(Customer.id == customer_id)
            .values(**data)
            .returning(Customer)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one_or_none()

    def update_user_name(self, user_id: int, full_name: str) -> None:
        user = self.db.get(User, user_id)
        if user:
            user.full_name = full_name
            self.db.commit()

    # ── Addresses ─────────────────────────────────────────────────────

    def get_addresses(self, customer_id: int) -> list[CustomerAddress]:
        result = self.db.execute(
            select(CustomerAddress)
            .where(CustomerAddress.customer_id == customer_id)
            .order_by(CustomerAddress.is_default.desc(), CustomerAddress.id)
        )
        return list(result.scalars().all())

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
        # If this is the first address or marked as default, unset other defaults
        if data.get("is_default"):
            self._unset_default_addresses(customer_id)

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

        # If setting as default, unset other defaults first
        if data.get("is_default"):
            self._unset_default_addresses(customer_id)

        for key, value in data.items():
            setattr(address, key, value)
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete_address(
        self, customer_id: int, address_id: int
    ) -> bool:
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

    # ── Helpers ───────────────────────────────────────────────────────

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

