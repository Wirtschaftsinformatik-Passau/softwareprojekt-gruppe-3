from flask import Flask, request, jsonify, has_request_context, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import logging
from logging.handlers import RotatingFileHandler
from glob import glob
import werkzeug

# customizing the Log file can be saved in seperate file by adding: filename="logs.log",
# logging.basicConfig(format="%(levelname)s:%(name)s_:%(message)s")

logger = logging.getLogger()

# logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # add console handler to the root logger
consoleHanlder = logging.StreamHandler()
consoleHanlder.setFormatter(logFormatter)  # customized format is applied
logger.addHandler(consoleHanlder)

    # add file handler to the root logger
fileHandler = RotatingFileHandler("logs.log", backupCount=100, maxBytes=1024)  # displays latest 100 logs
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)


conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format("merie", "1234", "localhost", "airline")
db = SQLAlchemy()
mail = Mail()
app = Flask(__name__)


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

    from .nutzer_ohne_account_views import nutzer_ohne_account_views
    from .nutzer_mit_account_views import nutzer_mit_account_views
    from .passagier_views import passagier_views
    from .verwaltungspersonal_views import verwaltungspersonal_views
    from .bodenpersonal_views import bodenpersonal_views

    app.register_blueprint(nutzer_ohne_account_views, url_prefix='/')
    app.register_blueprint(nutzer_mit_account_views, url_prefix='/')
    app.register_blueprint(passagier_views, url_prefix='/')
    app.register_blueprint(verwaltungspersonal_views, url_prefix='/')
    app.register_blueprint(bodenpersonal_views, url_prefix='/')

    from .models import Flughafen, Flugzeug, Nutzerkonto, Passagier, Gepaeck
    login_manager = LoginManager()
    login_manager.login_view = "nutzer_mit_account_views.anmelden"  # if the user is not logged in then he will be directed to login page
    login_manager.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Nutzerkonto.query.get(int(id))

    return app


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
    return render_template("Verwaltungspersonal/log.html", log=log)


