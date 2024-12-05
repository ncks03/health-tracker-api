# import pytest
# import os
#
# from main import app
# from fastapi.testclient import TestClient
#
# os.environ["DB_URL"] = "sqlite:///:memory:"
#
# client = TestClient(app)
#
# @pytest.mark.asyncio
# async def test_create_user():
#     customer = {
#         "gym_id":1, "first_name":'John', "last_name":'Doe', "birth_date":"1990-01-01",
#         "gender":'male', "length":180, "activity_level":10.0
#     }
#
#     result = client.post("/customers", json=customer)
#
#     assert result.status_code == 201
#
# @pytest.mark.asyncio
# async def test_get_user():
#     response = client.get("/customers/1")
#     assert response.status_code == 200
#     assert response.json() == {}

# i
import os
from datetime import datetime, date, timedelta

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app
from schemas.dtos import CustomerDTO
from services.functions import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models.entities import Base, Customer, Gym, Goal, Progress

load_dotenv()

# Create a single engine for the entire test session
test_url = os.getenv("TEST_DB_URL")
test_engine = create_engine(
    test_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Ensures the same connection is used
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables once before tests
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency for tests
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    """Create a new database session for a test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

def fill_tables(db: Session):
    Base.metadata.create_all(bind=test_engine)
    # Add gyms
    test_gyms = [
        Gym(name="Big Gym", address_place="Zwolle"),
        Gym(name="Profit", address_place="Nijmegen")
    ]

    for gym in test_gyms:
        db.add(gym)
        db.commit()
        db.refresh(gym)

    # Add customers
    test_customers = [
        Customer(
            first_name='John', last_name='Doe', gender='male',
            birth_date=datetime(1990, 1, 1).date(), length=180,
            gym_id=1, activity_level=10.0
        ),
        Customer(
            first_name='Jane', last_name='Smith', gender='female',
            birth_date=datetime(1985, 5, 15).date(), length=165,
            gym_id=2, activity_level=9.3
        )
    ]

    for customer in test_customers:
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # Add goals
    test_goals = [
        Goal(customer_id=1,
             weight_goal=70,
             start_date=date.today() - timedelta(days=15),
             end_date=date.today() - timedelta(days=1)),
        Goal(customer_id=2,
             weight_goal=60,
             start_date=date.today() - timedelta(days=28),
             end_date=date.today() - timedelta(days=14))
    ]

    for goal in test_goals:
        db.add(goal)
        db.commit()
        db.refresh(goal)

    # Add progress
    test_progress = [
        Progress(customer_id=1, weight=80,
                 date=date.today() - timedelta(days=270)),
        Progress(customer_id=2, weight=50,
                 date=date.today() - timedelta(days=365))
    ]

    for progress in test_progress:
        db.add(progress)
        db.commit()
        db.refresh(progress)

def drop_tables():
    Base.metadata.drop_all(bind=test_engine)

@pytest.mark.asyncio
async def test_create_user(db: Session):
    customer = {
        "gym_id": 1, "first_name": 'John', "last_name": 'Doe', "birth_date": "1990-01-01",
        "gender": 'male', "length": 180, "activity_level": 8
    }

    # Perform the POST request using TestClient
    result = client.post("/customers", json=customer)

    # Print diagnostic information
    print("Response status code:", result.status_code)
    print("Response data:", result.json())

    # Assert that the status code is 201 (Created)
    assert result.status_code == 201

    # Query the database directly to verify insertion
    customer_in_db = db.query(Customer).filter_by(first_name='John', last_name='Doe').first()

    # Print out the customer fetched from the DB to verify it was inserted
    if customer_in_db:
        print("Customer found in DB:", customer_in_db)
    else:
        print("Customer not found in DB.")

    assert customer_in_db is not None  # Ensure the customer was added

@pytest.mark.asyncio
async def test_get_user(db: Session):
    fill_tables(db)

    response = client.get("/customers/1")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1

    drop_tables()

