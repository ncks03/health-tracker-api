import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from routers.goals import read_goals
from models.entities import Goal as GoalsTable
from schemas.responses import GoalResponse

mock_goals = [
    (GoalsTable(id=1, customer_id=1, weight_goal=75.0, start_date="2023-01-01", end_date="2023-06-01"), "John", "Doe"),
    (GoalsTable(id=2, customer_id=2, weight_goal=65.0, start_date="2024-12-12", end_date="2024-12-14"), "Jane", "Smith")
]

@pytest.mark.asyncio
async def test_read_goals_no_filters():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.all.return_value = mock_goals

    # Act
    response = await read_goals(db=mock_db)

    # Assert
    expected_response = [
        GoalResponse(id=1, customer_id=1, customer_name="John Doe", weight_goal=75.0,
                     start_date="2023-01-01", end_date="2023-06-01"),
        GoalResponse(id=2, customer_id=2, customer_name="Jane Smith", weight_goal=65.0,
                     start_date="2024-12-12", end_date="2024-12-14")
    ]

    assert response == expected_response


@pytest.mark.asyncio
async def test_read_goals_no_results():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.all.return_value = False

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await read_goals(start_date="2025-01-01", db=mock_db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "No goals found (matching the given criteria)."

@pytest.mark.asyncio
async def test_read_goals_exception():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("Database error")

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await read_goals(db=mock_db)
    assert exc.value.status_code == 500
    assert "Could not fetch goals" in exc.value.detail
