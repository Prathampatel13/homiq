import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models
from app.database.base import Base
from app.database.session import get_db, SessionLocal
import app.database.session as app_db_session
from app.main import app as fastapi_app
from app.models.auth import Role, User
from app.models.services import Category, Service
from app.security.passwords import hash_password

TEST_DB_PATH = Path(__file__).parent.parent / "test_homiq.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"

if TEST_DB_PATH.exists():
    try:
        os.remove(TEST_DB_PATH)
    except Exception:
        pass

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False, "isolation_level": None},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

app_db_session.engine = test_engine
app_db_session.SessionLocal.configure(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test database tables and seed baseline roles, admin user, and catalog."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        # Seed standard roles
        roles = ["customer", "technician", "company", "admin"]
        for r_name in roles:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=f"{r_name.capitalize()} role")
                db.add(role)
        db.commit()

        # Seed master admin user
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        admin_user = db.query(User).filter(User.email == "admin_master@homiq.com").first()
        if not admin_user and admin_role:
            admin_user = User(
                email="admin_master@homiq.com",
                phone="0000000000",
                full_name="Admin Master",
                password_hash=hash_password("TestPassword@1234"),
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
                is_superuser=True,
            )
            db.add(admin_user)
            db.commit()

        # Seed smoke admin user
        smoke_admin = db.query(User).filter(User.email == "smoke_admin@homiq.com").first()
        if not smoke_admin and admin_role:
            smoke_admin = User(
                email="smoke_admin@homiq.com",
                phone="0000000001",
                full_name="Smoke Admin",
                password_hash=hash_password("Admin@12345"),
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
                is_superuser=True,
            )
            db.add(smoke_admin)
            db.commit()

        # Seed lifecycle admin user
        lifecycle_admin = db.query(User).filter(User.email == "lifecycle_admin@homiq.com").first()
        if not lifecycle_admin and admin_role:
            lifecycle_admin = User(
                email="lifecycle_admin@homiq.com",
                phone="0000000002",
                full_name="Lifecycle Admin",
                password_hash=hash_password("Admin@12345"),
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
                is_superuser=True,
            )
            db.add(lifecycle_admin)
            db.commit()

        # Seed a test category & service
        cat = db.query(Category).first()
        if not cat:
            cat = Category(name="Appliance Repair", description="Repair appliances")
            db.add(cat)
            db.commit()
            db.refresh(cat)

        svc = db.query(Service).first()
        if not svc:
            svc = Service(
                name="AC Repair Service",
                description="Air conditioner repair and maintenance",
                base_price=500.0,
                duration_minutes=60,
                category_id=cat.id,
                is_active=True,
            )
            db.add(svc)
            db.commit()
    finally:
        db.close()
    yield

    # Clean up after test session
    try:
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)
    except Exception:
        pass


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client():
    return TestClient(fastapi_app)
