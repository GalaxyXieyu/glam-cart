import pytest
from fastapi.testclient import TestClient

def test_get_products_empty(client):
    """Test getting products when database is empty."""
    response = client.get("/api/products")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["products"] == []
    assert data["data"]["total"] == 0
    assert data["data"]["page"] == 1
    assert data["data"]["totalPages"] == 0

def test_get_products_with_pagination(client, auth_headers, sample_product_data):
    """Test getting products with pagination."""
    # Create a test product first
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Test pagination
    response = client.get("/api/products?page=1&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 1
    assert data["data"]["total"] == 1
    assert data["data"]["page"] == 1
    assert data["data"]["totalPages"] == 1

def test_get_products_with_search(client, auth_headers, sample_product_data):
    """Test getting products with search."""
    # Create a test product first
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Test search by name
    response = client.get("/api/products?search=Test")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 1
    assert "Test" in data["data"]["products"][0]["name"]
    
    # Test search with no results
    response = client.get("/api/products?search=NonExistent")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 0

def test_get_products_with_filters(client, auth_headers, sample_product_data):
    """Test getting products with filters."""
    # Create a test product first
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Test filter by tube type
    response = client.get("/api/products?tube_types=口红管")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 1
    
    # Test filter with no results
    response = client.get("/api/products?tube_types=睫毛膏瓶")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 0

def test_get_products_with_sorting(client, auth_headers, sample_product_data):
    """Test getting products with sorting."""
    # Create a test product first
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Test sort by newest
    response = client.get("/api/products?sort=newest")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 1
    
    # Test sort by price
    response = client.get("/api/products?sort=price_low")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["products"]) == 1

def test_get_product_by_id_success(client, auth_headers, sample_product_data):
    """Test getting a single product by ID."""
    # Create a test product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Get the product
    response = client.get(f"/api/products/{product_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == product_id
    assert data["data"]["name"] == sample_product_data["name"]
    assert data["data"]["code"] == sample_product_data["code"]

def test_get_product_by_id_not_found(client):
    """Test getting a non-existent product."""
    response = client.get("/api/products/nonexistent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "Product not found" in data["message"]

def test_get_featured_products_empty(client):
    """Test getting featured products when database is empty."""
    response = client.get("/api/products/featured")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []

def test_get_featured_products_with_data(client, auth_headers, sample_product_data):
    """Test getting featured products with data."""
    # Create a test product first
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Get featured products
    response = client.get("/api/products/featured?limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == sample_product_data["name"]

def test_get_filter_options(client, auth_headers, sample_product_data):
    """Test getting filter options."""
    # Create a test product first
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Get filter options
    response = client.get("/api/products/filter-options")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "tubeTypes" in data["data"]
    assert "boxTypes" in data["data"]
    assert "functionalDesigns" in data["data"]
    assert "shapes" in data["data"]
    assert "materials" in data["data"]
    assert "capacityRange" in data["data"]
    assert "priceRange" in data["data"]
    
    # Check that our test product's values are included
    assert "口红管" in data["data"]["tubeTypes"]
    assert "圆形" in data["data"]["shapes"]
    assert "PETG" in data["data"]["materials"]
