import random
import string
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from website import db, mail, log_event, role_required
from website.model.models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier
from sqlalchemy import or_, cast, Date, and_
from datetime import date, timedelta
from flask_mail import Message
import re
import matplotlib.pyplot as plt
import io
import base64

# store the standard routes for a website where the user can navigate to
verwaltungspersonal_views = Blueprint('verwaltungspersonal_views', __name__)

default_flughafen_von = "Passau"
default_flughafen_nach = "München"


def is_date_after_yesterday(date, diff):
    # Convert the input date to a datetime object
    date = datetime.strptime(date, '%Y-%m-%d %H:%M')

    # Get the current date and time
    now = datetime.now() - timedelta(days=diff)

    # Compare the input date to the current date and time
    if date < now:
        return True
    else:
        return False


def is_between(start_time, end_time):
    if start_time <= end_time:
        return start_time <= str(datetime.now()) <= end_time
    else:  # over midnight e.g., 23:30-04:15
        return str(datetime.now()) >= start_time or str(datetime.now()) <= end_time


# /F520/
# Diese Funktion erlaubt es dem Verwaltungspersonal, ein Flugzeug zu erstellen
@verwaltungspersonal_views.route('/home-vp', methods=['GET', 'POST'])
@verwaltungspersonal_views.route('/home-vp', methods=['GET', 'POST'])
@login_required
def flugzeug_erstellen():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    if request.method == 'POST':
        modell = request.form.get('Modell')
        hersteller = request.form.get('Hersteller')
        anzahlsitzplaetze = request.form.get('anzahlsitzplaetze')
        if int(anzahlsitzplaetze) < 0:
            flash('Die Anzahl der Sitzplätze muss größer oder gleich 0 sein!', category="error")
        else:
            new_flugzeug = Flugzeug(modell=modell, hersteller=hersteller, anzahlsitzplaetze=anzahlsitzplaetze)
            db.session.add(new_flugzeug)
            db.session.commit()
            log_event('Flugzeug (id = ' + str(
                new_flugzeug.flugzeugid) + ') wurde hinzugefügt. [von NutzerID = ' + str(current_user.id) + ']')
            flash('Flugzeug angelegt!', category='success')

    return render_template("Verwaltungspersonal/home_vp.html", user=current_user)


# /F530/
# Diese Funktion erlaubt es dem Verwaltungspersonal, ein Flugzeug zu bearbeiten. Zeigt nur die Tabelle an
@verwaltungspersonal_views.route('/flugzeug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/flugzeug-bearbeiten/<int:page>', methods=['GET', 'POST'])
@login_required
def flugzeug_bearbeiten(page):
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    page = page
    pages = 4

    # nur 4 flugzeuge werden angezeigt über paginate

    flugzeuge = Flugzeug.query.filter(Flugzeug.status == "aktiv").order_by(Flugzeug.flugzeugid.desc()). \
        paginate(page=page, per_page=pages, error_out=False)

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        flugzeuge = Flugzeug.query.filter(Flugzeug.hersteller.like(search)). \
            filter(Flugzeug.status == "aktiv").order_by(Flugzeug.flugzeugid.desc()).paginate(page=page, per_page=pages,
                                                                                             error_out=False)

        return render_template("Verwaltungspersonal/flugzeug_bearbeiten.html", flugzeuge=flugzeuge,
                               user=current_user, tag=tag)

    return render_template("Verwaltungspersonal/flugzeug_bearbeiten.html", flugzeuge=flugzeuge, user=current_user)


