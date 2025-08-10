import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sreyeesh Garimella' in response.data
    assert b'Mentoring' in response.data

def test_home_page_content(client):
    """Test that the page contains expected content"""
    response = client.get('/')
    assert b'Book Your Session' in response.data
    assert b'Focus Areas' in response.data
    assert b'Contact' in response.data

def test_static_files(client):
    """Test that static files are accessible"""
    response = client.get('/static/css/style.css')
    assert response.status_code == 200

def test_404_page(client):
    """Test that 404 pages are handled properly"""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
