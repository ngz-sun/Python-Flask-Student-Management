import os
import pymysql

SECRET_KEY = os.urandom(24)

DIALECT = "mysql"
DRTVER = "pymysql"
USERNAME ="root"
PASSWORD ="666666"
HOST = "127.0.0.1"
PORT="3306"
DATABASE = "studentbase"

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4".format(DIALECT,DRTVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False