# hiermit können konkrete Änderungen durchgeführt werden
@verwaltungspersonal_views.route('/flugzeug-ändern', methods=['GET', 'POST'])
@login_required
def flugzeug_ändern():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    if request.method == 'POST':
        flugzeug = Flugzeug.query.get_or_404(request.form.get('id'))
        fluege_mit_flugzeug = Flug.query.join(Flugzeug).filter(Flug.flugzeugid == Flugzeug.flugzeugid). \
            filter(Flug.flugzeugid == request.form.get('id')). \
            filter(Flug.flugstatus != "annuliert")
        max_anzahl_passagier = 0
        for rows in fluege_mit_flugzeug:

            anzahl = Passagier.query.join(Buchung, Flug). \
                filter(Flug.flugid == Buchung.flugid).filter(Passagier.buchungsid == Buchung.buchungsid). \
                filter(Flug.flugid == rows.flugid). \
                filter(Buchung.buchungsstatus != 'storniert').filter(Flug.sollabflugzeit > date.today()).count()
            if anzahl > max_anzahl_passagier:
                max_anzahl_passagier = anzahl

        print(max_anzahl_passagier)

        flugzeug.modell = request.form['modell']
        flugzeug.hersteller = request.form['hersteller']

        if int(request.form['anzahlsitzplaetze']) < 0:
            flash('Die Anzahl der Sitzplätze muss größer oder gleich 0 sein!', category="error")
        elif max_anzahl_passagier > int(request.form['anzahlsitzplaetze']):
            flash('Die eingegebene Anzahl der Sitzplätze interferiert mit einem aktiven Flug. Bitte wenden Sie sich '
                  'an einen Vorgesetzten.', category="error")
        else:
            flugzeug.anzahlsitzplaetze = request.form['anzahlsitzplaetze']
            db.session.commit()

            log_event('Flugzeugdaten (id = ' + str(
                flugzeug.flugzeugid) + ') wurden geändert. [von NutzerID = ' + str(current_user.id) + ']')

            flash("Flugzeugdaten erfolgreich geändert")
        return redirect(url_for('verwaltungspersonal_views.flugzeug_bearbeiten'))


# Diese Hilfsfunktion setzt einen Flug inaktiv.
@verwaltungspersonal_views.route('/flugzeug-inaktiv-setzen/<int:id>', methods=['GET', 'POST'])
@login_required
def flugzeug_inaktiv_setzen(id):
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    flugzeug_inaktiv = Flugzeug.query.filter_by(flugzeugid=id).first()

    flug_mit_flugzeug = Flug.query.filter(Flug.flugzeugid == id).filter(Flug.flugstatus != "annuliert"). \
        filter(Flug.sollabflugzeit > date.today()).first()

    if flug_mit_flugzeug:
        flash('Das Flugzeug welches Sie löschen wollen ist mit einem aktiven Flug verbunden. Bitte wenden Sie sich '
              'an einen Vorgesetzten.', category="error")
    else:
        flugzeug_inaktiv.status = "inaktiv"
        db.session.merge(flugzeug_inaktiv)
        db.session.commit()
        flash(
            'Das Flugzeug wurde erfolgreich auf inaktiv gesetzt. Er befindet sich noch in der Datenbank aber kann '
            'nicht '
            'mehr für einen Flug ausgewählt werden', category="success")

        log_event('Flugzeug (id = ' + str(
            flugzeug_inaktiv.flugzeugid) + ') wurde auf inaktiv gesetzt. [von NutzerID = ' + str(current_user.id) + ']')

    return redirect(url_for('verwaltungspersonal_views.flugzeug_bearbeiten'))


