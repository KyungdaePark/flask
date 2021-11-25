import bcrypt
import pytest
import config

from model import UserDao, TweetDao
from sqlalchemy import create_engine, text
database = create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=0)

@pytest.fixture
def user_dao():
    return UserDao(database)

@pytest.fixture
def tweet_dao():
    return TweetDao(database)

def setup_function():
    ## create a test user
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
    
def get_user(user_id):
    row = database.execute(text("""
        SELECT id, name, email, profile
        FROM users
        WHERE id = :user_id                            
    """
    ), {
        'user_id' : user_id
    }).fetchone()
    
    return {
        'id' :row['id'],
        'name' :row['name'],
        'email' :row['email'],
        'profile' :row['profile']
    } if row else None
    
def get_follow_list(user_id):
    rows = database.execute(text(
    """
        SELECT follow_user_id
        FROM users_follow_list
        WHERE user_id = :user_id
    """
    ),{
        'user_id' : user_id
    }).fetchall()
    
    return [int(row['follow_user_id']) for row in rows]
    
def test_insert_user(user_dao):
    new_user = {
        'email' : 'hong@test.com',
        #'hashed_password' : 'test1234',
        'password' : 'test1234', 
        'name' : '홍길동',
        'profile' : '서번동번'
    }
    
    new_user_id = user_dao.insert_user(new_user)
    user = get_user(new_user_id)
    
    assert user == {
        'id' : new_user_id,
        'name' : new_user['name'],
        'email' : new_user['email'],
        'profile' : new_user['profile']
    }
    
def test_get_user_id_and_pasword(user_dao):
    # 1. get_user_id_and_password 함수를 이용해서 해쉬 비번을 가져온다.
    user_credential = user_dao.get_user_id_and_password(
            email = "pkdtesting@gmail.com"
        )
    
    #2. 사용자 아이디가 맞는지 확인한다.
    assert user_credential['id']==1
    #3. 가져온 해쉬 비번이 진짜랑 맞는지 확인한다
    assert bcrypt.checkpw('test password'.encode('UTF-8'), 
                user_credential['hashed_password'].encode('UTF-8')
            )
    
def test_insert_follow(user_dao):
    user_dao.insert_follow(
        user_id = 1,
        follow_id = 2
    )
    assert get_follow_list(1) == [2]
    
def test_insert_unfollow(user_dao):
    user_dao.insert_follow(
        user_id = 1,
        follow_id = 2
    )
    user_dao.insert_unfollow(
        user_id = 1,
        unfollow_id = 2
    )
    assert get_follow_list(1) == []

def test_insert_tweet(tweet_dao):
    tweet_dao.insert_tweet(1, "tweet test")
    test_timeline = tweet_dao.get_timeline(1)
    assert test_timeline == [{
        'user_id' : 1,
        'tweet' : "tweet test"
    }]
    
def test_get_timeline(user_dao, tweet_dao):
    tweet_dao.insert_tweet(1, "tweet test")
    user_dao.insert_follow(1,2)
    
    test_timeline = tweet_dao.get_timeline(1)
    
    assert test_timeline == [
        {
            'user_id' : 2,
            'tweet' : "Hello World2!"
        },
        {
            'user_id' : 1,
            'tweet' : "tweet test"    
        } 
    ]