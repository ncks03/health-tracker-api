import json

import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from routers.customers import read_customer_by_name, read_customer_by_id, get_daily_calorie_intake, create_user, \
    create_goal_for_user
from schemas.dtos import CustomerDTO, GoalDTO
from schemas.responses import CustomerResponse, SingleCustomerResponse
from models.entities import Customer as CustomerTable, Goal
from datetime import timedelta, datetime, date


mock_customers = [
    CustomerTable(
        id=1, first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=10.0
    ),
    CustomerTable(
        id=2, first_name='Jane', last_name='Smith', gender='female',
        birth_date=datetime(1985, 5, 15).date(), length=165,
        gym_id=1, activity_level=9.3
    ),
    CustomerTable(
        id=3, first_name='Alice', last_name='Johnson', gender='female',
        birth_date=datetime(2000, 8, 25).date(), length=170,
        gym_id=1, activity_level=5.5
    ),
    CustomerTable(
        id=4, first_name='Bob', last_name='Brown', gender='male',
        birth_date=datetime(1995, 12, 30).date(), length=175,
        gym_id=1, activity_level=2.3
    ),
    CustomerTable(
        id=5, first_name='Charlie', last_name='Davis', gender='male',
        birth_date=datetime(1988, 3, 10).date(), length=182,
        gym_id=1, activity_level=7.3
    )
]

# Create mock data directly as CustomerResponse objects
mock_customer_responses = [
    CustomerResponse(
        id=1, first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180,
        gym_id=1, activity_level=10.0
    ),
    CustomerResponse(
        id=2, first_name='Jane', last_name='Smith', gender='female',
        birth_date=datetime(1985, 5, 15).date(), length=165,
        gym_id=1, activity_level=9.3
    ),
    CustomerResponse(
        id=3, first_name='Alice', last_name='Johnson', gender='female',
        birth_date=datetime(2000, 8, 25).date(), length=170,
        gym_id=1, activity_level=5.5
    ),
    CustomerResponse(
        id=4, first_name='Bob', last_name='Brown', gender='male',
        birth_date=datetime(1995, 12, 30).date(), length=175,
        gym_id=1, activity_level=2.3
    ),
    CustomerResponse(
        id=5, first_name='Charlie', last_name='Davis', gender='male',
        birth_date=datetime(1988, 3, 10).date(), length=182,
        gym_id=1, activity_level=7.3
    )
]

mock_single_customer = SingleCustomerResponse(
id=1, first_name='John', last_name='Doe', gender='male',
        birth_date=datetime(1990, 1, 1).date(), length=180, weight=80,
        gym_id=1, activity_level=10.0
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
        gym_id=1, activity_level=10.0
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
        gym_id=1, activity_level=10.0
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    #Act
    with pytest.raises(HTTPException) as result:
        await create_user(mock_customer, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "This user already exists!"

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