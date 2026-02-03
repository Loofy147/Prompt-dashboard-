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

def test_search_by_text(client):
    client.post('/api/prompts', json={'text': 'Find me this secret word', 'tags': ['tag1']})
    client.post('/api/prompts', json={'text': 'Nothing here', 'tags': ['tag2']})

    rv = client.get('/api/prompts/search?q=secret')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1
    assert 'secret' in data['prompts'][0]['text']

def test_search_by_tag(client):
    client.post('/api/prompts', json={'text': 'Text 1', 'tags': ['important']})
    client.post('/api/prompts', json={'text': 'Text 2', 'tags': ['normal']})

    rv = client.get('/api/prompts/search?q=important')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1
    assert 'important' in data['prompts'][0]['tags']

def test_search_empty(client):
    client.post('/api/prompts', json={'text': 'Text 1'})

    rv = client.get('/api/prompts/search?q=nonexistent')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 0

def test_search_no_query(client):
    client.post('/api/prompts', json={'text': 'Text 1'})
    client.post('/api/prompts', json={'text': 'Text 2'})

    rv = client.get('/api/prompts/search')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 2
