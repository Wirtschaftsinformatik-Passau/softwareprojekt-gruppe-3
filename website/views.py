from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Flug, Flughafen, Flugzeug
from . import db
import json

# store the standard routes for a website where the user can navigate to
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    von = request.args.get('Von')
    nach = request.args.get('Nach')
    abflug = request.args.get('Abflugdatum')
    passagiere = request.args.get('AnzahlPersonen')
    print(von, nach, abflug, passagiere)
    fluege = Flug.query.all()
    return render_template("home.html", fluege=fluege)


@views.route('/suchen')
def flug_suchen():
    alle_flughafen = Flugzeug.query.all()
    return render_template("flugsuchen.html", alle_flughafen=alle_flughafen)


@views.route('/flugzeug_erstellen', methods=['GET', 'POST'])
def flugzeug_erstellen():
    if request.method == 'POST':
        modell = request.form.get('Modell')
        hersteller = request.form.get('Hersteller')
        anzahlsitzplaetze = request.form.get('anzahlsitzplaetze')

        new_flugzeug = Flugzeug(modell=modell, hersteller=hersteller, anzahlsitzplaetze=anzahlsitzplaetze)
        db.session.add(new_flugzeug)
        db.session.commit()
        flash('Flugzeug added!', category='success')

    return render_template("Verwaltungspersonal/flugzeug_erstellen.html")
