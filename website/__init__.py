from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import help

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format("root", help.pss, "localhost", "airlinedb")
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
    from .models import Nutzerkonto
    login_manager = LoginManager()
    login_manager.login_view = "auth.anmelden"  # if the user is not logged in then he will be directed to login page
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Nutzerkonto.query.get(int(id))

    return app
