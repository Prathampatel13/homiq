from typing import Any, Optional

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.models.services import Category, Service


class ServicesCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Categories ─────────────────────────────────────────────────────

    def create_category(self, data: dict[str, Any]) -> Category:
        category = Category(**data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: int) -> Optional[Category]:
        return self.db.get(Category, category_id)

    def get_category_by_name(self, name: str) -> Optional[Category]:
        return self.db.scalar(
            select(Category).where(Category.name.ilike(f"%{name}%"))
        )

    def update_category(self, category_id: int, data: dict[str, Any]) -> Optional[Category]:
        if not data:
            return self.get_category(category_id)

        stmt = (
            update(Category)
            .where(Category.id == category_id)
            .values(**data)
            .returning(Category)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one_or_none()

    def delete_category(self, category_id: int) -> bool:
        category = self.get_category(category_id)
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True

    def list_categories(self) -> list[Category]:
        result = self.db.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    # ── Services ───────────────────────────────────────────────────────

    def create_service(self, data: dict[str, Any]) -> Service:
        data.setdefault("duration_minutes", 0)
        data.setdefault("is_active", True)
        service = Service(**data)
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def get_service(self, service_id: int) -> Optional[Service]:
        return self.db.get(Service, service_id)

    def update_service(self, service_id: int, data: dict[str, Any]) -> Optional[Service]:
        if not data:
            return self.get_service(service_id)

        stmt = (
            update(Service)
            .where(Service.id == service_id)
            .values(**data)
            .returning(Service)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one_or_none()

    def delete_service(self, service_id: int) -> bool:
        service = self.get_service(service_id)
        if not service:
            return False
        self.db.delete(service)
        self.db.commit()
        return True

    def list_services(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Service], int]:
        stmt = select(Service)
        count_stmt = select(func.count(Service.id))

        if category_name:
            stmt = stmt.join(Category)
            count_stmt = count_stmt.join(Category)

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Service.name.ilike(search_term),
                    Service.description.ilike(search_term),
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    Service.name.ilike(search_term),
                    Service.description.ilike(search_term),
                )
            )

        if category_id is not None:
            stmt = stmt.where(Service.category_id == category_id)
            count_stmt = count_stmt.where(Service.category_id == category_id)

        if category_name:
            count_stmt = count_stmt.where(Category.name.ilike(f"%{category_name}%"))
            stmt = stmt.where(Category.name.ilike(f"%{category_name}%"))

        if min_price is not None:
            stmt = stmt.where(Service.base_price >= min_price)
            count_stmt = count_stmt.where(Service.base_price >= min_price)

        if max_price is not None:
            stmt = stmt.where(Service.base_price <= max_price)
            count_stmt = count_stmt.where(Service.base_price <= max_price)

        if min_duration is not None:
            stmt = stmt.where(Service.duration_minutes >= min_duration)
            count_stmt = count_stmt.where(Service.duration_minutes >= min_duration)

        if max_duration is not None:
            stmt = stmt.where(Service.duration_minutes <= max_duration)
            count_stmt = count_stmt.where(Service.duration_minutes <= max_duration)

        stmt = stmt.where(Service.is_active.is_(True))
        count_stmt = count_stmt.where(Service.is_active.is_(True))

        total = self.db.scalar(count_stmt) or 0
        offset = (page - 1) * per_page
        result = self.db.execute(
            stmt.order_by(Service.name).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), int(total)
