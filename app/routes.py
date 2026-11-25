from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Calculation
from app.schemas import (
    UserCreate,
    UserRead,
    CalculationCreate,
    CalculationRead,
)
from app.security import verify_password
from app.user_service import create_user
from app.calculation_service import create_calculation
from app.calculation_factory import CalculationFactory

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


# USER REGISTRATION

@router.post(
    "/users/register",
    response_model=UserRead,
    status_code=201,
    tags=["Users"],
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


# USER LOGIN

@router.post(
    "/users/login",
    response_model=UserRead,
    tags=["Users"],
)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User).where(User.email == str(data.email))
    )

    if user is None or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return UserRead.model_validate(user)


# BROWSE

@router.get(
    "/calculations",
    response_model=list[CalculationRead],
    tags=["Calculations"],
)
def browse_calculations(db: Session = Depends(get_db)):
    return db.scalars(
        select(Calculation).order_by(Calculation.id)
    ).all()


# READ

@router.get(
    "/calculations/{id}",
    response_model=CalculationRead,
    tags=["Calculations"],
)
def read_calculation(id: int, db: Session = Depends(get_db)):
    calculation = db.get(Calculation, id)

    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found.",
        )

    return calculation


# ADD

@router.post(
    "/calculations",
    response_model=CalculationRead,
    status_code=201,
    tags=["Calculations"],
)
def add_calculation(
    data: CalculationCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_calculation(db, data)
    except (ValueError, OverflowError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# EDIT

@router.put(
    "/calculations/{id}",
    response_model=CalculationRead,
    tags=["Calculations"],
)
def edit_calculation(
    id: int,
    data: CalculationCreate,
    db: Session = Depends(get_db),
):
    calculation = db.get(Calculation, id)

    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found.",
        )

    try:
        operation = CalculationFactory.create(data.type)
        result = operation.calculate(data.a, data.b)

        calculation.a = data.a
        calculation.b = data.b
        calculation.type = data.type
        calculation.result = result

        db.commit()
    except (ValueError, OverflowError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise

    db.refresh(calculation)
    return calculation


# DELETE

@router.delete(
    "/calculations/{id}",
    status_code=204,
    tags=["Calculations"],
)
def delete_calculation(
    id: int,
    db: Session = Depends(get_db),
):
    calculation = db.get(Calculation, id)

    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found.",
        )

    try:
        db.delete(calculation)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response(status_code=204)