# /F540/
# Diese Funktion erlaubt es dem Verwaltungspersonal, einen Flug anzulegen.
@verwaltungspersonal_views.route('/flug-anlegen', methods=['GET', 'POST'])
@login_required
def flug_anlegen():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)
    flugzeug_liste = Flugzeug.query.filter(Flugzeug.status == "aktiv").with_entities(Flugzeug.flugzeugid,
                                                                                     Flugzeug.hersteller,
                                                                                     Flugzeug.modell)
    if request.method == 'POST':
        flugzeugid = request.form["flugzeugtyp"]
        abflugid = Flughafen.query.filter(Flughafen.stadt == request.form.get('von')).first()
        zielid = Flughafen.query.filter(Flughafen.stadt == request.form.get('nach')).first()
        flugstatus = "pünktlich"
        abflugdatum = request.form.get('abflugdatum') + " " + request.form.get("abflugzeit")
        ankunftsdatum = request.form.get('ankunftsdatum') + " " + request.form.get("ankunftszeit")
        flugnummer = request.form.get('fluglinie')
        preis = request.form.get('preis')

        # check, ob ein Flug mit gleichen von und nach und abflugzeit existiert

        fluege = Flug.query.filter(Flug.abflugid == abflugid.flughafenid).filter(Flug.zielid == zielid.flughafenid). \
            filter(Flug.sollabflugzeit == abflugdatum).filter(Flug.sollankunftszeit == ankunftsdatum). \
            filter(Flug.flugzeugid == flugzeugid).filter(Flug.flugstatus != "annulliert")

        if is_date_after_yesterday(abflugdatum, 0):
            flash('Das Abflugdatum darf nicht in der Vergangenheit liegen',
                  category='error')
        elif abflugdatum > ankunftsdatum:
            flash('Der Ankunftszeit darf nicht vor der Abflugzeit sein. Bitte kontrollieren Sie die Eingabe',
                  category='error')
        elif abflugid.flughafenid == zielid.flughafenid:
            flash('Von und Nach dürfen nicht der gleichen Stadt entsprechen', category='error')
        elif fluege.first() is not None:
            flash('Der gleiche Flug existiert bereits. Wählen Sie andere Eingabedaten', category='error')
        else:

            new_flug = Flug(flugzeugid=flugzeugid, abflugid=abflugid.flughafenid, zielid=zielid.flughafenid,
                            flugstatus=flugstatus,
                            sollabflugzeit=abflugdatum, sollankunftszeit=ankunftsdatum,
                            istabflugzeit=abflugdatum, istankunftszeit=ankunftsdatum,
                            flugnummer=flugnummer,
                            preis=preis)

            db.session.add(new_flug)
            db.session.commit()

            log_event('Flug (id = ' + str(
                new_flug.flugid) + ') wurde angelegt. [von NutzerID = ' + str(current_user.id) + ']')

            flash('Flug hinzugefügt!', category='success')

    return render_template("Verwaltungspersonal/flug_anlegen.html", flughafen_liste=flughafen_liste, user=current_user,
                           flugzeug_liste=flugzeug_liste, default_flughafen_von=default_flughafen_von,
                           default_flughafen_nach=default_flughafen_nach, tomorrow=date.today() + timedelta(days=1))


# /F550/
# Diese Funktion erlaubt es dem Verwaltungspersonal, einen Flug zu bearbeiten.
@verwaltungspersonal_views.route('/flug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/flug-bearbeiten/<int:page>', methods=['GET', 'POST'])
@login_required
def flug_bearbeiten(page):
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    flughafen_liste = Flughafen.query.all()
    flugzeug_liste = Flugzeug.query.filter(Flugzeug.status == "aktiv").with_entities(Flugzeug.flugzeugid,
                                                                                     Flugzeug.hersteller,
                                                                                     Flugzeug.modell)
    page = page
    pages = 4

    # alle flüge von gestern bis in die Zukunft

    fluege = Flug.query.filter(Flug.istabflugzeit > date.today() - timedelta(days=1)).order_by(
        Flug.sollabflugzeit.desc()) \
        .paginate(page=page, per_page=pages, error_out=False)

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        fluege = Flug.query.filter(Flug.flugnummer.like(search)).order_by(Flug.flugid.desc()). \
            paginate(page=page, per_page=pages, error_out=False)

        return render_template("Verwaltungspersonal/flug_bearbeiten.html", fluege=fluege,
                               flughafen_liste=flughafen_liste,
                               user=current_user, tag=tag, flugzeug_liste=flugzeug_liste)

    return render_template("Verwaltungspersonal/flug_bearbeiten.html", fluege=fluege, user=current_user,
                           flugzeug_liste=flugzeug_liste,
                           flughafen_liste=flughafen_liste)


# Diese Funktion ermöglicht es dem Verwaltungspersonal, einen Flug zu annulieren.
@verwaltungspersonal_views.route('/flug-annulieren/<int:id>', methods=['GET', 'POST'])
@login_required
def flug_annulieren(id):
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))

    flug = Flug.query.get_or_404(id)
    if flug.flugstatus == "annulliert":
        flash('Flug wurde bereits annulliert!', category='error')
        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))

    elif is_between(str(flug.istabflugzeit), str(flug.istankunftszeit)):
        flash('Flug ist bereits gestartet. Sie können diesen Flug nicht mehr annullieren', category='error')
        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))

    else:
        flug.flugstatus = 'annulliert'
        db.session.commit()
        flughafen_von = Flughafen.query.filter(Flughafen.flughafenid == flug.abflugid).first()
        flughafen_nach = Flughafen.query.filter(Flughafen.flughafenid == flug.zielid).first()
        wann = flug.sollabflugzeit.strftime("%d.%m.%Y")

        emailadressen = ["test@default.com"]

        alle_nutzer = Nutzerkonto.query.join(Buchung).filter(Nutzerkonto.id == Buchung.nutzerid). \
            filter(Buchung.flugid == id).filter(Buchung.buchungsstatus != 'storniert')

        for rows in alle_nutzer:
            emailadressen.append(str(rows.emailadresse))

        msg = Message('Annullierung Ihres Fluges', sender='airpassau.de@gmail.com', recipients=emailadressen)
        msg.html = render_template('Verwaltungspersonal/Flug_annulliert_email.html',
                                   user=current_user, von=flughafen_von.stadt, nach=flughafen_nach.stadt, wann=wann)
        mail.send(msg)

        log_event('Flug (id = ' + str(
            flug.flugid) + ') wurde annulliert. [von NutzerID = ' + str(current_user.id) + ']')

        flash('Flug wurde erfolgreich annulliert', category='success')
        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))


