import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from routers.progress import get_progress


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