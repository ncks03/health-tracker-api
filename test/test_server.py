from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def test_get_customers():
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json() == {}