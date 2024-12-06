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

##########################################################################
#  S E T U P  T A B L E S
##########################################################################

def create_tables(db: Session):
    Base.metadata.create_all(bind=test_engine)

def fill_tables(db: Session):
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
            gym_id=1, activity_level=1.5
        ),
        Customer(
            first_name='Jane', last_name='Smith', gender='female',
            birth_date=datetime(1985, 5, 15).date(), length=165,
            gym_id=2, activity_level=1.3
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

##########################################################################
#  C U S T O M E R  T E S T   C A S E S
##########################################################################

@pytest.mark.asyncio
async def test_create_customer(db: Session):
    """It should Create a new Customer"""
    create_tables(db)

    new_customer = {
        "gym_id": 1, "first_name": 'John', "last_name": 'Doe', "birth_date": "1990-01-01",
        "gender": 'male', "length": 180, "activity_level": 1.5
    }

    # Perform the POST request using TestClient
    result = client.post("/customers", json=new_customer)

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

    assert customer_in_db is not None # Ensure the customer was added

    drop_tables()

@pytest.mark.asyncio
async def test_create_customer_bad_request(db: Session):
    """It should Create a new Customer"""
    create_tables(db)

    new_customer = {
        "gym_id": 1, "first_name": 'John', "last_name": 'Doe',
        "gender": 'male', "length": 180, "activity_level": 8, "birth_date": "1990-01-01",
    }

    # Perform the POST request using TestClient
    result = client.post("/customers", json=new_customer)

    # Print diagnostic information
    print("Response status code:", result.status_code)
    print("Response data:", result.json())

    # Assert that the status code is 400 (bad request)
    assert result.status_code == 400

    drop_tables()

@pytest.mark.asyncio
async def test_get_customer(db: Session):
    """It should Get a single Customer"""
    create_tables(db)
    fill_tables(db)

    response = client.get("/customers/1")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1

    drop_tables()

@pytest.mark.asyncio
async def test_get_customer_not_found(db: Session):
    """It should properly handle an empty table for Customers"""
    create_tables(db)

    response = client.get("/customers")
    assert response.status_code == 404

    drop_tables()

@pytest.mark.asyncio
async def test_delete_customer(db: Session):
    """Test that a customer can be deleted and is no longer in the database."""
    create_tables(db)

    # Fill tables with test data
    fill_tables(db)

    # Verify the customer exists before deletion
    customer_before = db.query(Customer).filter_by(id=1).first()
    assert customer_before is not None  # Ensure the customer exists

    # Perform the DELETE request
    response = client.delete("/customers/1")

    print("response after delete request", response.json())

    # Validate the response
    assert response.status_code == 200  # Ensure the response status code is 200
    assert response.json() == {'message': 'Customer with id 1 successfully deleted.'}   # Ensure the correct customer ID is returned

    # Verify the customer no longer exists in the database
    customer_after = db.query(Customer).filter_by(id=1).first()
    assert customer_after is None  # Ensure the customer was deleted

    # Cleanup
    drop_tables()

# @pytest.mark.asyncio
# async def test_patch_customer(db: Session):
#     """Test that a customer can have its data changed"""
#     # Fill tables with test data
#     fill_tables(db)
#
#     customer_before = db.query(Customer).filter_by(id=1).first()
#     assert customer_before is not None
#
#     response = client.patch("/customers/1", json={"first_name": "ThisIsANewNameForCustomer1"})
#
#     assert response.status_code == 200
#     assert response.json()["data"]["first_name"] == "Maximilianus"
#
#     drop_tables()

##########################################################################
#  G O A L S  T E S T   C A S E S
##########################################################################

@pytest.mark.asyncio
async def test_create_goal(db: Session):
    """It should Create a new Goal"""
    create_tables(db)

    new_goal = {
        "customer_id": 1, "weight_goal": 100, "start_date": "3000-01-01", "end_date": "3000-01-02"
    }

    # Perform the POST request using TestClient
    customer_id = new_goal["customer_id"]
    result = client.post(f"customers/{customer_id}/goals", json=new_goal)

    # Print diagnostic information
    print("Response status code:", result.status_code)
    print("Response data:", result.json())

    # Assert that the status code is 201 (Created)
    assert result.status_code == 201

    # Query the database directly to verify insertion
    goal_in_db = db.query(Goal).filter_by(weight_goal=100, start_date='3000-01-01').first()

    # Print out the goal fetched from the DB to verify it was inserted
    if goal_in_db:
        print("Goal found in DB:", goal_in_db)
    else:
        print("Goal not found in DB.")

    assert goal_in_db is not None  # Ensure the goal was added

    drop_tables()

@pytest.mark.asyncio
async def test_get_goal(db: Session):
    """It should get a single goal."""
    create_tables(db)

    fill_tables(db)  # Ensure data is populated

    response = client.get("/goals/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

    drop_tables()

@pytest.mark.asyncio
async def test_get_goal_not_found(db: Session):
    """It should handle a request for a non-existent goal."""
    create_tables(db)

    response = client.get("/goals")  # A goal that does not exist
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_goal(db: Session):
    """Test that a goal can be deleted and is no longer in the database."""
    fill_tables(db)  # Ensure data is populated

    # Verify the goal exists before deletion
    goal_before = db.query(Goal).filter_by(id=1).first()
    assert goal_before is not None  # Ensure the goal exists

    # Perform the DELETE request
    response = client.delete("/goals/1")

    # Print diagnostic information
    print("response after delete request", response.json())

    # Validate the response
    assert response.status_code == 200  # Ensure the response status code is 200
    assert response.json() == {'message': 'Goal with id 1 successfully deleted.'}  # Ensure the correct goal ID is returned

    # Verify the goal no longer exists in the database
    goal_after = db.query(Goal).filter_by(id=1).first()
    assert goal_after is None  # Ensure the goal was deleted

    drop_tables()

# @pytest.mark.asyncio
# async def test_update_goal(db: Session):
#     """It should update a goal."""
#     fill_tables(db)  # Ensure data is populated
#
#     updated_goal = {
#         "weight_goal": 110, "start_date": "3000-02-01", "end_date": "3000-02-02"
#     }
#
#     # Perform the PATCH request using TestClient
#     result = client.patch(f"customers/{customer_id}/goals", json=updated_goal)
#
#     # Print diagnostic information
#     print("Response status code:", result.status_code)
#     print("Response data:", result.json())
#
#     # Assert that the status code is 200 (OK)
#     assert result.status_code == 200
#
#     # Query the database directly to verify update
#     goal_in_db = db.query(Goal).filter_by(id=1).first()
#     assert goal_in_db is not None  # Ensure the goal exists
#     assert goal_in_db.weight_goal == 110  # Verify the weight_goal was updated
#
#     drop_tables()

