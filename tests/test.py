import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # Create a test user
        user = User(email="test@example.com", name="Test", password=generate_password_hash("test123"))
        db.session.add(user)
        db.session.commit()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, email, password):
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

def test_login_logout(client):
    # Test login page loads
    response = client.get('/login')
    assert response.status_code == 200
    # Test login with correct credentials
    response = login(client, "test@example.com", "test123")
    assert b"READLIST" in response.data or b"Profile" in response.data
    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert b"LOG IN" in response.data or b"login" in response.data

def test_protected_home_requires_login(client):
    # Should redirect to login if not authenticated
    response = client.get('/', follow_redirects=True)
    assert b"LOG IN" in response.data or b"login" in response.data