db = {
    'user' : 'root',
    'password' : '',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'miniter'
}

test_db = {
    'user' : 'root',
    'password' : '',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'test_miniter'
}

test_config ={
    'DB_URL' : f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY' : 'SOME_SUPER_SECRET_KEY'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

JWT_SECRET_KEY = 'SOME_SUPER_SECRET_KEY'