from flask import Blueprint

# store the standard routes for a website where the user can navigate to

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return "<h1>Test</h1>"
