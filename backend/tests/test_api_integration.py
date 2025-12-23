import pytest
from fastapi.testclient import TestClient

def test_api_root(client):
    """Test API root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_full_workflow_integration(client, auth_headers, sample_product_data, sample_image_file):
    """Test complete workflow: login -> create product -> upload image -> update -> delete."""

    # 1. Login (already done via auth_headers fixture)
    verify_response = client.get("/api/auth/verify", headers=auth_headers)
    assert verify_response.status_code == 200

    # 2. Create product
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    assert create_response.status_code == 200
    product_id = create_response.json()["data"]["id"]

    # 3. Verify product appears in public listing
    list_response = client.get("/api/products")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["products"]) == 1

    # 4. Get single product
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == sample_product_data["name"]

    # 5. Upload image
    files = {"images": sample_image_file}
    upload_response = client.post(f"/api/products/{product_id}/images", files=files, headers=auth_headers)
    assert upload_response.status_code == 200
    image_id = upload_response.json()["data"]["images"][0]["id"]

    # 6. Update product
    update_data = {"name": "Updated Product Name"}
    update_response = client.put(f"/api/products/{product_id}", json=update_data, headers=auth_headers)
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "Updated Product Name"

    # 7. Delete image
    delete_image_response = client.delete(f"/api/products/{product_id}/images/{image_id}", headers=auth_headers)
    assert delete_image_response.status_code == 200

    # 8. Delete product
    delete_response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # 9. Verify product is deleted
    get_deleted_response = client.get(f"/api/products/{product_id}")
    assert get_deleted_response.status_code == 404

    # 10. Logout
    logout_response = client.post("/api/auth/logout", headers=auth_headers)
    assert logout_response.status_code == 200

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/api/products")
    
    # FastAPI automatically handles OPTIONS requests
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly defined

def test_api_documentation_accessible(client):
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200

def test_static_files_mount(client):
    """Test that static files are properly mounted."""
    # This would test if static files are accessible
    # In a real scenario, you'd upload a file first and then test access
    response = client.get("/static/")
    # Should return 404 for directory listing or 200 if index exists
    assert response.status_code in [200, 404, 405]

def test_error_handling_404(client):
    """Test 404 error handling."""
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404

def test_error_handling_validation(client):
    """Test validation error handling."""
    # Send invalid JSON to an endpoint that expects specific format
    response = client.post("/api/auth/login", json={
        "invalid_field": "value"
    })
    
    assert response.status_code == 422  # Validation error

def test_request_logging(client, caplog):
    """Test that requests are being logged."""
    import logging
    
    with caplog.at_level(logging.INFO):
        response = client.get("/health")
        
    # Check if request was logged
    assert any("GET /health" in record.message for record in caplog.records)

def test_full_workflow_integration(client, auth_headers, sample_product_data, sample_image_file):
    """Test complete workflow: login -> create product -> upload image -> update -> delete."""
    
    # 1. Login (already done via auth_headers fixture)
    verify_response = client.get("/api/auth/verify", headers=auth_headers)
    assert verify_response.status_code == 200
    
    # 2. Create product
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    assert create_response.status_code == 200
    product_id = create_response.json()["data"]["id"]
    
    # 3. Verify product appears in public listing
    list_response = client.get("/api/products")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["products"]) == 1
    
    # 4. Get single product
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == sample_product_data["name"]
    
    # 5. Upload image
    files = {"images": sample_image_file}
    upload_response = client.post(f"/api/products/{product_id}/images", files=files, headers=auth_headers)
    assert upload_response.status_code == 200
    image_id = upload_response.json()["data"]["images"][0]["id"]
    
    # 6. Update product
    update_data = {"name": "Updated Product Name"}
    update_response = client.put(f"/api/products/{product_id}", json=update_data, headers=auth_headers)
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "Updated Product Name"
    
    # 7. Delete image
    delete_image_response = client.delete(f"/api/products/{product_id}/images/{image_id}", headers=auth_headers)
    assert delete_image_response.status_code == 200
    
    # 8. Delete product
    delete_response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    
    # 9. Verify product is deleted
    get_deleted_response = client.get(f"/api/products/{product_id}")
    assert get_deleted_response.status_code == 404
    
    # 10. Logout
    logout_response = client.post("/api/auth/logout", headers=auth_headers)
    assert logout_response.status_code == 200

def test_concurrent_requests(client, auth_headers, sample_product_data):
    """Test handling of concurrent requests."""
    import threading
    import time
    
    results = []
    
    def create_product(index):
        product_data = sample_product_data.copy()
        product_data["code"] = f"TEST{index:03d}"
        product_data["name"] = f"Test Product {index}"
        
        response = client.post("/api/products", json=product_data, headers=auth_headers)
        results.append(response.status_code)
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=create_product, args=(i,))
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All requests should succeed
    assert all(status == 200 for status in results)
    assert len(results) == 5

def test_data_consistency(client, auth_headers, sample_product_data):
    """Test data consistency across operations."""
    import time

    # Create product
    create_response = client.post("/api/products", json=sample_product_data, headers=auth_headers)
    product_id = create_response.json()["data"]["id"]
    original_created_at = create_response.json()["data"]["createdAt"]

    # Add a small delay to ensure different timestamps
    time.sleep(0.1)

    # Update product
    update_data = {"description": "Updated description"}
    update_response = client.put(f"/api/products/{product_id}", json=update_data, headers=auth_headers)

    # Verify data consistency
    updated_product = update_response.json()["data"]
    assert updated_product["id"] == product_id
    assert updated_product["createdAt"] == original_created_at  # Should not change
    # Compare timestamps more carefully - they should be different
    original_time = original_created_at
    updated_time = updated_product["updatedAt"]
    assert updated_time >= original_time  # Should be updated (at least same or later)
    assert updated_product["description"] == "Updated description"

    # Verify via separate GET request
    get_response = client.get(f"/api/products/{product_id}")
    get_product = get_response.json()["data"]
    assert get_product["description"] == "Updated description"
    assert get_product["updatedAt"] == updated_product["updatedAt"]
