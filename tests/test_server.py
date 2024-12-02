from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

# @pytest.fixture(scope="function", autouse=True)
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "the server is up and running"
