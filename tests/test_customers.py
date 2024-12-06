import json

import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException
from pydantic.v1 import NoneBytes

from routers.customers import read_customer_by_name, read_customer_by_id, get_daily_calorie_intake, create_user, \
    create_goal_for_user, read_customer_progress, create_progress_for_user
from schemas.dtos import CustomerDTO, GoalDTO, ProgressDTO
from schemas.responses import CustomerResponse, SingleCustomerResponse, ProgressResponse, CustomerProgressResponse
from models.entities import Customer as CustomerTable, Goal, Progress
from datetime import timedelta, datetime, date


mock_customers = [
    CustomerTable(
        id=1, first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=1.4
    ),
    CustomerTable(
        id=2, first_name='Jane', last_name='Smith', gender='female',
        birth_date=datetime(1985, 5, 15).date(), length=165,
        gym_id=1, activity_level=1.3
    ),
    CustomerTable(
        id=3, first_name='Alice', last_name='Johnson', gender='female',
        birth_date=datetime(2000, 8, 25).date(), length=170,
        gym_id=1, activity_level=1.5
    ),
    CustomerTable(
        id=4, first_name='Bob', last_name='Brown', gender='male',
        birth_date=datetime(1995, 12, 30).date(), length=175,
        gym_id=1, activity_level=1.3
    ),
    CustomerTable(
        id=5, first_name='Charlie', last_name='Davis', gender='male',
        birth_date=datetime(1988, 3, 10).date(), length=182,
        gym_id=1, activity_level=1.3
    )
]

# Create mock data directly as CustomerResponse objects
mock_customer_responses = [
    CustomerResponse(
        id=1, first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=1.4
    ),
    CustomerResponse(
        id=2, first_name='Jane', last_name='Smith', gender='female',
        birth_date=datetime(1985, 5, 15).date(), length=165,
        gym_id=1, activity_level=1.3
    ),
    CustomerResponse(
        id=3, first_name='Alice', last_name='Johnson', gender='female',
        birth_date=datetime(2000, 8, 25).date(), length=170,
        gym_id=1, activity_level=1.5
    ),
    CustomerResponse(
        id=4, first_name='Bob', last_name='Brown', gender='male',
        birth_date=datetime(1995, 12, 30).date(), length=175,
        gym_id=1, activity_level=1.3
    ),
    CustomerResponse(
        id=5, first_name='Charlie', last_name='Davis', gender='male',
        birth_date=datetime(1988, 3, 10).date(), length=182,
        gym_id=1, activity_level=1.3
    )
]

mock_single_customer = SingleCustomerResponse(
id=1, first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180, weight=80,
        gym_id=1, activity_level=1.4
)

# Test get requests
@pytest.mark.asyncio
async def test_get_customers():
    """
    Test getting all customers
    """
    # Arrange
    mock_db = MagicMock()

    # Return the mock customers directly when the query is executed
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_customers

    # Act
    result = await read_customer_by_name(db=mock_db)

    # Assert
    # Directly comparing the result to the mock data
    assert result == {'customers': mock_customer_responses}
    #nu wel goeie push?....

@pytest.mark.asyncio
async def test_customer_by_id():
    """
    Test getting a customer by id
    """
    # Arrange
    mock_db = MagicMock()

    # Return the mock customers directly when the query is executed
    mock_db.execute.return_value.scalars.return_value.first.return_value = mock_customers[0]

    (mock_db.query.return_value
     .filter.return_value
     .order_by.return_value
     .limit.return_value.scalar).return_value = 80

    # Act
    result = await read_customer_by_id(mock_customers[0].id, db=mock_db)

    # Assert
    # Directly comparing the result to the mock data
    assert result == {'data': mock_single_customer}

# Test post requests
@pytest.mark.asyncio
async def test_create_user():
    """
    Test creating user
    """
    #Arrange
    mock_db = MagicMock()
    mock_customer = CustomerDTO(
        first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=1.4
    )

    mock_db.query.return_value.filter.return_value.first.return_value = None

    #Act
    result = await create_user(mock_customer, db=mock_db)

    #Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.status_code == 201

