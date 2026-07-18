"""Unit tests for the Flask application."""
import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models import Item

@pytest.fixture
def app() -> Flask:
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_item(app: Flask) -> Item:
    """Create a sample item for testing."""
    item = Item(name='Test Item', description='Test Description')
    db.session.add(item)
    db.session.commit()
    return item

def test_index_page(client: FlaskClient) -> None:
    """Test the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Flask Learning' in response.data
    assert b'What you can learn' in response.data

def test_create_item(client: FlaskClient) -> None:
    """Test creating a new item."""
    response = client.post('/items/add', data={
        'name': 'Test Item',
        'description': 'Test Description'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Item "Test Item" created successfully!' in response.data
    
    # Check item was created
    item = Item.query.first()
    assert item is not None
    assert item.name == 'Test Item'
    assert item.description == 'Test Description'

def test_create_item_validation(client: FlaskClient) -> None:
    """Test form validation when creating an item."""
    response = client.post('/items/add', data={
        'name': '',  # Empty name should fail validation
        'description': 'Test'
    })
    assert response.status_code == 200
    assert b'Name is required' in response.data
    
    # Check no item was created
    assert Item.query.count() == 0

def test_list_items(client: FlaskClient, sample_item: Item) -> None:
    """Test the items listing page."""
    response = client.get('/items')
    assert response.status_code == 200
    assert b'Test Item' in response.data
    assert b'Test Description' in response.data

def test_item_detail(client: FlaskClient, sample_item: Item) -> None:
    """Test viewing a single item."""
    response = client.get(f'/items/{sample_item.id}')
    assert response.status_code == 200
    assert b'Test Item' in response.data
    assert b'Test Description' in response.data

def test_api_items(client: FlaskClient, sample_item: Item) -> None:
    """Test the items API endpoint."""
    response = client.get('/api/items')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Test Item'
    assert data[0]['description'] == 'Test Description'

def test_api_single_item(client: FlaskClient, sample_item: Item) -> None:
    """Test the single item API endpoint."""
    response = client.get(f'/api/items/{sample_item.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Item'
    assert data['description'] == 'Test Description'

def test_api_delete_item(client: FlaskClient, sample_item: Item) -> None:
    """Test deleting an item via API."""
    assert Item.query.count() == 1
    
    response = client.delete(f'/items/{sample_item.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'deleted successfully' in data['message']
    
    # Check item was deleted
    assert Item.query.count() == 0

def test_api_update_item(client: FlaskClient, sample_item: Item) -> None:
    """Test updating an item via API."""
    response = client.put(f'/items/{sample_item.id}', json={
        'name': 'Updated Name',
        'description': 'Updated Description'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item updated successfully'
    assert data['item']['name'] == 'Updated Name'
    assert data['item']['description'] == 'Updated Description'
    
    # Check database was updated
    updated_item = Item.query.first()
    assert updated_item.name == 'Updated Name'
    assert updated_item.description == 'Updated Description'

def test_404_error(client: FlaskClient) -> None:
    """Test 404 error page."""
    response = client.get('/non-existent-page')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page Not Found' in response.data

def test_pagination(client: FlaskClient, app: Flask) -> None:
    """Test pagination functionality."""
    # Create 12 items (more than the 5 per page default)
    with app.app_context():
        for i in range(12):
            item = Item(name=f'Item {i}', description=f'Description {i}')
            db.session.add(item)
        db.session.commit()
    
    # First page
    response = client.get('/items?page=1')
    assert response.status_code == 200
    assert b'Item 0' in response.data
    assert b'Next' in response.data
    
    # Last page
    response = client.get('/items?page=3')
    assert response.status_code == 200
    assert b'Item 10' in response.data
    assert b'Previous' in response.data