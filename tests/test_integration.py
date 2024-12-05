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
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app
from schemas.responses import SingleCustomerResponse
from services.functions import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models.entities import Base, Customer

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

# def populate_db():
#     test_customers = [
#         {
#             "first_name":'John', "last_name":'Doe', "gender":'M',
#             "birth_date":"1990-01-01", "length":180,
#             "gym_id":1, "activity_level":10.0
#         },
#         {
#             "first_name":'Alice', "last_name":'Cooper', "gender":'V',
#             "birth_date":"2001-01-01", "length":165,
#             "gym_id":1, "activity_level":5.7
#         }
#     ]
#     try:
#         for customer in test_customers:
#             client.post("/customers", json=customer)
#     except Exception as e:
#         print(e)
#
#     return test_customers


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
async def test_get_user_empty(db: Session):

    response = client.get("/customers/1")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1

@pytest.mark.asyncio
async def test_get_user(db: Session):
    # test_customers = populate_db()

    response = client.get("/customers/1")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1

