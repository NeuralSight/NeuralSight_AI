import json
from fastapi.testclient import TestClient


from helpers import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)
from main import app



def test_reset_password():
    client = TestClient(app)
    token = generate_password_reset_token("test@example.com")
    new_password = "newpassword"
    response = client.post("/user/reset-password/", json={"token": token, "new_password": new_password})
    assert response.status_code == 200
    assert json.loads(response.text) == {"msg": "Password updated successfully"}

    # Test invalid token
    response = client.post("/user/reset-password/", json={"token": "invalid_token", "new_password": new_password})
    assert response.status_code == 400
    assert json.loads(response.text) == {"detail": "Invalid token"}

    # Test non-existent user
    response = client.post("/user/reset-password/", json={"token": generate_password_reset_token("nonexistent@example.com"), "new_password": new_password})
    assert response.status_code == 404
    assert json.loads(response.text) == {"detail": "The user with this username does not exist in the system."}

    # Test inactive user
    response = client.post("/user/reset-password/", json={"token": generate_password_reset_token("inactive@example.com"), "new_password": new_password})
    assert response.status_code == 400
    assert json.loads(response.text) == {"detail": "Inactive user"}


test_reset_password()
