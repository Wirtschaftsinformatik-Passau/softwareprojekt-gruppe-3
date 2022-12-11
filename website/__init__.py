from flask import Flask
from flask_sqlalchemy import SQLAlchemy


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

    from .models import Flughafen, Flugzeug, Nutzerkonto

    return app
