from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required, login_user
from werkzeug.security import generate_password_hash
from . import db, log_event
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date
import re
from datetime import date, datetime, timedelta

# store the standard routes for a website where the user can navigate to
nutzer_ohne_account_views = Blueprint('nutzer_ohne_account_views', __name__)
default_flughafen_von = "Passau"
default_flughafen_nach = "München"

passwort_min_length=8

def is_date_after_yesterday(date, diff):
    # Convert the input date to a datetime object
    date = datetime.strptime(date, '%Y-%m-%d')

    # Get the current date and time
    now = datetime.today() - timedelta(days=diff)

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
            flash('Wiederholen Sie die Passworteingabe. Diese müssen übereinstimmen.', category='error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', emailadresse):
            flash('Ungültige Email Adresse !', category='error')
        elif  len(passwort1) < passwort_min_length:
            flash('Bitte geben Sie ein Passwort ein, welches mehr als 8 Zeichen hat.', category='error')
        elif not re.match(r'^(?=.*\d)(?=.*[/().,;+#*!%&?"-])[A-Za-z\d/().,;+#*!%&?"-]{8,}$', passwort1):
            flash(
                'Bitte geben Sie ein Passwort ein, welches mindestens eine Zahl und mindestens ein Sonderzeichen enthält.',
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

            log_event(user.emailadresse + ' hat ein Konto erstellt')

            return redirect(url_for('nutzer_ohne_account_views.home'))

    return render_template("nutzer_ohne_account/registrieren.html", user=current_user)


# nutzer_ohne_account Funktionen
# nutzer_ohne_account Funktionen
@nutzer_ohne_account_views.route('/', methods=['GET', 'POST'])
def home():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)

    vonID = Flughafen.query.filter(Flughafen.stadt == request.args.get('von', default_flughafen_von)).with_entities(
        Flughafen.flughafenid)
    nachID = Flughafen.query.filter(Flughafen.stadt == request.args.get('nach', default_flughafen_nach)).with_entities(
        Flughafen.flughafenid)
    abflug = request.args.get('Abflugdatum')
    passagiere = request.args.get('AnzahlPersonen', 1)

    # Default search

    if request.args.get('Abflugdatum') is None:
        buchbare_fluege = []

        mögliche_fluege = Flug.query.join(Flugzeug).filter(Flug.flugzeugid == Flugzeug.flugzeugid). \
            filter(Flug.abflugid == 6, Flug.zielid == 1).filter(Flugzeug.status != "inaktiv"). \
            filter(cast(Flug.sollabflugzeit, Date) == date.today() + timedelta(days=1)).filter(
            Flug.flugstatus != "annulliert")

        for rows in mögliche_fluege:
            anzahl_geb_passagiere = Passagier.query.join(Buchung). \
                filter(Buchung.flugid == rows.flugid).filter(Passagier.buchungsid == Buchung.buchungsid).count()
            flugzeug_kapa = Flugzeug.query.get(rows.flugzeugid).anzahlsitzplaetze
            if (int(anzahl_geb_passagiere) + int(passagiere)) <= int(flugzeug_kapa):
                buchbare_fluege.append(rows)

        return render_template("nutzer_ohne_account/home.html", flughafen_liste=flughafen_liste,
                               user=current_user,
                               passagiere=1,
                               tomorrow=date.today() + timedelta(days=1), abflug=abflug,
                               default_flughafen_von=default_flughafen_von,
                               default_flughafen_nach=default_flughafen_nach, buchbare_fluege=buchbare_fluege)

    # Datenbankabfrage nach Abflug und Ziel Flughafen sowie Datum und Passagieranzahl < Summe bereits gebuchter
    # Passagiere, und ob Flug nicht annulliert ist.

    # is date in the future

    if request.args.get('Abflugdatum') is not None and is_date_after_yesterday(request.args.get('Abflugdatum'), 0):
        flash('Bitte geben Sie ein Datum ein, welches in der Zukunft liegt', category='error')
        return render_template("nutzer_ohne_account/home.html", user=current_user, flughafen_liste=flughafen_liste)

    else:

        mögliche_fluege = Flug.query.join(Flugzeug).filter(Flug.flugzeugid == Flugzeug.flugzeugid). \
            filter(Flug.abflugid == vonID, Flug.zielid == nachID). \
            filter(cast(Flug.sollabflugzeit, Date) == request.args.get('Abflugdatum')).filter(
            Flug.flugstatus != "annulliert").filter(Flugzeug.status != "inaktiv")

        buchbare_fluege = []

        # zählt Anzahl der bereits gebuchten passagiere und überprüft ob innherhalb der Kapazität des Flugzeugs und
        # fügt sie zu buchbaren Flügen hinzu

        for rows in mögliche_fluege:
            anzahl_geb_passagiere = Passagier.query.join(Buchung). \
                filter(Buchung.flugid == rows.flugid).filter(Passagier.buchungsid == Buchung.buchungsid).count()
            flugzeug_kapa = Flugzeug.query.get(rows.flugzeugid).anzahlsitzplaetze
            if (int(anzahl_geb_passagiere) + int(passagiere)) <= int(flugzeug_kapa):
                buchbare_fluege.append(rows)

        # wenn keiner der flüge buchbar ist

        if not buchbare_fluege:
            flash('Zu Ihren Suchkriterien wurde kein passender Flug gefunden', category='error')

        log_event('User logged in')

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

        if request.args.get('abflugdatum') is not None and is_date_after_yesterday(
                request.args.get('abflugdatum'), 1):
            flash('Bitte geben Sie ein Datum ein, welches nicht in der Vergangenheit liegt', category='error')
            return render_template("nutzer_ohne_account/flugstatus_überprüfen.html", user=current_user)
        else:

            fluege = Flug.query.join(Flugzeug).filter(Flug.flugzeugid == Flugzeug.flugzeugid). \
                filter(cast(Flug.sollabflugzeit, Date) == abflug).filter(Flug.flugnummer == flugnummer). \
                filter(Flugzeug.status != "inaktiv")

            if fluege is None:
                flash('Zu Ihren Suchenkriterien wurde kein passender Flug gefunden.', category='error')

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

    fluege = Flug.query.filter(Flug.sollabflugzeit > (date.today() - timedelta(days=1))). \
        filter(Flug.flugstatus != "annulliert").with_entities(Flug.flugnummer,
                                                              Flug.abflugid,
                                                              Flug.zielid).distinct().paginate(
        page=page, per_page=pages, error_out=False)
    return render_template("nutzer_ohne_account/fluglinien_anzeigen.html", user=current_user, fluege=fluege,
                           flughafen_liste=flughafen_liste)
