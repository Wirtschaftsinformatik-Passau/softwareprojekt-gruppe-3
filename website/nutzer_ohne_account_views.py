from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required, login_user
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date
import re
from datetime import date

# store the standard routes for a website where the user can navigate to
nutzer_ohne_account_views = Blueprint('nutzer_ohne_account_views', __name__)


@nutzer_ohne_account_views.route('/registrieren', methods=['GET', 'POST'])
def registrieren():
    if request.method == 'POST':
        vorname = request.form.get("vorname")
        nachname = request.form.get("nachname")
        emailadresse = request.form.get("emailadresse")
        passwort1 = request.form.get("passwort1")
        passwort2 = request.form.get("passwort2")

        konto = Nutzerkonto.query.filter_by(emailadresse=emailadresse).first()
        if konto:
            flash('Konto existiert bereits !', category='error')
        elif passwort1 != passwort2:
            flash('Passwort stimmt nicht überein!', category='error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', emailadresse):
            flash('Ungültige Email Adresse !', category='error')
        elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&/+])[A-Za-z\d@$!%*#?&/+]{8,}$', passwort1):
            flash(
                'Passwort muss mindestens 8 Zeichen lang sein und mindestens eine Zahl und ein Sonderzeichen enthalten!',
                category='error')

        else:
            # Create a new user and add them to the database
            user = Nutzerkonto(vorname=vorname, nachname=nachname, emailadresse=emailadresse,

                               passwort=generate_password_hash(passwort1, method='sha256'), rolle="Passagier")
            db.session.add(user)
            db.session.commit()
            # Log the user in
            login_user(user, remember=True)
            flash('Sie haben sich erfolgreich registriert !', category='success')

            return redirect(url_for('nutzer_ohne_account_views.home'))

    return render_template("nutzer_ohne_account/registrieren.html", user=current_user)


# nutzer_ohne_account Funktionen
@nutzer_ohne_account_views.route('/', methods=['GET', 'POST'])
def home():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)

    vonID = Flughafen.query.filter(Flughafen.stadt == request.args.get('von')).with_entities(Flughafen.flughafenid)
    nachID = Flughafen.query.filter(Flughafen.stadt == request.args.get('nach')).with_entities(Flughafen.flughafenid)
    abflug = request.args.get('Abflugdatum')
    passagiere = request.args.get('AnzahlPersonen')

    kuerzel_von = Flughafen.query.filter(Flughafen.flughafenid == vonID).first()
    kuerzel_nach = Flughafen.query.filter(Flughafen.flughafenid == nachID).first()

    # Datenbankabfrage nach Abflug und Ziel Flughafen sowie Datum und Passagieranzahl < Summe bereits gebuchter
    # Passagiere

    fluege = Flug.query.filter(Flug.abflugid == vonID, Flug.zielid == nachID). \
        filter(cast(Flug.sollabflugzeit, Date) == abflug)

    return render_template("nutzer_ohne_account/home.html", fluege=fluege, flughafen_liste=flughafen_liste,
                           user=current_user,
                           kuerzel_nach=kuerzel_nach, kuerzel_von=kuerzel_von, passagiere=passagiere)


@nutzer_ohne_account_views.route('/flugstatus-überprüfen', methods=['GET', 'POST'])
def flugstatus_überprüfen():

    abflug = request.args.get('abflugdatum')
    flugnummer = request.args.get('flugnummer')

    fluege = Flug.query.filter(cast(Flug.sollabflugzeit, Date) == abflug).filter(Flug.flugnummer == flugnummer)

    return render_template("nutzer_ohne_account/flugstatus_überprüfen.html", user=current_user, fluege=fluege,
                           abflug=abflug, flugnummer=flugnummer, today=date.today())


@nutzer_ohne_account_views.route('fluglinien-anzeigen', methods=['GET', 'POST'], defaults={"page": 1})
@nutzer_ohne_account_views.route('fluglinien-anzeigen/<int:page>', methods=['GET', 'POST'])
def fluglinien_anzeigen(page):
    page = page
    pages = 4
    fluege = Flug.query.distinct(Flug.flugnummer).paginate(page=page, per_page=pages, error_out=False)
    return render_template("nutzer_ohne_account/fluglinien_anzeigen.html", user=current_user, fluege=fluege)
