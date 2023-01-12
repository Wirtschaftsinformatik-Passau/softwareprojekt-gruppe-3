from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required, login_user
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date
import re
from datetime import date, datetime, timedelta

# store the standard routes for a website where the user can navigate to
nutzer_ohne_account_views = Blueprint('nutzer_ohne_account_views', __name__)

default_flughafen_von = "Passau"
default_flughafen_nach = "München"


def is_date_after_yesterday(date):
    # Convert the input date to a datetime object
    date = datetime.strptime(date, '%Y-%m-%d')

    # Get the current date and time
    now = datetime.today() - timedelta(days=1)

    # Compare the input date to the current date and time
    if date < now:
        return True
    else:
        return False


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
            flash('Mit dieser E-Mail-Adresse existiert bereits ein Account. Bitte melden Sie sich mit diesem an.',
                  category='error')
        elif passwort1 != passwort2:
            flash('Die angegebenen Passwörter müssen übereinstimmen.', category='error')
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
    # Passagiere, und ob Flug nicht annulliert ist.

    # is date today or in the future

    if abflug is not None and is_date_after_yesterday(abflug):
        flash('Bitte geben Sie ein Datum ein, welches in der Zukunft liegt', category='error')

    mögliche_fluege = Flug.query.filter(Flug.abflugid == vonID, Flug.zielid == nachID). \
        filter(cast(Flug.sollabflugzeit, Date) == request.args.get('Abflugdatum')).filter(
        Flug.flugstatus != "annulliert")

    buchbare_fluege = []

    # zählt Anzahl der bereits gebuchten passagiere und überprüft ob innherhalb der Kapazität des Flugzeugs und fügt sie
    # zu buchbaren Flügen hinzu

    for rows in mögliche_fluege:
        anzahl_ges_passagiere = Passagier.query.join(Buchung). \
            filter(Buchung.flugid == rows.flugid).filter(Passagier.buchungsid == Buchung.buchungsid).count()
        flugzeug_kapa = Flugzeug.query.get(rows.flugzeugid).anzahlsitzplaetze
        if (int(anzahl_ges_passagiere) + int(passagiere)) <= int(flugzeug_kapa):
            buchbare_fluege.append(rows)
            print(buchbare_fluege)

    if not buchbare_fluege:
        flash('Zu Ihren Suchkriterien wurde kein passender Flug gefunden', category='error')

    return render_template("nutzer_ohne_account/home.html", flughafen_liste=flughafen_liste,
                           user=current_user,
                           passagiere=passagiere,
                           today=date.today(), abflug=abflug, default_flughafen_von=default_flughafen_von,
                           default_flughafen_nach=default_flughafen_nach, buchbare_fluege=buchbare_fluege)


@nutzer_ohne_account_views.route('/flugstatus-überprüfen', methods=['GET', 'POST'])
def flugstatus_überprüfen():
    if request.method == 'GET':
        flughafen_liste = Flughafen.query.all()

        abflug = request.args.get('abflugdatum')
        flugnummer = request.args.get('flugnummer')

        # DATUM IN DER VERGANGENHEIT
        fluege = Flug.query.filter(cast(Flug.sollabflugzeit, Date) == abflug).filter(Flug.flugnummer == flugnummer)
        if not fluege:
            flash('Zu Ihren Suchenkriterien wurde kein passender Flug gefunden.', category='error')
            redirect(url_for('nutzer_ohne_account_views.flugstatus_überprüfen'))

        return render_template("nutzer_ohne_account/flugstatus_überprüfen.html", user=current_user, fluege=fluege,
                               abflug=abflug, flugnummer=flugnummer, today=date.today(),
                               flughafen_liste=flughafen_liste)


@nutzer_ohne_account_views.route('fluglinien-anzeigen', methods=['GET', 'POST'], defaults={"page": 1})
@nutzer_ohne_account_views.route('fluglinien-anzeigen/<int:page>', methods=['GET', 'POST'])
def fluglinien_anzeigen(page):
    flughafen_liste = Flughafen.query.all()
    page = page
    pages = 4

    # flüge müssen ab gestern in der Zukunft sein

    fluege = Flug.query.filter(Flug.sollabflugzeit > date.today() - timedelta(days=1)).with_entities(Flug.flugnummer,
                                                                                                     Flug.abflugid,
                                                                                                     Flug.zielid).distinct().paginate(
        page=page, per_page=pages, error_out=False)
    return render_template("nutzer_ohne_account/fluglinien_anzeigen.html", user=current_user, fluege=fluege,
                           flughafen_liste=flughafen_liste)
