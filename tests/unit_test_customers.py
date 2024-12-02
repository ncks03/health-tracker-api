import pytest
from unittest.mock import MagicMock
from routers.customers import read_customer_by_name, CustomerResponse
from datetime import datetime

# Create mock data directly as CustomerResponse objects
mock_customers = [
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

@pytest.mark.asyncio
async def test_get_customers():
    # Arrange
    mock_db = MagicMock()

    # Return the mock customers directly when the query is executed
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_customers

    # Act
    result = await read_customer_by_name(db=mock_db)

    # Assert
    # Directly comparing the result to the mock data
    assert result == {'customers': mock_customers}
    #nu wel goeie push?....
