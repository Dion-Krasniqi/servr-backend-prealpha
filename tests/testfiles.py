from fastapi.testclient import TestClient
from main.main import app
from main.tests.testauth import *
import os

client = TestClient(
        app,
        base_url="http://127.0.0.1:8000",
        root_path="",
)

def test_upload():

    # login 
    
    with open("Colossus.JPG", "rb") as f:
        files = {
                "file": ("Colossus.JPG", f, "image/jpeg")
                }
    
    response = client.post("/upload_file", files=files)
    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
