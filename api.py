from flask import current_app
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from api import *
import bcrypt
import jwt

def login_user(payload):
    input_password = payload['password']
    row = current_app.database.execute(text(
    """
        SELECT id, hashed_password
        FROM users
        WHERE email = :email
    """
    ),payload).fetchone()
    
    if row and bcrypt.checkpw(
        input_password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
        user_id = row['id']
        jwt_create = {
            'user_id' :user_id,
            'exp' : datetime.utcnow() + timedelta(seconds=60*60*24) #exp는 유효기간 : 1일
        }
        token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], 'HS256')
        
        return token
    else:
        return '',401
def insert_user(user):
    new_user_data =  current_app.database.execute(text("""
        INSERT INTO users(
            name,
            email,
            profile,
            hashed_password
        ) VALUES(
            :name,
            :email,
            :profile,
            :password
        )
    """), user).lastrowid
    #SQL 구문을 LASTROWID를 이용해서 전달. :name은 post로 보내는 인자에서 value가 name인 값의 key로 대체한다는 뜻, 즉 name=[보내는name]이 됨.
    return new_user_data

def get_user(user):
    sending_user = current_app.database.execute(text("""
        SELECT
            id, name, email, profile
        FROM
            users
        WHERE id = :id
    """),{
        'id' :user #user : lastrowid를 이용해 id가 반환되어 있음 : user는 마지막으로 만든 계정의 id를 담고 있음
    }).fetchone()

    send_info = { #jsonify할 수 있는 형식으로 바꿈
        'id' : sending_user['id'],
        'name' : sending_user['name'],
        'email' : sending_user['email'],
        'profile' : sending_user['profile']
    } if sending_user else None
    
    return send_info
    
def insert_tweet(tweet):
    current_app.database.execute(text("""
        INSERT INTO tweets(
            user_id,
            tweet
        ) VALUES(
            :id,
            :tweet
        )
    """),tweet)
   
def insert_follow(user):
    current_app.database.execute(text("""
        INSERT INTO users_follow_list(
            user_id,
            follow_user_id
        ) VALUES(
            :user_id,
            :follow_user_id
        )
    """),user)
    
def delete_follow(user):
    current_app.database.execute(text(
    """
        DELETE FROM users_follow_list
        WHERE user_id = :user_id
        AND follow_user_id = :unfollow_user_id
    """ 
    ), user)
    
def send_timeline(user_id): #user_id 는 int값
    rows = current_app.database.execute(text(
    """
        SELECT tweets.tweet, tweets.user_id
        FROM tweets
        LEFT JOIN users_follow_list ON users_follow_list.user_id = :user_id
        WHERE tweets.user_id =:user_id
        OR tweets.user_id = users_follow_list.follow_user_id
    """
    ),{'user_id' : user_id}).fetchall()
    #WHERE : 내가 팔로우한사람이 팔로우한사람(n차팔로우)한사람의 트윗은 보지 않도록 하기 위해서
   #서 left join하여 나온 사람 & 나랑만 관련있는 사람(팔로우를 한 사람을 하고있는 사람의 id가 내 id와 같은경우)
    timeline = [{
        'user_id' : row['user_id'],
        'tweet' : row['tweet']
    } for row in rows]
    
    return timeline
    
    
    
    
    