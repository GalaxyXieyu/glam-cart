import pytest
import os
import tempfile
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your app and dependencies
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db
from models import Base
from auth import create_admin_user

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Override the get_db dependency for this session
    def override_get_db_for_test():
        try:
            yield session
        finally:
            pass  # Don't close here, we'll handle it in cleanup

    app.dependency_overrides[get_db] = override_get_db_for_test

    # Create admin user for each test
    try:
        from models import User
        from auth import get_password_hash

        # Delete existing admin if any
        existing_admin = session.query(User).filter(User.username == 'admin').first()
        if existing_admin:
            session.delete(existing_admin)
            session.commit()

        # Create new admin user
        admin_user = User(
            username='admin',
            hashed_password=get_password_hash('password'),
            role='admin',
            is_active=True
        )
        session.add(admin_user)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error creating admin user: {e}")
        # Try with create_admin_user function as fallback
        try:
            create_admin_user(session)
            session.commit()
        except Exception as e2:
            session.rollback()
            print(f"Fallback admin creation also failed: {e2}")

    yield session

    # Cleanup
    try:
        session.close()
    except:
        pass
    try:
        transaction.rollback()
    except:
        pass
    try:
        connection.close()
    except:
        pass

    # Reset dependency override
    app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def admin_token(client):
    """Get admin authentication token."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "password"
    })
    assert response.status_code == 200
    return response.json()["data"]["token"]

@pytest.fixture(scope="function")
def auth_headers(admin_token):
    """Get authentication headers."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def temp_upload_dir():
    """Create temporary upload directory."""
    temp_dir = tempfile.mkdtemp()
    original_upload_dir = os.environ.get("UPLOAD_DIR", "static/images")
    os.environ["UPLOAD_DIR"] = temp_dir
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.environ["UPLOAD_DIR"] = original_upload_dir

@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Lipstick Tube",
        "code": "TEST001",
        "description": "A test lipstick tube for testing purposes",
        "tube_type": "口红管",
        "functional_designs": ["磁吸", "透明/透色"],
        "shape": "圆形",
        "material": "PETG",
        "dimensions": {
            "weight": 15.5,
            "length": 10.2,
            "width": 2.1,
            "height": 2.1,
            "capacity": {"min": 3.5, "max": 4.0}
        },
        "cost_price": 2.50,
        "factory_price": 1.80,
        "has_sample": True,
        "box_dimensions": "50x30x20cm",
        "box_quantity": 100,
        "in_stock": True,
        "popularity_score": 85
    }

@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    from PIL import Image
    import io
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return ("test_image.jpg", img_bytes, "image/jpeg")
