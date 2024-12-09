import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from routers.customers import get_customer_by_name, get_customer_by_id, get_daily_calorie_intake, create_customer, \
    create_goal_for_customer, get_customer_progress, create_progress_for_customer, get_customer_goals, delete_customer, \
    update_customer
from schemas.dtos import CustomerDTO, ProgressDTO
from schemas.responses import CustomerResponse, SingleCustomerResponse, CustomerProgressResponse, CustomerGoalResponse
from models.entities import Customer as CustomerTable
from models.entities import Goal as GoalsTable
from models.entities import Progress as ProgressTable
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
    It should get all customers and return them in the correct response format
    """
    # Arrange
    mock_db = MagicMock()

    # Return the mock customers directly when the query is executed
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_customers

    # Act
    result = await get_customer_by_name(db=mock_db)

    # Assert
    # Directly comparing the result to the mock data
    assert result == mock_customer_responses

@pytest.mark.asyncio
async def test_get_customer_by_name_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_customers[:1]

    # Act
    response = await get_customer_by_name(first_name="John", last_name="Doe", db=mock_db)

    # Assert
    assert response == [mock_customer_responses[0]]
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_customer_by_name_not_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    # Act
    with pytest.raises(HTTPException) as exc:
        await get_customer_by_name(first_name="DoesNotExist", last_name="MyFriend", db=mock_db)

    # Assert
    assert exc.value.status_code == 404
    assert exc.value.detail == "No customers found for name DoesNotExist MyFriend"

@pytest.mark.asyncio
async def test_get_customer_by_name_database_error():
    # Arrange
    mock_db = MagicMock()

    # Simulate a database error (e.g., database connection issue)
    mock_db.execute.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await get_customer_by_name(first_name="DoesNotExist", last_name="MyFriend", db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_get_customer_by_id():
    """
    It should get a single customer by id and return it in the correct response format
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
    result = await get_customer_by_id(mock_customers[0].id, db=mock_db)

    # Assert
    # Directly comparing the result to the mock data
    assert result == mock_single_customer

