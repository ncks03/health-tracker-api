import pytest
import os

from main import app
from fastapi.testclient import TestClient

os.environ["DB_URL"] = "sqlite:///:memory:"

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_user():
    customer = {
        "gym_id":1, "first_name":'John', "last_name":'Doe', "birth_date":"1990-01-01",
        "gender":'male', "length":180, "activity_level":10.0
    }

    result = client.post("/customers", json=customer)

    assert result.status_code == 201

@pytest.mark.asyncio
async def test_get_user():
    response = client.get("/customers/1")
    assert response.status_code == 200
    assert response.json() == {}