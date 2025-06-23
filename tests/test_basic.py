# tests/test_basic.py
from app import app

def test_home():
    client = app.test_client()
    res = client.get('/notes')
    assert res.status_code == 200

def test_add_note():
    client = app.test_client()
    res = client.post('/add', json={'note': 'Test note'})
    assert res.status_code == 200
    assert res.json == {"status": "ok"}