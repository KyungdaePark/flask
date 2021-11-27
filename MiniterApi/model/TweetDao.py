from sqlalchemy import text

class TweetDao:
    def __init__(self, database):
        self.db = database
        
    def insert_tweet(self, user_id, tweet):
        return self.db.execute(text("""
        INSERT INTO tweets(
            user_id,
            tweet
        ) VALUES(
            :id,
            :tweet
        )
    """),{
        'id' :user_id,
        'tweet' :tweet
    }).rowcount
        
    def get_timeline(self,user_id):
        rows = self.db.execute(text(
        """
            SELECT tweets.tweet, tweets.user_id
            FROM tweets
            LEFT JOIN users_follow_list ON users_follow_list.user_id = :user_id
            WHERE tweets.user_id =:user_id
            OR tweets.user_id = users_follow_list.follow_user_id
        """    
        ),{
            'user_id' :user_id
        }).fetchall()
        
        timeline = [{
        'user_id' : row['user_id'],
        'tweet' : row['tweet']
        } for row in rows]
        
        return timeline