
import os

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Calculation
from app.schemas import CalculationCreate
from app.calculation_factory import CalculationFactory
from app.calculation_service import create_calculation


# Set up the PostgreSQL test database
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


# Use a separate transaction for each test
@pytest.fixture
def pg_db(pg_engine):
    with pg_engine.connect() as connection:
        transaction = connection.begin()

        try:
            with Session(
                bind=connection,
                join_transaction_mode="create_savepoint"
            ) as db:
                yield db
        finally:
            if transaction.is_active:
                transaction.rollback()


# Test all four operations in PostgreSQL
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


# Test saving multiple calculations
def test_postgres_multiple_calculations(pg_db):
    first = create_calculation(
        pg_db,
        CalculationCreate(
            a=20,
            b=10,
            type="add"
        )
    )

    second = create_calculation(
        pg_db,
        CalculationCreate(
            a=20,
            b=10,
            type="sub"
        )
    )

    assert first.id != second.id
    assert first.result == 30
    assert second.result == 10


# NEW TEST 1:
# Verify invalid input never creates a database record
def test_postgres_invalid_input_not_saved(pg_db):
    before = pg_db.scalar(
        select(func.count()).select_from(Calculation)
    )

    invalid_cases = [
        {
            "a": 10,
            "b": 0,
            "type": "divide"
        },
        {
            "a": 10,
            "b": 5,
            "type": "power"
        },
        {
            "a": float("inf"),
            "b": 5,
            "type": "add"
        },
    ]

    for invalid_data in invalid_cases:
        with pytest.raises(ValidationError):
            data = CalculationCreate(**invalid_data)
            create_calculation(pg_db, data)

    after = pg_db.scalar(
        select(func.count()).select_from(Calculation)
    )

    assert after == before


# NEW TEST 2:
# Verify failed database transactions roll back safely
def test_postgres_failed_transaction_rollback(
    pg_db,
    monkeypatch
):
    before = pg_db.scalar(
        select(func.count()).select_from(Calculation)
    )

    # Deliberately create an invalid result
    # to trigger PostgreSQL's NOT NULL constraint.
    class BrokenOperation:
        def calculate(self, a, b):
            return None

    # Temporarily replace the factory operation
    with monkeypatch.context() as patch:
        patch.setattr(
            CalculationFactory,
            "create",
            classmethod(
                lambda cls, calculation_type: BrokenOperation()
            )
        )

        with pytest.raises(IntegrityError):
            create_calculation(
                pg_db,
                CalculationCreate(
                    a=10,
                    b=5,
                    type="add"
                )
            )

    # Verify the failed transaction was rolled back
    after = pg_db.scalar(
        select(func.count()).select_from(Calculation)
    )

    assert after == before

    # Verify the session can still save valid data
    recovered = create_calculation(
        pg_db,
        CalculationCreate(
            a=10,
            b=5,
            type="add"
        )
    )

    assert recovered.result == 15

    saved = pg_db.scalar(
        select(Calculation).where(
            Calculation.id == recovered.id
        )
    )

    assert saved is not None
    assert saved.result == 15
