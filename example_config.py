import os

basedir = os.path.abspath(os.path.dirname(__file__))

MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = ''
MYSQL_HOST = 'localhost'
MYSQL_DB = 'shapeshift'

class Config:
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False