@verwaltungspersonal_views.route('/flug-ändern/', methods=['GET', 'POST'])
@login_required
def flug_ändern():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    if request.method == 'POST':
        flug = Flug.query.get_or_404(request.form.get('id'))
        #alte werte speicher für vergleich
        old_price = flug.preis
        old_abflug_soll = str(flug.sollabflugzeit)
        old_ankunft_soll = str(flug.sollankunftszeit)
        old_abflug_ist = str(flug.istabflugzeit)
        old_ankunft_ist = str(flug.istankunftszeit)

        fliegt_schon = is_between(old_abflug_ist, old_ankunft_ist)

        print(old_ankunft_ist, str(datetime.now()), old_ankunft_ist < str(datetime.now()))

        flug.abflugid = request.form['von']
        flug.zielid = request.form['nach']
        flug.flugzeugid = request.form['flugzeugtyp']
        flug.preis = request.form['preis']
        flug.sollabflugzeit = request.form['abflugdatum'] + " " + request.form['sollabflugzeit'] + ":00"
        flug.sollankunftszeit = request.form['ankunftsdatum'] + " " + request.form['sollankunftszeit'] + ":00"
        flug.istabflugzeit = request.form['abflugdatum'] + " " + request.form['istabflugzeit']
        flug.istankunftszeit = request.form['ankunftsdatum'] + " " + request.form['istankunftszeit']
        flug.flugnummer = request.form['fluglinie']

        # check ob ein Flug mit gleichen von und nach und abflugzeit existiert
        if old_ankunft_ist < str(datetime.now()) or flug.flugstatus == "annulliert":
            flash('Der Flug ist bereits gelandet oder annulliert worden. Sie können keine Änderungen mehr vornehmen',
                  category='error')
        elif flug.sollabflugzeit > flug.sollankunftszeit or flug.istabflugzeit > flug.istankunftszeit:
            flash('Der Ankunftszeit darf nicht vor der Abflugzeit sein. Bitte kontrollieren Sie die Eingabe',
                  category='error')
        elif flug.abflugid == flug.zielid:
            flash('Von und Nach dürfen nicht der gleichen Stadt entsprechen', category='error')
        elif fliegt_schon and int(old_price) != int(request.form['preis']):
            flash('Der Flug ist bereits gestartet. Sie können den Preis nicht mehr ändern', category='error')
        elif fliegt_schon and old_abflug_soll != str(
                flug.sollabflugzeit) or old_ankunft_soll != str(flug.sollankunftszeit):
            flash('Der Flug ist bereits gestartet. Sie können die Sollzeiten nicht mehr ändern', category='error')
        else:

            if flug.istankunftszeit > flug.sollankunftszeit:
                flug.flugstatus = "verspätet"

            elif flug.istankunftszeit == flug.sollankunftszeit or flug.istankunftszeit < flug.sollankunftszeit:
                flug.flugstatus = "pünktlich"

            flughafen_von = Flughafen.query.filter(Flughafen.flughafenid == flug.abflugid).first()
            flughafen_nach = Flughafen.query.filter(Flughafen.flughafenid == flug.zielid).first()

            db.session.commit()

            # random email adresse, da sonst fehler meldung wenn keine Email adresse hinterlegt ist

            emailadressen = ["test@default.com"]

            alle_nutzer = Nutzerkonto.query.join(Buchung).filter(Nutzerkonto.id == Buchung.nutzerid). \
                filter(Buchung.flugid == request.form.get('id')).filter(Buchung.buchungsstatus != 'storniert')

            for rows in alle_nutzer:
                emailadressen.append(str(rows.emailadresse))

            msg = Message('Änderungen in Ihrer Buchung', sender='mailhog_grup3', recipients=emailadressen)
            msg.html = render_template('Verwaltungspersonal/Flugdaten_geändert_email.html',
                                       user=current_user, von=flughafen_von.stadt, nach=flughafen_nach.stadt,
                                       wann=flug.sollabflugzeit)
            mail.send(msg)

            log_event('Flugdaten (id = ' + str(
                flug.flugid) + ') wurden geändert. [von NutzerID = ' + str(current_user.id) + ']')

            flash("Flugdaten erfolgreich geändert", category='success')

        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))


