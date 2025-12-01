from fastapi.testclient import TestClient
from main.main import app

client = TestClient(
        app,
        base_url="http://127.0.0.1:8000",
        root_path="",
)

def test_login():
    data = {"username":"user@mail.com",
            "password":"secret"}

    response = client.post("/token", data=data)
    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
