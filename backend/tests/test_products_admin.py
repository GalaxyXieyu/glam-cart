import pytest
from fastapi.testclient import TestClient
import io

def test_create_product_success(client, auth_headers, sample_product_data):
    """Test successful product creation."""
    response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == sample_product_data["name"]
    assert data["data"]["code"] == sample_product_data["code"]
    assert "id" in data["data"]
    assert "createdAt" in data["data"]
    assert "updatedAt" in data["data"]

def test_create_product_duplicate_code(client, auth_headers, sample_product_data):
    """Test creating product with duplicate code."""
    # Create first product
    client.post("/api/products", json=sample_product_data, headers=auth_headers)
    
    # Try to create another with same code
    duplicate_data = sample_product_data.copy()
    duplicate_data["name"] = "Different Name"
    
    response = client.post("/api/products", json=duplicate_data, headers=auth_headers)
    
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "Product code already exists" in data["message"]

def test_create_product_without_auth(client, sample_product_data):
    """Test creating product without authentication."""
    response = client.post("/api/products", json=sample_product_data)
    
    assert response.status_code == 403

def test_update_product_success(client, auth_headers, sample_product_data):
    """Test successful product update."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Update product
    update_data = {
        "name": "Updated Product Name",
        "description": "Updated description",
        "cost_price": 3.00
    }
    
    response = client.put(f"/api/products/{product_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Updated Product Name"
    assert data["data"]["description"] == "Updated description"
    assert data["data"]["pricing"]["costPrice"] == 3.00
    # Original values should remain
    assert data["data"]["code"] == sample_product_data["code"]

def test_update_product_not_found(client, auth_headers):
    """Test updating non-existent product."""
    update_data = {"name": "Updated Name"}
    
    response = client.put("/api/products/nonexistent-id", json=update_data, headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "Product not found" in data["message"]

def test_update_product_duplicate_code(client, auth_headers, sample_product_data):
    """Test updating product with duplicate code."""
    # Create two products
    product1_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product1_id = product1_response.json()["data"]["id"]
    
    product2_data = sample_product_data.copy()
    product2_data["code"] = "TEST002"
    product2_data["name"] = "Second Product"
    product2_response = client.post("/api/products", json=product2_data, headers=auth_headers)
    product2_id = product2_response.json()["data"]["id"]
    
    # Try to update product2 with product1's code
    update_data = {"code": sample_product_data["code"]}
    
    response = client.put(f"/api/products/{product2_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "Product code already exists" in data["message"]

def test_delete_product_success(client, auth_headers, sample_product_data):
    """Test successful product deletion."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Delete product
    response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Product deleted successfully" in data["message"]
    
    # Verify product is deleted
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 404

def test_delete_product_not_found(client, auth_headers):
    """Test deleting non-existent product."""
    response = client.delete("/api/products/nonexistent-id", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "Product not found" in data["message"]

def test_delete_product_without_auth(client, auth_headers, sample_product_data):
    """Test deleting product without authentication."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Try to delete without auth
    response = client.delete(f"/api/products/{product_id}")
    
    assert response.status_code == 403

def test_upload_product_images_success(client, auth_headers, sample_product_data, sample_image_file):
    """Test successful image upload."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Upload image
    files = {"images": sample_image_file}
    response = client.post(f"/api/products/{product_id}/images", files=files, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "images" in data["data"]
    assert len(data["data"]["images"]) == 1
    assert "id" in data["data"]["images"][0]
    assert "url" in data["data"]["images"][0]

def test_upload_product_images_product_not_found(client, auth_headers, sample_image_file):
    """Test uploading images to non-existent product."""
    files = {"images": sample_image_file}
    response = client.post("/api/products/nonexistent-id/images", files=files, headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "Product not found" in data["message"]

def test_upload_product_images_no_files(client, auth_headers, sample_product_data):
    """Test uploading with no files."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Try to upload without files
    response = client.post(f"/api/products/{product_id}/images", headers=auth_headers)
    
    assert response.status_code == 422  # Validation error

def test_delete_product_image_success(client, auth_headers, sample_product_data, sample_image_file):
    """Test successful image deletion."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Upload image
    files = {"images": sample_image_file}
    upload_response = client.post(f"/api/products/{product_id}/images", files=files, headers=auth_headers)
    image_id = upload_response.json()["data"]["images"][0]["id"]
    
    # Delete image
    response = client.delete(f"/api/products/{product_id}/images/{image_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Image deleted successfully" in data["message"]

def test_delete_product_image_not_found(client, auth_headers, sample_product_data):
    """Test deleting non-existent image."""
    # Create product first
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    
    # Try to delete non-existent image
    response = client.delete(f"/api/products/{product_id}/images/nonexistent-id", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "Image not found" in data["message"]
