import pytest
import bcrypt
import json
import config

from app import create_app
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding= 'utf-8', max_overflow = 0)

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TESTING'] = True
    api = app.test_client()

    return api
def setup_function():
    ## Create a test user
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
    """), new_user)
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

def test_login(api):
    resp = api.post(
        '/login',
        data  = json.dumps(
            {'email' : 'pkdtesting@gmail.com', 'password' : 'test password'}
        ),
        content_type = 'application/json'
    )
    assert b"access_token" in resp.data 
    
def test_unauthorized(api):
    resp = api.post(
        '/tweet', 
        data = json.dumps(
            {'tweet' : "Hello World!"}
        ),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp  = api.post(
        '/follow',
        data = json.dumps({'follow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp  = api.post(
        '/unfollow',
        data = json.dumps({'unfollow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

def test_tweet(api):
    resp = api.post(
        '/login',
        data         = json.dumps(
            {'email' : 'pkdtesting@gmail.com', 
             'password' : 'test password'}
        ),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    ## tweet
    resp = api.post(
        '/tweet', 
        data = json.dumps({'tweet' : "Hello World!"}),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## tweet 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == [ 
            {
                'user_id' : 1,
                'tweet'   : "Hello World!"
            }
        ]

def test_follow(api):
    # 로그인
    resp = api.post(
        '/login',
        data = json.dumps(
            {'email' : 'pkdtesting@gmail.com', 
             'password' : 'test password'}
        ),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200

    # follow 유저 아이디 = 2
    resp  = api.post(
        '/follow',
        data         = json.dumps({'follow_user_id' : 2}),
        content_type = 'application/json',
        headers      = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 유저 1의 tweet 확인 해서 유저 2의 tweet의 리턴 되는것을 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == [
            {
                'user_id' : 2,
                'tweet'   : "Hello World2!"
            }
        ]
    

def test_unfollow(api):
    # 로그인
    resp = api.post(
        '/login',
        data  = json.dumps({'email' : 'pkdtesting@gmail.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp  = api.post(
        '/follow',
        data = json.dumps({'follow_user_id' : 2}),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 유저 1의 tweet 확인 해서 유저 2의 tweet의 리턴 되는것을 확인
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == [
            {
                'user_id' : 2,
                'tweet'   : "Hello World2!"
            }
        ]

    resp  = api.post(
        '/unfollow',
        data         = json.dumps({'unfollow_user_id' : 2}),
        content_type = 'application/json',
        headers      = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

     ## 이제 유저 1의 tweet 확인 해서 유저 2의 tweet이 더 이상 리턴 되지 않는 것을 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets  == []
