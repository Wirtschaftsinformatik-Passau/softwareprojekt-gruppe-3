from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import datetime

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format("clara", "1234", "localhost", "airline")
db = SQLAlchemy()
mail = Mail()
app = Flask(__name__)


def log_event(event):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('flask.log', 'a') as logfile:
        logfile.write(f'{now} - {event}\n')


def create_app():
    global app
    # app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hdfsoanfi sfnkosnfmeu'
    app.config['SQLALCHEMY_DATABASE_URI'] = conn
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'airpassau.de@gmail.com'
    app.config['MAIL_PASSWORD'] = 'xelxozlfzphverxt'
    db.init_app(app)

    from website.controller.nutzer_ohne_account_controller import nutzer_ohne_account_views
    from website.controller.nutzer_mit_account_controller import nutzer_mit_account_views
    from website.controller.passagier_controller import passagier_views
    from website.controller.verwaltungspersonal_controller import verwaltungspersonal_views
    from website.controller.bodenpersonal_controller import bodenpersonal_views

    app.register_blueprint(nutzer_ohne_account_views, url_prefix='/')
    app.register_blueprint(nutzer_mit_account_views, url_prefix='/')
    app.register_blueprint(passagier_views, url_prefix='/')
    app.register_blueprint(verwaltungspersonal_views, url_prefix='/')
    app.register_blueprint(bodenpersonal_views, url_prefix='/')

    from website.model.models import Flughafen, Flugzeug, Nutzerkonto, Passagier, Gepaeck
    login_manager = LoginManager()
    login_manager.login_view = "nutzer_mit_account_views.anmelden"  # if the user is not logged in then he will be directed to login page
    login_manager.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Nutzerkonto.query.get(int(id))

    return app


"""
@app.route("/log/")
def logging():
    # [2023-01-17 11:21:27,054] INFO in __init__: Hier ist ein Log.
    # in app app.
    # Error -> warning -> debug -> info
    log_files = glob('path/to/logs.log.*')
    app.logger.info("Hier ist ein Log.")
    log = ''
    for log_file in log_files:
        with open(log_file, 'r') as f:
            log += f.read()
    return render_template("Verwaltungspersonal/logging.html", log=log)

"""
