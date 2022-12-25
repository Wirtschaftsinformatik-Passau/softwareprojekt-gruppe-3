from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck


# store the standard routes for a website where the user can navigate to
bodenpersonal_views = Blueprint('bodenpersonal_views', __name__)

@bodenpersonal_views.route('/bodenpersonal/passagier_suchen')
def passagier_suchen():
    render_template()


@bodenpersonal_views.route('/bodenpersonal/home')
def home():
    render_template()


@bodenpersonal_views.route('/bodenpersonal/einchecken')
def einchecken():
    render_template()



@bodenpersonal_views.route('/bodenpersonal/fluege_pruefen')
def fluege_pruefen():
    render_template()