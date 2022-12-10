from flask import Blueprint, render_template, Flask

# store the standard routes for a website where the user can navigate to

auth = Blueprint('auth', __name__)


@auth.route('/anmelden')
def anmelden():
    return render_template("user_authentification/anmelden.html")


@auth.route('/logout')
def logout():
    return render_template("user_authentification/logout.html")


@auth.route('/registrieren')
def registrieren():
    return render_template("user_authentification/registrieren.html")
