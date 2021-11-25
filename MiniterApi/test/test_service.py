import config
import pytest
import bcrypt 
import jwt

from sqlalchemy import create_engine, text
from model import UserDao, TweetDao
from service import UserService, TweetService

database = create_engine(config.test_config['DB_URL'],encoding='utf-8',max_overflow=0)

@pytest.fixture
def user_service():
    return UserService(UserDao(database), config)

def tweet_service():
    return TweetService(TweetDao(database), config)

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
    
def test_create_new_user(user_service):
    new_user={
        'email' : 'hong@test.com',
        'password' : 'test1234', 
        'name' : '홍길동',
        'profile' : '서번동번'
    }
    
    new_user_id = user_service.create_new_user(new_user)
    created_user = get_user(new_user_id)
    
    assert created_user =={
        'id' : new_user_id,
        'name' : new_user['name'],
        'email' : new_user['email'],
        'profile' : new_user['profile']
    }

def test_login(user_service):
    user = {
        'email' : 'pkdtesting@gmail.com',
        'password' : 'test password'
    }
    assert user_service.login(user)
    
    wronguser ={
        'email' : 'pkdtesting@gmail.com',
        'password' : 'test password2'
    }
    
    assert not user_service.login(wronguser)
    
def test_generate_access_token(user_service):
    token = user_service.generate_access_token(1)
    payload = jwt.decode(token, config.JWT_SECRET_KEY, 'HS256')
    ## decode해서 같은 user_id가 나오는지 확인
    assert payload['user_id'] == 1
    
def test_follow(user_service):
    user_service.follow(1,2)
    follow_list = get_follow_list(1)
    assert follow_list == [2]
    
def test_unfollow(user_service):
    user_service.follow(1,2)
    user_service.unfollow(1,2)
    follow_list = get_follow_list(1)
    assert follow_list == []