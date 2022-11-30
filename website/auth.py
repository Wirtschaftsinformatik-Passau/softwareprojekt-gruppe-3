from flask import Blueprint

# store the standard routes for a website where the user can navigate to

auth = Blueprint('auth', __name__)


@auth.route('login')
def login():
    return "<p>login</p>"


@auth.route('/logout')
def logout():
    return "<p>logout</p>"


@auth.route('/anmelden')
def anmelden():
    return "<p>anmelden</p>"
