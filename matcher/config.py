class Config:
    MYSQL_DB_USER = 'root'
    MYSQL_DB_PASSWORD = ''

    DB_ENGINE = f'mysql://{MYSQL_DB_USER}:{MYSQL_DB_PASSWORD}@127.0.0.1:3306/'
    DB_NAME = 'matcher'
    SQLALCHEMY_DATABASE_URI = f"{DB_ENGINE}{DB_NAME}"
    FLASK_ADMIN_URL = '/'
