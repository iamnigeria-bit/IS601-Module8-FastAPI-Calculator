
import os

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import User
from app.schemas import UserCreate
from app.security import verify_password
from app.user_service import create_user


@pytest.fixture(scope="module")
def pg_engine():
    url = os.getenv("TEST_DATABASE_URL")

    if not url:
        pytest.skip("PostgreSQL test database not configured")

    engine = create_engine(url)

    if (
        engine.dialect.name != "postgresql"
        or engine.url.database != "module10_test"
    ):
        engine.dispose()
        pytest.fail("A dedicated module10_test PostgreSQL database is required")

    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def pg_db(pg_engine):
    with pg_engine.connect() as connection:
        transaction = connection.begin()
        db = Session(
            bind=connection,
            join_transaction_mode="create_savepoint"
        )

        try:
            yield db
        finally:
            db.close()
            transaction.rollback()


def test_postgres_create_user(pg_db):
    data = UserCreate(
        username="postgres_student",
        email="postgres@example.com",
        password="TestPassword123!"
    )

    result = create_user(pg_db, data)

    assert result.username == "postgres_student"
    assert "password_hash" not in result.model_dump()

    saved = pg_db.scalar(
        select(User).where(User.username == "postgres_student")
    )

    assert saved is not None
    assert saved.password_hash != data.password
    assert verify_password(data.password, saved.password_hash)


def test_postgres_duplicate_username(pg_db):
    create_user(pg_db, UserCreate(
        username="duplicate_user",
        email="first@example.com",
        password="TestPassword123!"
    ))

    with pytest.raises(ValueError):
        create_user(pg_db, UserCreate(
            username="duplicate_user",
            email="second@example.com",
            password="TestPassword123!"
        ))


def test_postgres_duplicate_email(pg_db):
    create_user(pg_db, UserCreate(
        username="first_user",
        email="duplicate@example.com",
        password="TestPassword123!"
    ))

    with pytest.raises(ValueError):
        create_user(pg_db, UserCreate(
            username="second_user",
            email="duplicate@example.com",
            password="TestPassword123!"
        ))
