from fastapi.testclient import TestClient
from main.main import app

client = TestClient(
        app,
        base_url="http://127.0.0.1:8000",
        root_path="",
)

def test_login():
    data = {"email":"user@mail.com",
            "password":"secret"}

    response = client.post("/token", json=data)
    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
    token = body["access_token"]
    get_user_response = client.get("/users/me", 
                                    headers={"Authorization":"Bearer " + token})
    body = get_user_response.json()
    assert "email" in body
    print(body)

def test_create_account():
    data = {"username":"user1",
            "email":"user1@mail.com",
            "password":"secret"
            }
    response = client.post("/create_user", json=data)
    body = response.json()
    data = {"email":"user1@mail.com",
            "password":"secret"}

    response = client.post("/token", json=data)
    assert response.status_code == 200
    body = response.json()
    
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    token = body["access_token"]
    
    delete_user = client.post("/delete_account", headers={"Authorization":"Bearer " + token})
    

