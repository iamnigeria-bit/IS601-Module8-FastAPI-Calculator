
import os

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Calculation
from app.schemas import CalculationCreate
from app.calculation_service import create_calculation


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
        pytest.fail("Use the dedicated module10_test database")

    Base.metadata.create_all(bind=engine)

    yield engine
    engine.dispose()


@pytest.fixture
def pg_db(pg_engine):
    with pg_engine.connect() as connection:
        transaction = connection.begin()

        with Session(
            bind=connection,
            join_transaction_mode="create_savepoint"
        ) as db:
            try:
                yield db
            finally:
                transaction.rollback()


@pytest.mark.parametrize(
    "operation, expected",
    [
        ("add", 15),
        ("sub", 5),
        ("multiply", 50),
        ("divide", 2),
    ],
)
def test_postgres_calculation(pg_db, operation, expected):
    data = CalculationCreate(
        a=10,
        b=5,
        type=operation
    )

    result = create_calculation(pg_db, data)

    assert result.id is not None
    assert result.type == operation
    assert result.result == expected

    saved = pg_db.scalar(
        select(Calculation).where(
            Calculation.id == result.id
        )
    )

    assert saved is not None
    assert saved.result == expected


def test_postgres_multiple_calculations(pg_db):
    first = create_calculation(
        pg_db,
        CalculationCreate(a=20, b=10, type="add")
    )

    second = create_calculation(
        pg_db,
        CalculationCreate(a=20, b=10, type="sub")
    )

    assert first.id != second.id
    assert first.result == 30
    assert second.result == 10
