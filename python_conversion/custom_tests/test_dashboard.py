import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from python_conversion.src.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_dashboard_index(client):
    response = client.get('/api/dashboard/index')
    assert response.status_code == 200
    data = response.get_json()
    assert 'stats' in data

def test_dashboard_newdemos(client):
    response = client.get('/api/dashboard/newdemos')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_dashboard_responderFile(client):
    response = client.get('/api/dashboard/responderFile')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