@pytest.mark.asyncio
async def test_get_customer_by_id_not_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await get_customer_by_id(customer_id=99, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Customer not found"
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_customer_by_id_database_error():
    # Arrange
    mock_db = MagicMock()

    # Simulate a database error (e.g., database connection issue)
    mock_db.execute.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await get_customer_by_id(customer_id=1, db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_get_customer_goals_found():
    # Arrange
    mock_goals = [
        GoalsTable(id=1, customer_id=1, weight_goal=75, start_date="2023-01-01", end_date="2023-06-01"),
        GoalsTable(id=2, customer_id=1, weight_goal=70, start_date="2023-06-02", end_date="2023-12-31")
    ]

    # Create mock database object
    mock_db = MagicMock()

    # Configure the mock to return the goals
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_goals

    # Mock customer retrieval
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    # Act
    response = await get_customer_goals(customer_id=1, db=mock_db)

    # Create the expected response using CustomerGoalResponse objects
    expected_response = {
        "customer_id": 1,
        "customer_name": "John Doe",
        "goals": [
            CustomerGoalResponse(id=1, weight_goal=75, start_date=date(2023, 1, 1), end_date=date(2023, 6, 1)),
            CustomerGoalResponse(id=2, weight_goal=70, start_date=date(2023, 6, 2), end_date=date(2023, 12, 31))
        ]
    }

    # Act: Compare the response with expected response directly
    assert response == expected_response

@pytest.mark.asyncio
async def test_get_customer_goals_not_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await get_customer_goals(customer_id=99, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "No goals found for customer with id 99"
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_customer_goals_database_error():
    # Arrange
    mock_db = MagicMock()

    # Simulate a database error (e.g., database connection issue)
    mock_db.execute.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await get_customer_goals(customer_id=1, db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_delete_customer_success():
    # Arrange
    mock_db = MagicMock()

    # Mock the case where the customer exists
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[3]

    # Act
    response = await delete_customer(customer_id=mock_customers[3].id, db=mock_db)

    # Assert
    assert response.status_code == 200
    assert response.body.decode() == '{"message":"Customer with id 4 successfully deleted."}'
    mock_db.delete.assert_called_once_with(mock_customers[3])
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_customer_not_found():
    # Arrange
    mock_db = MagicMock()
    customer_id = 1

    # Mock the case where the customer does not exist in the database
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await delete_customer(customer_id=customer_id, db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 404
    assert exc.value.detail == "Customer 1 does not exist."

@pytest.mark.asyncio
async def test_delete_customer_database_error():
    # Arrange
    mock_db = MagicMock()
    customer_id = 1

    # Simulate a database error (e.g., database connection issue)
    mock_db.query.return_value.filter.return_value.first.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await delete_customer(customer_id=customer_id, db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

# Test post requests
@pytest.mark.asyncio
async def test_create_customer():
    """
    Test creating customer
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
    result = await create_customer(mock_customers[0], db=mock_db)

    #Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.status_code == 201
    assert result.body.decode() == '{"message":"Customer John Doe successfully added."}'

@pytest.mark.asyncio
async def test_create_customer_exists():
    """
    Test creating a customer that already exists raises error
    """
    #Arrange
    mock_db = MagicMock()

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    #Act
    with pytest.raises(HTTPException) as result:
        await create_customer(mock_customers[0], db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "This user already exists!"

@pytest.mark.asyncio
async def test_create_customer_database_error():
    # Arrange
    mock_db = MagicMock()

    # Simulate a database error (e.g., database connection issue)
    mock_db.query.return_value.filter.return_value.first.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await create_customer(customer=mock_customers[3], db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_update_customer_unexpected_error():
    # Arrange
    mock_db = MagicMock()
    customer_id = 1
    updated_data = {"first_name": "Unexpected"}

    mock_db.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected DB error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await update_customer(
            customer_id=customer_id,
            data=MagicMock(**updated_data),
            db=mock_db
        )

    # Assert the correct error details
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Unexpected DB error"

@pytest.mark.asyncio
async def test_update_customer_violate_constraints():
    # Arrange
    mock_db = MagicMock()
    customer_id = 1
    invalid_data = {"activity_level": 2.0}  # Outside the valid range

    mock_customer = mock_customers[0]
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await update_customer(
            customer_id=customer_id,
            data=MagicMock(**invalid_data),
            db=mock_db
        )

    # Assert the correct error details
    assert exc.value.status_code == 422
    assert exc.value.detail == "The activity level must be between 1.2 and 1.725."

@pytest.mark.asyncio
async def test_create_customer_violate_constraints():
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
        await create_customer(mock_customer, db=mock_db)

    assert result.value.status_code == 422
    assert result.value.detail == "The activity level must be between 1.2 and 1.725."

# test post goals
@pytest.mark.asyncio
async def test_create_goal():
    """
    Test creating a goal.
    """
    mock_db = MagicMock()
    mock_goal = GoalsTable(
        weight_goal=100,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14)
    )

    result = await create_goal_for_customer(1, mock_goal, db=mock_db)

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
    mock_goal = GoalsTable(
        weight_goal=100,
        start_date=date.today() - timedelta(days=28),
        end_date=date.today() - timedelta(days=14)
    )

    with pytest.raises(HTTPException) as result:
        await create_goal_for_customer(1, mock_goal, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "End date must be in the future"

@pytest.mark.asyncio
async def test_create_goal_same_dates():
    """
    Test creating goal with same dates raises error
    """
    mock_db = MagicMock()
    mock_goal = GoalsTable(
        weight_goal=100,
        start_date=date.today() + timedelta(days=14),
        end_date=date.today() + timedelta(days=14)
    )

    with pytest.raises(HTTPException) as result:
        await create_goal_for_customer(1, mock_goal, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "Start date and end date cannot be the same"

@pytest.mark.asyncio
async def test_create_goal_wrong_end_date():
    """
    Test creating goal with end date after start_date raises error
    """
    mock_db = MagicMock()
    mock_goal = GoalsTable(
        weight_goal=100,
        start_date=date.today(),
        end_date=date.today() - timedelta(days=14)
    )

    with pytest.raises(HTTPException) as result:
        await create_goal_for_customer(1, mock_goal, db=mock_db)

    assert result.value.status_code == 400
    assert result.value.detail == "End date cannot be before start date"

# Get progress test
@pytest.mark.asyncio
async def test_get_customer_progress():
    mock_db = MagicMock()
    mock_progress = [ProgressTable(
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

    result = await get_customer_progress(customer_id=1, db=mock_db)

    assert result == {
                "customer_id": 1,
                "customer_name": mock_customers[0].first_name + " " + mock_customers[0].last_name,
                "progress": [mock_progress_response]
            }

# Test post progress
@pytest.mark.asyncio
async def test_create_customer_progress():
    mock_db = MagicMock()
    mock_progress = ProgressDTO(
        weight = 100
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    result = await create_progress_for_customer(customer_id=1, progress=mock_progress, db = mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.status_code == 201

@pytest.mark.asyncio
async def test_create_customer_progress_no_customer():
    mock_db = MagicMock()
    mock_progress = ProgressDTO(
        weight = 100
    )

    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as result:
        await create_progress_for_customer(customer_id=5, progress=mock_progress, db = mock_db)

    assert result.value.status_code == 404
    assert result.value.detail == "No customer with id 5"

@pytest.mark.asyncio
async def test_create_customer_progress_negative_weight():
    mock_db = MagicMock()
    mock_progress = ProgressTable(
        weight=-100
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_customers[0]

    with pytest.raises(HTTPException) as result:
        await create_progress_for_customer(customer_id=1, progress=mock_progress, db = mock_db)

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