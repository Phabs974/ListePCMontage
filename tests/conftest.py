import sys
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append("backend")

from app.api.deps import get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_user(db_session):
    user = User(
        id=uuid.uuid4(),
        username="admin",
        password_hash=hash_password("secret"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def vendor_user(db_session):
    user = User(
        id=uuid.uuid4(),
        username="vendor",
        password_hash=hash_password("secret"),
        role=UserRole.VENDOR,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def builder_user(db_session):
    user = User(
        id=uuid.uuid4(),
        username="builder",
        password_hash=hash_password("secret"),
        role=UserRole.BUILDER,
    )
    db_session.add(user)
    db_session.commit()
    return user
