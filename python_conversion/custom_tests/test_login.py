
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from python_conversion.src.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_post(client):
    response = client.post('/api/login', json={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 200 or response.status_code == 401
    data = response.get_json()
    assert 'message' in data or 'token' in data

def test_login_get(client):
    response = client.get('/api/login')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