# /F580/
# Diese Funktion erlaubt es dem Verwaltungspersonal, Accounts für Boden- oder Verwaltungspersonal anzulegen.
@verwaltungspersonal_views.route('/accounts-anlegen', methods=['GET', 'POST'])
@login_required
def accounts_anlegen():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    if request.method == 'POST':
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        emailadresse = request.form.get('emailadresse')
        special_characters = '!@#$%^&*/_+-'
        passwort = ''.join(random.choices(string.ascii_letters + string.digits + special_characters, k=8))
        while not (any(c.isdigit() for c in passwort) and any(c in special_characters for c in passwort)):
            passwort = ''.join(random.choices(string.ascii_letters + string.digits + special_characters, k=8))
        rolle = request.form.get('rolle')

        konto = Nutzerkonto.query.filter_by(emailadresse=emailadresse).first()
        if konto:
            flash('Mit dieser E-Mail-Adresse existiert bereits ein Account. Bitte löschen Sie diesen bevor Sie einen '
                  'neuen Account erstellen.',
                  category='error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', emailadresse):
            flash('Ungültige Email Adresse !', category='error')
        else:

            new_account = Nutzerkonto(vorname=vorname, nachname=nachname, emailadresse=emailadresse, rolle=rolle,
                                      passwort=generate_password_hash(passwort, method='sha256'))
            db.session.add(new_account)
            db.session.commit()
            msg = Message('Ihr Account wurde erstellt', sender='mailhog_grup3', recipients=[emailadresse])
            msg.html = render_template('Verwaltungspersonal/neuer_account_erstellt_email.html', password=passwort,
                                       user=current_user, rolle=rolle, vorname=vorname)
            mail.send(msg)

            flash(rolle + "account wurde erfolgreich erstellt")

            log_event(rolle + 'account (id = ' + str(
                new_account.id) + ') wurden erstellt [von NutzerID = ' + str(current_user.id) + '].')

            return render_template("Verwaltungspersonal/accounts_anlegen.html", user=current_user)

    return render_template("Verwaltungspersonal/accounts_anlegen.html", user=current_user)


# /F590/
# Diese Funktion erlaubt es dem Verwaltungspersonal, Accounts für Boden- oder Verwaltungspersonal zu bearbeiten.
@verwaltungspersonal_views.route('/accounts-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/accounts-bearbeiten/<int:page>', methods=['GET', 'POST'])
@login_required
def accounts_bearbeiten(page):
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    page = page
    pages = 4
    accounts = Nutzerkonto.query.filter(
        or_(Nutzerkonto.rolle == 'Bodenpersonal', Nutzerkonto.rolle == 'Verwaltungspersonal')).order_by(
        Nutzerkonto.id.desc()) \
        .paginate(page=page, per_page=pages, error_out=False)

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        accounts = Nutzerkonto.query.filter(
            and_(Nutzerkonto.nachname.like(search),
                 or_(Nutzerkonto.rolle == 'Bodenpersonal', Nutzerkonto.rolle == 'Verwaltungspersonal'))). \
            order_by(Nutzerkonto.id.desc()).paginate(
            page=page, per_page=pages, error_out=False)

        return render_template("Verwaltungspersonal/accounts_bearbeiten.html", accounts=accounts, user=current_user)

    return render_template("Verwaltungspersonal/accounts_bearbeiten.html", accounts=accounts, user=current_user)


