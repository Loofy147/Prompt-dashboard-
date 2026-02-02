import pytest
import sys
import os
import json

# Add api to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from app import app, db, PromptModel

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_health_check(client):
    rv = client.get('/api/health')
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == 'healthy'
    assert 'bolt ⚡' in json_data['mode']

def test_create_and_list_prompts(client):
    # Create
    rv = client.post('/api/prompts', json={
        'text': 'You are a Senior Architect. Output JSON.',
        'tags': ['tech']
    })
    assert rv.status_code == 201
    data = rv.get_json()
    assert data['version'] == 1

    # List
    rv = client.get('/api/prompts')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1

def test_versioning(client):
    # Initial
    rv = client.post('/api/prompts', json={'text': 'Original'})
    p1_id = rv.get_json()['id']

    # Version 2
    rv = client.post('/api/prompts', json={'text': 'V2', 'parent_id': p1_id})
    data = rv.get_json()
    assert data['version'] == 2
    assert data['parent_id'] == p1_id

def test_variants(client):
    rv = client.post('/api/prompts', json={'text': 'This is a long test prompt for variants. It needs to have multiple sentences.'})
    p_id = rv.get_json()['id']

    rv = client.post(f'/api/prompts/{p_id}/variants')
    assert rv.status_code == 201
    data = rv.get_json()
    assert len(data['variants']) == 3
    assert any(v['type'] == 'commanding' for v in data['variants'])

def test_export(client):
    client.post('/api/prompts', json={'text': 'Export me'})

    # JSON
    rv = client.get('/api/prompts/export')
    assert rv.status_code == 200
    assert len(rv.get_json()) == 1

    # CSV
    rv = client.get('/api/prompts/export?format=csv')
    assert rv.status_code == 200
    assert 'Export me' in rv.get_data(as_text=True)
    assert rv.headers['Content-Type'] == 'text/csv'
