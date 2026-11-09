
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import hash_password


def create_user(db: Session, data: UserCreate) -> UserRead:
    """Create a user and store a securely hashed password."""

    user = User(
        username=data.username,
        email=str(data.email),
        password_hash=hash_password(data.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Username or email already exists."
        ) from exc

    db.refresh(user)
    return UserRead.model_validate(user)
