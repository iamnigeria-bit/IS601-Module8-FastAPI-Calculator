
import pytest

from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Calculation
from app.schemas import CalculationCreate
from app.calculation_factory import CalculationFactory
from app.calculation_service import create_calculation


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


# Test all four mathematical operations
@pytest.mark.parametrize(
    "operation, expected",
    [
        ("add", 15),
        ("sub", 5),
        ("multiply", 50),
        ("divide", 2),
    ],
)
def test_factory_operations(operation, expected):
    calculator = CalculationFactory.create(operation)
    assert calculator.calculate(10, 5) == expected


# Test unsupported operations
def test_invalid_factory_operation():
    with pytest.raises(ValueError):
        CalculationFactory.create("power")


# Test division by zero
def test_division_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type="divide")


# Test invalid operation validation
def test_invalid_calculation_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=5, type="power")


# Test invalid numeric values
def test_invalid_number():
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=float("inf"),
            b=5,
            type="add"
        )


# Test calculation storage in SQLite
@pytest.mark.parametrize(
    "operation, expected",
    [
        ("add", 15),
        ("sub", 5),
        ("multiply", 50),
        ("divide", 2),
    ],
)
def test_save_calculation(db, operation, expected):
    data = CalculationCreate(
        a=10,
        b=5,
        type=operation
    )

    result = create_calculation(db, data)

    assert result.id is not None
    assert result.type == operation
    assert result.result == expected

    saved = db.scalar(
        select(Calculation).where(
            Calculation.id == result.id
        )
    )

    assert saved is not None
    assert saved.result == expected
