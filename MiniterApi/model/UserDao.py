from sqlalchemy import text

class UserDao:
    def __init__(self, database):
        self.db = database
        
    def insert_user(self, user):
        new_user_data =  self.db.execute(text("""
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
        return new_user_data
   
    def get_user_id_and_password(self,email):
        row = self.db.execute(text(
        """
        SELECT id, hashed_password
        FROM users
        WHERE email = :email
        """
       ),{
           'email' :email
         }).fetchone()
        
        return row
    # 책에서는 ,
    # return { 'id' :row['id'], 'hashed_password' : row['hashed_password]} if row else None
     
    def insert_follow(self, user_id, follow_id):
        self.db.execute(text("""
        INSERT INTO users_follow_list(
            user_id,
            follow_user_id
        ) VALUES(
            :user_id,
            :follow_user_id
        )
       """),{
        'user_id' :user_id,
        'follow_user_id' :follow_id
      }).rowcount #why rowcount?
        
    def insert_unfollow(self, user_id, unfollow_id):
        self.db.execute(text(
        """
        DELETE FROM users_follow_list
        WHERE user_id = :user_id
        AND follow_user_id = :unfollow_id
        """ 
    ), {
        'user_id' :user_id,
        'unfollow_id' :unfollow_id
      }).rowcount
