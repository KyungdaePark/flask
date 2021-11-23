
class TweetDao:
    def __init__(self, database):
        self.db = database
        
    def insert_tweet(self, user_id, tweet):
        