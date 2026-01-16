from app.core.security import create_access_token


def test_login(client, admin_user):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_me(client, admin_user):
    token = create_access_token(str(admin_user.id))
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
