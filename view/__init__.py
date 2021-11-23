#view : presentation layer : http 통신위주
import jwt

from flask import request, jsonify, current_app, Response, g
from flask.json import JSONEncoder
from functools import wraps

class CustomJSONEncoder(JSONEncoder):
    def default(self,obj):
        if isinstance(obj,set):
            return list(obj)
        
        return JSONEncoder.default(self,obj)
    
##########DECORATORS############
def login_required(f):
    @wraps(f)
    def decofunc(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token,current_app.config['JWT_SECRET_KEY'],'HS256')
            except jwt.InvalidTokenError:
                payload = None
            if payload is None : return Response(status=401)
            user_id = payload['user_id']
            g.user_id = user_id
        else:
            return Response(status=401)
            
        return f(*args, **kwargs)
    return decofunc

def create_endpoint(app,services):
    app.json_encoder = CustomJSONEncoder
    
    #####service : business layer : user와 tweet기능 담당#####
    user_service = services.user_service
    tweet_service = services.tweet_service
    ##########################################################
    
    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"
    
    @app.route("/sign-up", methods=['POST'])
    def singup():
        new_user = request.json
        # new_user['password'] = bcrypt.hashpw(
        #     new_user['password'].encode('UTF-8'),bcrypt.gensalt()
        # )
        new_user = user_service.create_new_user(new_user) # lastrowid가 들어온다...?
        # inserted_user = insert_user(new_user) #입력받은 정보를 sql에 넣을 수 있도록 가공
        # got_user = get_user(inserted_user) # sql로부터 방금 넣은 정보를 불러옥 위해서 사용
        return jsonify(new_user)
    
    @app.route("/login", methods=['POST']) #login email, password
    def login():
       credential = request.json
       authorized = user_service.login(credential)
       
       if authorized:
           user_credential = user_service.get_user_id_and_password(credential['email'])
           user_id = user_credential['id']
           token = user_service.generate_access_token(user_id)
           
           return jsonify({
               'user_id' :user_id,
               'access_token' :token
           })
           
       else:
           return '',401
       
    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet():
        payload = request.json
        user_id = payload['id']
        tweet = payload['tweet']
        # if(len(tweet) > 300):
        #     return "300자를 초과했습니다.",400
        
        # insert_tweet(payload)
        
        result = tweet_service.tweet(user_id, tweet)
        if result is None:
            return '300자 초과',400
        
        return '',200
    
    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        user_id = g.user_id
        follow_id = payload['follow_user_id']
        # insert_follow(payload)
        user_service.follow(user_id, follow_id)
        
        return '',200
    
    
    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        user_id = g.user_id
        unfollow_id = payload['unfollow_user_id']
        # delete_follow(payload)
        
        user_service.unfollow(user_id, unfollow_id)

        return '',200

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        # timelines = send_timeline(user_id)   
        timelines = tweet_service.get_timeline(user_id)
        
        return jsonify({
            'user_id' : user_id,
            'timeline' : timelines
        })
        
    @app.route('/timeline', methods=['GET'])
    @login_required
    def user_timeline():
        timelines = tweet_service.get_timeline(g.user_id)
        
        return jsonify({
            'user_id'  : g.user_id,
            'timeline' : timelines
        })