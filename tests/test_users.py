
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import User
from app.schemas import UserCreate
from app.security import hash_password, verify_password
from app.user_service import create_user


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def test_password_hashing():
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="student1",
            email="invalid-email",
            password="TestPassword123!"
        )


def test_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            username="student1",
            email="student1@example.com",
            password="123"
        )


def test_create_user(db):
    data = UserCreate(
        username="student1",
        email="student1@example.com",
        password="TestPassword123!"
    )

    result = create_user(db, data)

    assert result.username == "student1"
    assert "password_hash" not in result.model_dump()

    saved = db.scalar(
        select(User).where(User.username == "student1")
    )

    assert saved is not None
    assert saved.password_hash != data.password
    assert verify_password(data.password, saved.password_hash)


def test_duplicate_username(db):
    create_user(db, UserCreate(
        username="student1",
        email="student1@example.com",
        password="TestPassword123!"
    ))

    with pytest.raises(ValueError):
        create_user(db, UserCreate(
            username="student1",
            email="other@example.com",
            password="AnotherPass123!"
        ))


def test_duplicate_email(db):
    create_user(db, UserCreate(
        username="student1",
        email="student1@example.com",
        password="TestPassword123!"
    ))

    with pytest.raises(ValueError):
        create_user(db, UserCreate(
            username="student2",
            email="student1@example.com",
            password="AnotherPass123!"
        ))
