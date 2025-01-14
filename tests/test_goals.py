import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from routers.goals import read_goals, get_goal_by_id, delete_goal
from models.entities import Goal as GoalsTable
from schemas.responses import GoalResponse

@pytest.mark.asyncio
async def test_read_goals_no_filters():
    # Arrange
    mock_db = MagicMock()
    mock_goals = [
        (GoalsTable(id=1, customer_id=1, weight_goal=75.0, start_date="2023-01-01", end_date="2023-06-01"), "John",
         "Doe"),
        (GoalsTable(id=2, customer_id=2, weight_goal=65.0, start_date="2024-12-12", end_date="2024-12-14"), "Jane",
         "Smith")
    ]
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
    assert exc.value.detail == "Could not fetch goals: Database error"

@pytest.mark.asyncio
async def test_get_goal_by_id_success():
    # Arrange
    mock_db = MagicMock()
    mock_goal = GoalsTable(id=1, customer_id=1, weight_goal=75.0, start_date="2023-01-01", end_date="2023-06-01")
    mock_customer = ("John", "Doe")
    mock_db.execute.return_value.first.return_value = (mock_goal, *mock_customer)

    # Act
    response = await get_goal_by_id(goals_id=1, db=mock_db)

    # Assert
    expected_response = GoalResponse(
        id=1,
        customer_id=1,
        customer_name="John Doe",
        weight_goal=75.0,
        start_date="2023-01-01",
        end_date="2023-06-01",
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_get_goal_by_id_not_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.return_value.first.return_value = None

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await get_goal_by_id(goals_id=9999, db=mock_db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Goal with ID 9999 not found."


@pytest.mark.asyncio
async def test_get_goal_by_id_exception():
    # Arrange
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("Database error")

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await get_goal_by_id(goals_id=1, db=mock_db)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Could not retrieve goal: Database error"


@pytest.mark.asyncio
async def test_delete_goal_success():
    # Arrange
    mock_db = MagicMock()
    mock_goal = GoalsTable(id=1, customer_id=1, weight_goal=75.0, start_date="2023-01-01", end_date="2023-06-01")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_goal

    # Act
    response = await delete_goal(goal_id=1, db=mock_db)

    # Assert
    assert response.status_code == 200
    assert response.body.decode() == '{"message":"Goal with id 1 successfully deleted."}'
    mock_db.delete.assert_called_once_with(mock_goal)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_goal_not_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await delete_goal(goal_id=9999, db=mock_db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Goal with ID 9999 not found."

@pytest.mark.asyncio
async def test_delete_goal_exception():
    # Arrange
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("Database error")

    # Act and Assert
    with pytest.raises(HTTPException) as exc:
        await delete_goal(goal_id=1, db=mock_db)
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

