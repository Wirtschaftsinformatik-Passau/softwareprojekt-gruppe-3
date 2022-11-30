from flask import Blueprint, render_template

# store the standard routes for a website where the user can navigate to

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("home.html")
