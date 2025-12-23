import pytest
from fastapi.testclient import TestClient

def test_login_success(client):
    """Test successful admin login."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "password"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert "user" in data["data"]
    assert data["data"]["user"]["username"] == "admin"
    assert data["data"]["user"]["role"] == "admin"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "Incorrect username or password" in data["message"]

def test_login_missing_user(client):
    """Test login with non-existent user."""
    response = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "password"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False

def test_verify_token_valid(client, auth_headers):
    """Test token verification with valid token."""
    response = client.get("/api/auth/verify", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "admin"
    assert data["data"]["role"] == "admin"

def test_verify_token_invalid(client):
    """Test token verification with invalid token."""
    response = client.get("/api/auth/verify", headers={
        "Authorization": "Bearer invalid_token"
    })
    
    assert response.status_code == 401

def test_verify_token_missing(client):
    """Test token verification without token."""
    response = client.get("/api/auth/verify")

    assert response.status_code == 403  # FastAPI returns 403 for missing auth

def test_logout_success(client, auth_headers):
    """Test successful logout."""
    response = client.post("/api/auth/logout", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Logout successful" in data["message"]

def test_logout_without_auth(client):
    """Test logout without authentication."""
    response = client.post("/api/auth/logout")

    assert response.status_code == 403

def test_protected_endpoint_without_auth(client):
    """Test accessing protected endpoint without authentication."""
    response = client.post("/api/products", json={
        "name": "Test Product",
        "code": "TEST001"
    })

    assert response.status_code == 403

def test_protected_endpoint_with_auth(client, auth_headers, sample_product_data):
    """Test accessing protected endpoint with authentication."""
    response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Should not return 403 (unauthorized)
    assert response.status_code != 403
