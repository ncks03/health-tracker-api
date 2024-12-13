from unittest.mock import MagicMock
from fastapi import HTTPException
import pytest
from routers.gyms import get_gyms, create_gym, get_gym_by_id, delete_gym_by_id, get_customers_by_gym_id
from models.entities import Gym as GymTable
from models.entities import Customer
from schemas.dtos import GymDTO
from schemas.responses import GymResponse, SingleGymResponse, CustomerResponse
from datetime import date

# Sample mock data for GymResponse
mock_gyms = [
    GymTable(id=1, name="hot gym", address_place="ergens"),
    GymTable(id=2, name="Cool Gym", address_place="Anywhere")
]

mock_gym_responses= [
    GymResponse(id=1, name="hot gym", address_place="ergens"),
    GymResponse(id=2, name="Cool Gym", address_place="Anywhere")
]

mock_single_gym_responses= [SingleGymResponse(id=1, name="hot gym", address_place="ergens")]

mock_customers = [
    Customer(
        id=1,
        first_name="John",
        last_name="Doe",
        birth_date=date(1990, 1, 1),
        gender="Male",
        length=180,
        gym_id=1,
        activity_level=1.2
    ),
    Customer(
        id=2,
        first_name="Jane",
        last_name="Doe",
        birth_date=date(1985, 6, 15),
        gender="Female",
        length=165,
        gym_id=1,
        activity_level=1.5
    ),
]

mock_customer_responses = [
    CustomerResponse(
        id=1,
        first_name="John",
        last_name="Doe",
        birth_date=date(1990, 1, 1),
        gender="Male",
        length=180,
        gym_id=1,
        activity_level=1.2
    ),
    CustomerResponse(
        id=2,
        first_name="Jane",
        last_name="Doe",
        birth_date=date(1985, 6, 15),
        gender="Female",
        length=165,
        gym_id=1,
        activity_level=1.5
    ),
]


@pytest.mark.asyncio
async def test_read_gyms():
    mock_db = MagicMock()

    mock_db.query.return_value.all.return_value = mock_gyms

    result = await get_gyms(db=mock_db)

    assert result ==  mock_gym_responses

@pytest.mark.asyncio
async def test_get_gyms_empty_table():
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = []

    with pytest.raises(HTTPException) as e:
        await get_gyms(db=mock_db)

    assert e.value.status_code == 404
    assert e.value.detail == "there are no Gyms registered in database"

@pytest.mark.asyncio
async def test_get_gyms_with_place_name_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_gyms[0]]

    result = await get_gyms(db=mock_db, address_place="hot gym")

    assert result == [mock_gym_responses[0]] # expected as an array

@pytest.mark.asyncio
async def test_get_gyms_with_place_name_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(HTTPException) as exc:
        await get_gyms(db=mock_db, address_place="not that hot gym")

    assert exc.value.status_code == 404
    assert exc.value.detail == "No gyms found in not that hot gym"

@pytest.mark.asyncio
async def test_create_gym_already_exists():
    mock_db = MagicMock()
    mock_gym = GymDTO(name="hot gym", address_place="ergens")

    mock_db.query.return_value.filter.return_value.first.return_value = mock_gyms[0]

    with pytest.raises(HTTPException) as exc:
        await create_gym(gym=mock_gym, db=mock_db)

    assert exc.value.status_code == 409
    assert exc.value.detail == f"Gym with name 'hot gym' in 'ergens' already exists"

@pytest.mark.asyncio
async def test_create_gym_successful():
    mock_db = MagicMock()
    mock_gym = GymDTO(name="not that hot gym", address_place="ergens")

    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = await create_gym(gym=mock_gym, db=mock_db)

    assert result.status_code == 201
    assert result.body.decode() == '{"message":"Gym \'not that hot gym\' is successfully registered!"}'

@pytest.mark.asyncio
async def test_create_gym_unexpected_error():
    # Arrange
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add.side_effect = Exception("Unexpected database error")  # Simulate database error

    gym_dto = GymDTO(name="Fitness World", address_place="123 Main St")

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await create_gym(gym=gym_dto, db=mock_db)

    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Unexpected database error"

@pytest.mark.asyncio
async def test_get_gym_by_id_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        await get_gym_by_id(gym_id=1, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Gym with id 1 not found"

@pytest.mark.asyncio
async def test_get_gym_by_id_is_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_gyms[0]

    result = await get_gym_by_id(gym_id=1, db=mock_db)

    assert result == mock_single_gym_responses[0]

@pytest.mark.asyncio
async def test_delete_gym_by_id_success():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_gyms[0]

    response = await delete_gym_by_id(gym_id=1, db=mock_db)

    assert response.status_code == 200
    assert response.body == b'{"message":"Gym with id 1 successfully deleted."}'

    mock_db.delete.assert_called_once_with(mock_gyms[0])
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_gym_by_id_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        await delete_gym_by_id(gym_id=99, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Gym with id 99 not found"

    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_delete_gym_by_id_server_error():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc:
        await delete_gym_by_id(gym_id=1, db=mock_db)

    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_get_customers_by_gym_id_no_customers_found():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_gyms[0]  # Mock gym retrieval
    mock_query.filter.return_value.all.return_value = []  # No customers found
    mock_db.query.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        await get_customers_by_gym_id(gym_id=1, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Gym with id 1 has no customers"


@pytest.mark.asyncio
async def test_get_customers_by_gym_id_server_error():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.side_effect = Exception("Database error")  # Simulate a database error
    mock_db.query.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        await get_customers_by_gym_id(gym_id=1, db=mock_db)

    assert exc.value.status_code == 500
    assert exc.value.detail == "An error occurred: Database error"

@pytest.mark.asyncio
async def test_get_customers_by_gym_id_success():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_gyms[0]  # Mock gym retrieval
    mock_query.filter.return_value.all.return_value = mock_customers  # Mock customers retrieval
    mock_db.query.return_value = mock_query

    response = await get_customers_by_gym_id(gym_id=1, db=mock_db)

    assert response == {
        "gym": "hot gym",
        "customers": mock_customer_responses
    }


@pytest.mark.asyncio
async def test_get_customers_by_gym_id_no_gym_found():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None  # Gym not found
    mock_db.query.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        await get_customers_by_gym_id(gym_id=99, db=mock_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Gym with id 99 does not exist"