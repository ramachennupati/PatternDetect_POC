import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_detect_no_file():
    r = client.post('/detect')
    assert r.status_code == 422  # missing file
