import config
from app2 import create_app
import pytest
import json
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding = 'utf-8', max_overflow = 0)

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api

def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data
    
def test_tweet(api):
    #signup
    new_user = {
        'email' : 'testpkd10@gmail.com',
        'password' : '1234',
        'name' : '박경대',
        'profile' : 'test profile'
    }
    resp = api.post(
        '/sign-up',
        data = json.dumps(new_user),
        content_type ='application/json'
    )
    assert resp.status_code == 200
    
    new_user_id = json.loads(resp.data.decode('utf-8'))['id']
    
    #login
    resp = api.post(
        '/login',
        data = json.dumps({
            'email' : 'testpkd10@gmail.com',
            'password' : '1234'
            }),
        content_type = 'application/json'
    )
    
    access_token = json.loads(resp.data.decode('utf-8'))['access_token']

    #tweet
    resp = api.post(
        '/tweet',
        data = json.dumps({
            'tweet' : 'Hello World!'
        }),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )    
    
    assert resp.status_code == 200
    
    ##check tweet
    resp = api.get(f'/timeline/{new_user_id}')
    tweets = json.loads(resp.data.decode('utf-8'));
    
    assert resp.status_code == 200
    assert tweets == [
        {
            'user_id' : 18,
            'tweet' : 'Hello World!'
        }]
    
    
    