@pytest.mark.asyncio
async def test_create_user_exists():
    """
    Test creating a user that already exists raises error
    """
    #Arrange
    mock_db = MagicMock()
    mock_customer = CustomerDTO(
        first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=1.4
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    #Act
    with pytest.raises(HTTPException) as result:
        await create_user(mock_customer, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "This user already exists!"

@pytest.mark.asyncio
async def test_create_user_violate_constraints():
    """
    Test creating user
    """
    #Arrange
    mock_db = MagicMock()
    mock_customer = CustomerDTO(
        first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=3.1
    )

    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as result:
        await create_user(mock_customer, db=mock_db)

    assert result.value.status_code == 422
    assert result.value.detail == "The activity level must be between 1.2 and 1.725."

# test post goals
@pytest.mark.asyncio
async def test_create_goal():
    """
    Test creating a goal.
    """
    mock_db = MagicMock()
    mock_goal = Goal(
        weight_goal=100,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14)
    )

    result = await create_goal_for_user(1, mock_goal, db=mock_db)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.status_code == 201

@pytest.mark.asyncio
async def test_create_goal_past_date():
    """
    Test creating goal with past date raises error
    """
    mock_db = MagicMock()
    mock_goal = Goal(
        weight_goal=100,
        start_date=date.today() - timedelta(days=28),
        end_date=date.today() - timedelta(days=14)
    )

    with pytest.raises(HTTPException) as result:
        await create_goal_for_user(1, mock_goal, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "An error occurred: 400: End date must be in the future"

@pytest.mark.asyncio
async def test_create_goal_same_dates():
    """
    Test creating goal with same dates raises error
    """
    mock_db = MagicMock()
    mock_goal = Goal(
        weight_goal=100,
        start_date=date.today() + timedelta(days=14),
        end_date=date.today() + timedelta(days=14)
    )

    with pytest.raises(HTTPException) as result:
        await create_goal_for_user(1, mock_goal, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "An error occurred: 400: Start date and end date cannot be the same"

@pytest.mark.asyncio
async def test_create_goal_wrong_end_date():
    """
    Test creating goal with end date after start_date raises error
    """
    mock_db = MagicMock()
    mock_goal = Goal(
        weight_goal=100,
        start_date=date.today(),
        end_date=date.today() - timedelta(days=14)
    )

    with pytest.raises(HTTPException) as result:
        await create_goal_for_user(1, mock_goal, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "An error occurred: 400: End date cannot be before start date"

# Get progress test
@pytest.mark.asyncio
async def test_get_user_progress():
    mock_db = MagicMock()
    mock_progress = [Progress(
        id = 1,
        customer_id = 1,
        date = date.today() - timedelta(days=14),
        weight = 100
    )]

    mock_progress_response = CustomerProgressResponse(
        date = date.today() - timedelta(days=14),
        weight = 100
    )

    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_progress
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    result = await read_customer_progress(customer_id=1, db=mock_db)

    assert result == {
                "customer_id": 1,
                "customer_name": mock_customers[0].first_name + " " + mock_customers[0].last_name,
                "progress": [mock_progress_response]
            }

# Test post progress
@pytest.mark.asyncio
async def test_post_user_progress():
    mock_db = MagicMock()
    mock_progress = ProgressDTO(
        weight = 100
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    result = await create_progress_for_user(customer_id=1, progress=mock_progress, db = mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.status_code == 201

@pytest.mark.asyncio
async def test_post_user_progress_no_customer():
    mock_db = MagicMock()
    mock_progress = ProgressDTO(
        weight = 100
    )

    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as result:
        await create_progress_for_user(customer_id=5, progress=mock_progress, db = mock_db)

    assert result.value.status_code == 404
    assert result.value.detail == "No customer with id 5"

@pytest.mark.asyncio
async def test_post_user_progress_negative_weight():
    mock_db = MagicMock()
    mock_progress = Progress(
        weight=-100
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    with pytest.raises(HTTPException) as result:
        await create_progress_for_user(customer_id=1, progress=mock_progress, db = mock_db)

    assert result.value.status_code == 422
    assert result.value.detail == "Weight must be greater than 0."

# test algorithm/ daily calorie intake
@pytest.mark.asyncio
async def test_daily_calorie_intake():
    """
    Test getting daily calories intake from customer
    """
    # Arrange
    mock_db = MagicMock()

    # Act
    result = await get_daily_calorie_intake(mock_customers[0].id, db=mock_db)

    # Assert

    # Directly comparing the result to the mock data
    assert result == "This function does not work yet"