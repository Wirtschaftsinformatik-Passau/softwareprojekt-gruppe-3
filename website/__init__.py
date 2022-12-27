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

    from .nutzer_ohne_account_views import nutzer_ohne_account_views
    from .nutzer_mit_account_views import nutzer_mit_account_views
    from .passagier_views import passagier_views
    from .verwaltungspersonal_views import verwaltungspersonal_views

    app.register_blueprint(nutzer_ohne_account_views, url_prefix='/')
    app.register_blueprint(nutzer_mit_account_views, url_prefix='/')
    app.register_blueprint(passagier_views, url_prefix='/')
    app.register_blueprint(verwaltungspersonal_views, url_prefix='/')

    from .models import Flughafen, Flugzeug, Nutzerkonto, Passagier, Gepaeck
    login_manager = LoginManager()
    login_manager.login_view = "nutzer_mit_account_views.anmelden"  # if the user is not logged in then he will be directed to login page
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Nutzerkonto.query.get(int(id))

    return app
