
from sqlalchemy.orm import Session

from app.calculation_factory import CalculationFactory
from app.models import Calculation
from app.schemas import CalculationCreate, CalculationRead


def create_calculation(
    db: Session,
    data: CalculationCreate
) -> CalculationRead:
    # Select the correct mathematical operation
    operation = CalculationFactory.create(data.type)

    # Calculate the result
    answer = operation.calculate(data.a, data.b)

    # Create a database record
    calculation = Calculation(
        a=data.a,
        b=data.b,
        type=data.type,
        result=answer
    )

    # Save the calculation
    db.add(calculation)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    # Retrieve the saved record
    db.refresh(calculation)

    # Return validated data
    return CalculationRead.model_validate(calculation)