# konkrete Funktion um Accountdaten über Modal zu ändern
@verwaltungspersonal_views.route('/accounts-ändern', methods=['GET', 'POST'])
@login_required
def accounts_ändern():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    if request.method == 'POST':
        nutzer = Nutzerkonto.query.get_or_404(request.form.get('id'))

        nutzer.vorname = request.form['vorname']
        nutzer.nachname = request.form['nachname']
        nutzer.email = request.form['emailadresse']
        nutzer.rolle = request.form['rolle']
        db.session.commit()

        log_event('Nutzerdaten (id = ' + str(
            nutzer.id) + ') wurden geändert. [von NutzerID = ' + str(current_user.id) + ']')

        flash("Nutzerdaten erfolgreich geändert")

        return redirect(url_for('verwaltungspersonal_views.accounts_bearbeiten'))


# Diese Hilfsfunktion erlaubt es dem Verwaltungspersonal, Accounts für Boden- oder Verwaltungspersonal zu löschen.
@verwaltungspersonal_views.route('/accounts-loeschen/<int:id>', methods=['GET', 'POST'])
@login_required
def accounts_loeschen(id):
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    if id == current_user.id:
        flash('Sie können nicht Ihren eigenen Account löschen!', category='error')
        return redirect(url_for('verwaltungspersonal_views.accounts_bearbeiten'))
    else:
        account = Nutzerkonto.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()
        log_event('Nutzer (id = ' + str(
            account.id) + ') wurde gelöscht. [von NutzerID = ' + str(current_user.id) + ']')

        return redirect(url_for('verwaltungspersonal_views.accounts_bearbeiten'))


@verwaltungspersonal_views.route('/reporting', methods=['GET', 'POST'])
@login_required
def reporting():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    flughafen_liste = Flughafen.query.all()

    vonID = Flughafen.query.filter(Flughafen.stadt == request.args.get('von')).with_entities(
        Flughafen.flughafenid)
    nachID = Flughafen.query.filter(Flughafen.stadt == request.args.get('nach')).with_entities(
        Flughafen.flughafenid)
    zeitvon = datetime.strptime(request.args.get('zeitvon', "2022-01-01"), '%Y-%m-%d')
    zeitbis = datetime.strptime(request.args.get('zeitbis', str(datetime.today().date())), '%Y-%m-%d')

    reporting_list = []
    if zeitvon > zeitbis:
        flash('"Zeit Von" darf nicht nach "Zeit Bis" liegen. Bitte kontrollieren Sie die Eingabe',
              category='error')
        return redirect(url_for('verwaltungspersonal_views.reporting'))
    elif zeitbis > datetime.now():
        flash('Die Datumseingaben dürfen nicht in der Zukunft liegen',
              category='error')
        return redirect(url_for('verwaltungspersonal_views.reporting'))

    if request.args.get('von') == "..." and request.args.get('nach') != "...":
        alle_fluege = Flug.query.filter(Flug.zielid == nachID).filter(
            Flug.sollabflugzeit). \
            filter(Flug.sollabflugzeit >= zeitvon).filter(cast(Flug.sollankunftszeit, Date) <= zeitbis)
    elif request.args.get('nach') == "..." and request.args.get('von') != "...":
        alle_fluege = Flug.query.filter(Flug.abflugid == vonID).filter(
            Flug.sollabflugzeit). \
            filter(Flug.sollabflugzeit >= zeitvon).filter(cast(Flug.sollankunftszeit, Date) <= zeitbis)
    elif request.args.get('nach') == "..." and request.args.get('von') == "...":
        alle_fluege = Flug.query.filter(Flug.sollabflugzeit). \
            filter(Flug.sollabflugzeit >= zeitvon).filter(cast(Flug.sollankunftszeit, Date) <= zeitbis)
    else:

        alle_fluege = Flug.query.filter(Flug.abflugid == vonID).filter(Flug.zielid == nachID).filter(
            Flug.sollabflugzeit). \
            filter(Flug.sollabflugzeit >= zeitvon).filter(cast(Flug.sollankunftszeit, Date) <= zeitbis)

    gesamtumsatz = 0
    gesamt_pünktlich = 0
    gesamt_verspätet = 0
    gesamt_annulliert = 0
    gesamt_passagiere = 0
    gesamt_sitzplaetze = 0

    for rows in alle_fluege:
        anzahl_passagiere = Passagier.query.join(Buchung, Flug). \
            filter(Flug.flugid == Buchung.flugid).filter(Passagier.buchungsid == Buchung.buchungsid). \
            filter(Flug.flugid == rows.flugid).filter(Buchung.buchungsstatus != "storniert").count()
        gesamt_passagiere += int(anzahl_passagiere)
        abflugid = rows.abflugid
        zielid = rows.zielid
        flugid = rows.flugid
        umsatz = rows.preis * anzahl_passagiere
        gesamtumsatz = gesamtumsatz + umsatz
        status = rows.flugstatus
        if status == "pünktlich":
            gesamt_pünktlich += 1
        elif status == "verspätet":
            gesamt_verspätet += 1
        else:
            gesamt_annulliert += 1

        sitzplaetze = Flugzeug.query.filter(Flugzeug.flugzeugid == rows.flugzeugid).first().anzahlsitzplaetze
        gesamt_sitzplaetze += int(sitzplaetze)
        auslastung = '{:.1%}'.format(anzahl_passagiere / sitzplaetze)

        reporting_list.append([flugid, abflugid, zielid, status, umsatz, auslastung])

    if not reporting_list and request.args.get('von') is not None:
        flash('In diesem Zeitraum oder zu diesen Flughäfen gibt es noch keine Daten', category='error')

    print(gesamt_annulliert, gesamt_verspätet, gesamt_pünktlich,
          gesamtumsatz)

    return render_template("Verwaltungspersonal/reporting.html", user=current_user, flughafen_liste=flughafen_liste,
                           default_flughafen_von=default_flughafen_von, default_flughafen_nach=default_flughafen_nach,
                           alle_fluege=alle_fluege, reporting_list=reporting_list, today=datetime.today().date(),
                           gesamt_annulliert=gesamt_annulliert, gesamt_verspaetet=gesamt_verspätet,
                           gesamt_puenktlich=gesamt_pünktlich,
                           gesamtumsatz=gesamtumsatz, gesamt_sitzplaetze=gesamt_sitzplaetze,
                           gesamt_passagiere=gesamt_passagiere)


