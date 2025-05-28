import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from python_conversion.src.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_reports_responderFile(client):
    response = client.get('/api/reports/responderFile')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_feedmanager_report(client):
    response = client.get('/api/reports/feedmanagerreport')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
