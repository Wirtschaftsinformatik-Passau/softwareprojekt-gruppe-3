from flask import Flask
from flask_mysqldb import MySQL
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import pymysql

mydb = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Anne-frank1',
    port='3306',
    database='airlinedb'
)

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format("root", "Anne-frank1", "localhost", "airlinedb")
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hdfsoanfi sfnkosnfmeu'
    app.config['SQLALCHEMY_DATABASE_URI'] = conn
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Flugzeug, Nutzerkonto

    return app
