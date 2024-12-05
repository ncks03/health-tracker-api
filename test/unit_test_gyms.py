import pytest
from unittest.mock import MagicMock
from routers.gyms import read_gyms
from schemas.responses import GymResponse

# Sample mock data for GymResponse
mock_gyms = [
    GymResponse(name="hot gym", address_place="ergens")
]

@pytest.mark.asyncio
async def test_read_gyms():
    # Arrange
    mock_db = MagicMock()  # Use AsyncMock for async database sessions

    # Mock the return value of execute and subsequent calls for scalars and all
    mock_db.query.return_value.all.return_value = mock_gyms

    # Act
    result = await read_gyms(db=mock_db)

    # Assert
    # Ensure the result is correctly formatted
    assert result ==  mock_gyms
