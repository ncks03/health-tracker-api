import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from routers.progress import get_progress, get_progress_by_id
from models.entities import Progress as ProgressTable
from datetime import datetime

from schemas.responses import ProgressResponse

mock_progresses = [
    ProgressTable(id=1, customer_id=1, date= datetime(2023, 6, 21).date(), weight=78),
    ProgressTable(id=2, customer_id=1, date= datetime(2023, 8, 11).date(), weight=120)
]

mock_progress_responses = [
    ProgressResponse(id=1, customer_id=1, date= datetime(2023, 6, 21).date(), weight=78),
    ProgressResponse(id=2, customer_id=1, date= datetime(2023, 8, 11).date(), weight=120)
]

@pytest.mark.asyncio
async def test_get_progress_database_error():
    # Arrange
    mock_db = MagicMock()

    # Simulate a database error (e.g., database connection issue)
    mock_db.query.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await get_progress(db=mock_db)

    # Check that the exception contains the correct status code and detail
    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_get_progress_response_ok():
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = mock_progresses

    response = await get_progress(db=mock_db)

    assert response == mock_progress_responses

@pytest.mark.asyncio
async def test_get_progress_by_id_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        await get_progress_by_id(progress_id=999, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "No progress found with id '999'"

@pytest.mark.asyncio
async def test_get_progress_by_id_is_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_progresses[1]

    response = await get_progress_by_id(progress_id=2, db=mock_db)

    assert response == mock_progress_responses[1]

@pytest.mark.asyncio
async def test_get_progress_by_id_server_error():
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("something went wrong")

    with pytest.raises(HTTPException) as exc:
        await get_progress_by_id(progress_id=203, db=mock_db)

    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: something went wrong"
