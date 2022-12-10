from flask import Flask
from .database import mysql


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hdfsoanfi sfnkosnfmeu'
    app.config['MYSQL_DATABASE_USER'] = 'clara'
    app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
    app.config['MYSQL_DATABASE_DB'] = 'airline'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    mysql.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
