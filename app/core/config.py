import os

try:
    config = {
        'user': os.environ["DB_USER"],
        'password': os.environ["DB_PASSWORD"],
        'host': os.environ["DB_HOST"],
        'db_name': os.environ["DB_NAME"]
    }
except KeyError:
    print("DB_USER, DB_PASSWORD, DB_HOST and DB_NAME environment variables were not provided, terminating!")
    exit(1)

db_uri = 'mysql+pymysql://%s:%s@%s/%s' % (config['user'], config['password'], config['host'], config['db_name'])