@verwaltungspersonal_views.route("/diagramm_anzeigen/", methods=["GET", "POST"])
@login_required
def diagramm_anzeigen():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    gesamtumsatz = int(request.args.get('gesamtumsatz'))
    gesamt_pünktlich = int(request.args.get('gesamt_puenktlich'))
    gesamt_verspätet = int(request.args.get('gesamt_verspaetet'))
    gesamt_annulliert = int(request.args.get('gesamt_annulliert'))
    gesamt_sitzplaetze = int(request.args.get('gesamt_sitzplaetze'))
    gesamt_passagiere = int(request.args.get('gesamt_passagiere'))

    gesamt_auslastung = '{:.1%}'.format(gesamt_passagiere / gesamt_sitzplaetze)

    sum = gesamt_verspätet + gesamt_pünktlich + gesamt_annulliert

    labels = ['annulliert', 'verspätet', 'pünktlich']
    sizes = [gesamt_annulliert / sum, gesamt_verspätet / sum, gesamt_pünktlich / sum]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False)
    ax.axis('equal')

    pngImage = io.BytesIO()
    fig.savefig(pngImage, format='png')
    pngImageB64 = base64.b64encode(pngImage.getvalue()).decode('utf-8')

    return render_template("Verwaltungspersonal/reporting_diagramm.html", image=pngImageB64, user=current_user,
                           gesamtumsatz=gesamtumsatz, gesamt_auslastung=gesamt_auslastung,
                           gesamt_passagiere=gesamt_passagiere)


@verwaltungspersonal_views.route("/logging/", methods=["GET", "POST"])
@login_required
def logging():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    with open("flask.log", "r") as logfile:
        logs = logfile.readlines()
    return render_template("Verwaltungspersonal/logging.html", logs=logs, user=current_user)


@verwaltungspersonal_views.route("/logging-löschen/", methods=["GET", "POST"])
@login_required
def log_löschen():
    if not role_required("Verwaltungspersonal"):
        flash('ERROR: Kein Zugriff auf diese URL', category='error')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))
    with open("flask.log", "w") as logfile:
        logs = logfile.write("")
    return redirect(url_for('verwaltungspersonal_views.logging'))
