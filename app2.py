#2021.11.14 app.py

from types import new_class
from flask import Flask, request, jsonify
from flask.json import JSONDecoder, JSONEncoder
from sqlalchemy.engine import create_engine
from api import *
from sqlalchemy import create_engine, text

class CustomJSONEncoder(JSONEncoder):
    def default(self,obj):
        if isinstance(obj,set):
            return list(obj)
        
        return JSONEncoder.default(self,obj)
    
def createApp():
    app = Flask(__name__) #flask app을 만든다.
    app.json_encoder = CustomJSONEncoder
    app.config.from_pyfile('config.py')
    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow = 0)
    #DB_URL = 'mysql+mysqlconnector://root:@localhost:3306/miniter?charset=utf8'
    #create_engine은 데이터베이스와 연결해주는 역할을 한다.
    app.database = database;
    
    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"
    
    @app.route("/sign-up", methods=['POST'])
    def singup():
        new_user = request.json
        inserted_user = insert_user(new_user) #입력받은 정보를 sql에 넣을 수 있도록 가공
        got_user = get_user(inserted_user) # sql로부터 방금 넣은 정보를 불러옥 위해서 사용
        return jsonify(got_user)
    
    @app.route("/tweet", methods=['POST'])
    def tweet():
        payload = request.json
        tweet = payload['tweet']
        if(len(tweet) > 300):
            return "300자를 초과했습니다.",400
        
        insert_tweet(payload)
        
        return '',200
        
    @app.route("/follow", methods=['POST'])
    def follow():
        payload = request.json
        user_id = payload['user_id']
        follow_user_id = payload['follow_user_id']

        insert_follow(payload)
        
        return '',200
    
    @app.route("/unfollow", methods=['POST'])
    def unfollow():
        payload = request.json
        delete_follow(payload)

        return '',200
    
    @app.route("/timeline/<int:user_id>", methods=['POST'])
    def timeline(user_id):
        timelines = send_timeline(user_id)   
        return jsonify(timelines)
    
    return app
    
    
    


if __name__ == '__main__':
    app = createApp()
    app.run(host='localhost', port=5000, debug=True)
