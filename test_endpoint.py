import config
from app2 import create_app
import pytest
import json
from sqlalchemy import create_engine, text
import bcrypt
database = create_engine(config.test_config['DB_URL'], encoding = 'utf-8', max_overflow = 0)

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api

def setup_function():
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )
    new_user = {
        'id' : 1,
        'email' : 'pkdtesting@gmail.com',
        'hashed_password' : hashed_password,
        'name' : '박경대',
        'profile' : 'test profile'
    }
    database.execute(text("""
        INSERT INTO users(
            name,
            email,
            profile,
            hashed_password
        ) VALUES(
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_user)
    
    new_user2 = {
        'id' : 2,
        'email' : 'pkdtesting2@gmail.com',
        'hashed_password' : hashed_password,
        'name' : '박경대2',
        'profile' : 'test profile'
    }
    database.execute(text("""
        INSERT INTO users(
            name,
            email,
            profile,
            hashed_password
        ) VALUES(
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_user2)
    
    #tweet user 2 미리 만들기
    database.execute(text(
        """ 
        INSERT INTO tweets(
            user_id,
            tweet
        ) VALUES(
            2,
            "Hello World2!"
        )
        """
    ))
     
    
def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    

def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data
    
def test_tweet(api):

    #login
    resp = api.post(
        '/login',
        data = json.dumps({
            'email' : 'pkdtesting@gmail.com',
            'password' : 'test password'
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
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'));
    
    assert resp.status_code == 200
    assert tweets == [
        {
            'user_id' : 1,
            'tweet' : 'Hello World!'
        }]
    
def test_unauthorized(api):
    #access token 없을때 401을 return 하는지?
    resp = api.post(
        '/tweet',
        data = json.dumps({
            'tweet' : 'Hello World!!'
        }),
        content_type = 'application/json'
    )
    assert resp.status_code == 401
    
    resp = api.post(
        '/unfollow',
        data = json.dumps({
            'unfollow_user_id' : 2
        }),
        content_type = 'appllication/json'
    )
    assert resp.status_code == 401
def test_follow(api):
    resp = api.post(
        '/login',
        data = json.dumps({
            'email' : 'pkdtesting@gmail.com',
            'password' : 'test password'
            }),
        content_type = 'application/json'
    )
    
    access_token = json.loads(resp.data.decode('utf-8'))['access_token']
    resp = api.post(
        '/follow',
        data = json.dumps({
            #'user_id' : 1,
            'follow_user_id' : 2
        }),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    
    assert resp.status_code == 200
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'));
    assert tweets == [{
       'user_id' : 2,
       'tweet' : "Hello World2!" 
    }]


def test_unfollow(api):
    resp = api.post(
        '/login',
        data = json.dumps({
            'email' : 'pkdtesting@gmail.com',
            'password' : 'test password'
            }),
        content_type = 'application/json'
    )
    
    access_token = json.loads(resp.data.decode('utf-8'))['access_token']
    resp = api.post(
        '/follow',
        data = json.dumps({
            #'user_id' : 1,
            'follow_user_id' : 2
        }),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    resp = api.post(
        '/unfollow',
        data = json.dumps({
            'user_id' : 1,
            'unfollow_user_id' : 2
        }),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    
    assert resp.status_code == 200
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'));
    assert tweets == []
