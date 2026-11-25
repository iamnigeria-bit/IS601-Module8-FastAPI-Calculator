import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from main import app
from app.database import Base
from app.models import User, Calculation
from app.routes import get_db
from app.security import verify_password


@pytest.fixture
def db(tmp_path):
    url = os.getenv("TEST_DATABASE_URL")

    if url:
        engine = create_engine(url)

        if (
            engine.dialect.name != "postgresql"
            or engine.url.database != "module10_test"
        ):
            engine.dispose()
            pytest.fail("Use the dedicated PostgreSQL test database")
    else:
        engine = create_engine(
            f"sqlite:///{tmp_path / 'module12.db'}",
            connect_args={"check_same_thread": False},
        )

    Base.metadata.create_all(bind=engine)

    try:
        if url:
            with engine.connect() as connection:
                transaction = connection.begin()

                try:
                    with Session(
                        bind=connection,
                        join_transaction_mode="create_savepoint",
                    ) as session:
                        yield session
                finally:
                    if transaction.is_active:
                        transaction.rollback()
        else:
            with Session(engine) as session:
                yield session
    finally:
        engine.dispose()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def user_data():
    return {
        "username": "module12_student",
        "email": "module12student@example.com",
        "password": "TestPassword123!",
    }


# USER REGISTRATION

def test_register_user(client, db, user_data):
    response = client.post("/users/register", json=user_data)

    assert response.status_code == 201

    body = response.json()

    assert body["username"] == user_data["username"]
    assert body["email"] == user_data["email"]
    assert "password" not in body
    assert "password_hash" not in body

    db.expire_all()
    saved = db.get(User, body["id"])

    assert saved is not None
    assert saved.password_hash != user_data["password"]

    assert verify_password(
        user_data["password"],
        saved.password_hash,
    )


# DUPLICATE ACCOUNTS

def test_duplicate_email(client, user_data):
    assert client.post(
        "/users/register", json=user_data
    ).status_code == 201

    duplicate = {
        **user_data,
        "username": "another_student",
    }

    response = client.post("/users/register", json=duplicate)

    assert response.status_code == 409
    assert "error" in response.json()


def test_duplicate_username(client, user_data):
    assert client.post(
        "/users/register", json=user_data
    ).status_code == 201

    duplicate = {
        **user_data,
        "email": "another@example.com",
    }

    response = client.post("/users/register", json=duplicate)

    assert response.status_code == 409


# LOGIN

def test_login_success(client, user_data):
    registered = client.post(
        "/users/register", json=user_data
    )

    assert registered.status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == registered.json()["id"]
    assert "password_hash" not in response.json()


def test_login_wrong_password(client, user_data):
    assert client.post(
        "/users/register", json=user_data
    ).status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/users/login",
        json={
            "email": "unknown@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 401


# USER VALIDATION

@pytest.mark.parametrize(
    "field, value",
    [
        ("username", "ab"),
        ("email", "invalid-email"),
        ("password", "123"),
    ],
)
def test_invalid_registration(client, user_data, field, value):
    invalid = {**user_data, field: value}

    response = client.post("/users/register", json=invalid)

    assert response.status_code == 400
    assert "error" in response.json()


# CALCULATION OPERATIONS

@pytest.mark.parametrize(
    "operation, expected",
    [
        ("add", 15),
        ("sub", 5),
        ("multiply", 50),
        ("divide", 2),
    ],
)
def test_create_calculation(client, db, operation, expected):
    response = client.post(
        "/calculations",
        json={"a": 10, "b": 5, "type": operation},
    )

    assert response.status_code == 201

    body = response.json()

    assert body["result"] == expected

    db.expire_all()
    saved = db.get(Calculation, body["id"])

    assert saved is not None
    assert saved.result == expected


# COMPLETE BREAD LIFECYCLE

def test_calculation_bread(client, db):
    created = client.post(
        "/calculations",
        json={"a": 20, "b": 5, "type": "multiply"},
    )

    assert created.status_code == 201

    calculation_id = created.json()["id"]
    endpoint = f"/calculations/{calculation_id}"

    # Browse
    browsed = client.get("/calculations")

    assert browsed.status_code == 200
    assert any(
        item["id"] == calculation_id
        for item in browsed.json()
    )

    # Read
    retrieved = client.get(endpoint)

    assert retrieved.status_code == 200
    assert retrieved.json()["result"] == 100

    # Edit
    edited = client.put(
        endpoint,
        json={"a": 50, "b": 10, "type": "divide"},
    )

    assert edited.status_code == 200
    assert edited.json()["result"] == 5

    db.expire_all()
    saved = db.get(Calculation, calculation_id)

    assert saved.result == 5

    # Delete
    deleted = client.delete(endpoint)

    assert deleted.status_code == 204
    assert deleted.content == b""

    # Confirm deletion
    assert client.get(endpoint).status_code == 404

    db.expire_all()
    assert db.get(Calculation, calculation_id) is None


# INVALID CALCULATION DATA

@pytest.mark.parametrize(
    "payload",
    [
        {"a": 10, "b": 0, "type": "divide"},
        {"a": 10, "b": 5, "type": "power"},
        {"a": "invalid", "b": 5, "type": "add"},
        {"a": 10, "type": "add"},
    ],
)
def test_invalid_calculation(client, db, payload):
    before = db.scalar(
        select(func.count()).select_from(Calculation)
    )

    response = client.post("/calculations", json=payload)

    assert response.status_code == 400
    assert "error" in response.json()

    after = db.scalar(
        select(func.count()).select_from(Calculation)
    )

    assert before == after


# INVALID UPDATE

def test_invalid_update(client, db):
    created = client.post(
        "/calculations",
        json={"a": 10, "b": 5, "type": "add"},
    )

    assert created.status_code == 201

    calculation_id = created.json()["id"]
    endpoint = f"/calculations/{calculation_id}"

    response = client.put(
        endpoint,
        json={"a": 10, "b": 0, "type": "divide"},
    )

    assert response.status_code == 400

    db.expire_all()
    saved = db.get(Calculation, calculation_id)

    assert saved.result == 15
    assert saved.type == "add"


# MISSING RECORDS

def test_missing_calculation(client):
    endpoint = "/calculations/-1"

    assert client.get(endpoint).status_code == 404

    assert client.put(
        endpoint,
        json={"a": 10, "b": 5, "type": "add"},
    ).status_code == 404

    assert client.delete(endpoint).status_code == 404
