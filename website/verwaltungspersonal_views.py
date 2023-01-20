import random
import string
from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db, mail
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date, and_
from datetime import date, timedelta
from flask_mail import Mail, Message
import re

# import __init__

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
    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
    end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
    if start_time <= end_time:
        return start_time <= datetime.now() <= end_time
    else:  # over midnight e.g., 23:30-04:15
        return datetime.now() >= start_time or datetime.now() <= end_time


# Flugzeug funktionen
@verwaltungspersonal_views.route('/home-vp', methods=['GET', 'POST'])
@verwaltungspersonal_views.route('/home-vp', methods=['GET', 'POST'])
def flugzeug_erstellen():
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
            flash('Flugzeug angelegt!', category='success')

    return render_template("Verwaltungspersonal/home_vp.html", user=current_user)


@verwaltungspersonal_views.route('/flugzeug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/flugzeug-bearbeiten/<int:page>', methods=['GET', 'POST'])
def flugzeug_bearbeiten(page):
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


@verwaltungspersonal_views.route('/flugzeug-ändern', methods=['GET', 'POST'])
def flugzeug_ändern():
    if request.method == 'POST':
        flugzeug = Flugzeug.query.get_or_404(request.form.get('id'))
        fluege_mit_flugzeug = Flug.query.join(Flugzeug).filter(Flug.flugzeugid == Flugzeug.flugzeugid). \
            filter(Flug.flugzeugid == request.form.get('id')). \
            filter(Flug.flugstatus != "annuliert")
        max_anzahl_passagier = 0
        for rows in fluege_mit_flugzeug:

            anzahl = Passagier.query.join(Buchung, Flug). \
                filter(Flug.flugid == Buchung.flugid).filter(Passagier.buchungsid == Buchung.buchungsid). \
                filter(Flug.flugid == rows.flugid).filter(Flug.sollabflugzeit > date.today()).count()
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
            flash("Flugzeugdaten erfolgreich geändert")
        return redirect(url_for('verwaltungspersonal_views.flugzeug_bearbeiten'))


@verwaltungspersonal_views.route('/flugzeug-inaktiv-setzen/<int:id>', methods=['GET', 'POST'])
def flugzeug_inaktiv_setzen(id):
    flugzeug_inaktiv = Flugzeug.query.filter_by(flugzeugid=id).first()
    anzahl_passagiere = Passagier.query.join(Buchung, Flug). \
        filter(Flug.flugid == Buchung.flugid).filter(Passagier.buchungsid == Buchung.buchungsid). \
        filter(Flug.flugzeugid == id). \
        filter(Flug.flugstatus != "annuliert").filter(Flug.sollabflugzeit > date.today()).count()

    if anzahl_passagiere > 0:
        flash('Das Flugzeug welches Sie löschen wollen ist mit einem aktiven Flug verbunden. Bitte wenden Sie sich '
              'an einen Vorgesetzten.', category="error")
    else:
        flugzeug_inaktiv.status = "inaktiv"
        db.session.merge(flugzeug_inaktiv)
        db.session.commit()

    return redirect(url_for('verwaltungspersonal_views.flugzeug_bearbeiten'))


# Flug funktionen
@verwaltungspersonal_views.route('/flug-anlegen', methods=['GET', 'POST'])
def flug_anlegen():
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

        # chec, ob ein Flug mit gleichen von und nach und abflugzeit existiert

        fluege = Flug.query.filter(Flug.abflugid == abflugid.flughafenid).filter(Flug.zielid == zielid.flughafenid). \
            filter(Flug.sollabflugzeit == abflugdatum).filter(Flug.sollankunftszeit == ankunftsdatum). \
            filter(Flug.flugzeugid == flugzeugid)

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
            flash('Flug hinzugefügt!', category='success')

    return render_template("Verwaltungspersonal/flug_anlegen.html", flughafen_liste=flughafen_liste, user=current_user,
                           flugzeug_liste=flugzeug_liste, default_flughafen_von=default_flughafen_von,
                           default_flughafen_nach=default_flughafen_nach, tomorrow=date.today() + timedelta(days=1))


@verwaltungspersonal_views.route('/flug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/flug-bearbeiten/<int:page>', methods=['GET', 'POST'])
def flug_bearbeiten(page):
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


@verwaltungspersonal_views.route('/flug-annulieren/<int:id>', methods=['GET', 'POST'])
def flug_annulieren(id):
    flug = Flug.query.get_or_404(id)
    if flug.flugstatus == "annulliert":
        flash('Flug wurde bereits annulliert!', category='error')
        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))
    elif is_between(flug.istabflugzeit, flug.istankunftszeit):
        flash('Flug ist bereits gestartet. Sie können diesen Flug nicht mehr annullieren', category='error')
    else:
        flug.flugstatus = 'annulliert'
        db.session.commit()
        flughafen_von = Flughafen.query.filter(Flughafen.flughafenid == flug.abflugid).first()
        flughafen_nach = Flughafen.query.filter(Flughafen.flughafenid == flug.zielid).first()
        wann = flug.sollabflugzeit.strftime("%d.%m.%Y")

        emailadressen = ["test@default.com"]

        alle_nutzer = Nutzerkonto.query.join(Buchung).filter(Nutzerkonto.id == Buchung.nutzerid). \
            filter(Buchung.flugid == id)

        for rows in alle_nutzer:
            emailadressen.append(str(rows.emailadresse))

        print(emailadressen)

        msg = Message('Annullierung Ihres Fluges', sender='airpassau.de@gmail.com', recipients=emailadressen)
        msg.html = render_template('Verwaltungspersonal/Flug_annulliert_email.html',
                                   user=current_user, von=flughafen_von.stadt, nach=flughafen_nach.stadt, wann=wann)
        mail.send(msg)
        flash('Flug wurde erfolgreich annulliert', category='success')
        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))


@verwaltungspersonal_views.route('/flug-ändern/', methods=['GET', 'POST'])
def flug_ändern():
    if request.method == 'POST':
        flug = Flug.query.get_or_404(request.form.get('id'))

        old_price = flug.preis
        old_abflug = flug.sollabflugzeit
        old_ankunft = flug.sollankunftszeit

        flug.abflugid = request.form['von']
        flug.zielid = request.form['nach']
        flug.flugzeugid = request.form['flugzeugtyp']
        flug.preis = request.form['preis']
        flug.sollabflugzeit = request.form['abflugdatum'] + " " + request.form['sollabflugzeit']
        flug.sollankunftszeit = request.form['ankunftsdatum'] + " " + request.form['sollankunftszeit']
        flug.istabflugzeit = request.form['abflugdatum'] + " " + request.form['istabflugzeit']
        flug.istankunftszeit = request.form['ankunftsdatum'] + " " + request.form['istankunftszeit']
        flug.flugnummer = request.form['fluglinie']

        # check ob ein Flug mit gleichen von und nach und abflugzeit existiert
        if is_date_after_yesterday(flug.istankunftszeit, 0) or flug.flugstatus == "annulliert":
            flash('Der Flug ist bereits gelandet oder annulliert worden. Sie können keine Änderungen mehr vornehmen',
                  category='error')
        elif flug.sollabflugzeit > flug.sollankunftszeit or flug.istabflugzeit > flug.istankunftszeit:
            flash('Der Ankunftszeit darf nicht vor der Abflugzeit sein. Bitte kontrollieren Sie die Eingabe',
                  category='error')
        elif flug.abflugid == flug.zielid:
            flash('Von und Nach dürfen nicht der gleichen Stadt entsprechen', category='error')
        elif is_between(flug.istabflugzeit, flug.istankunftszeit) and int(old_price) != int(request.form['preis']):
            flash('Der Flug ist bereits gestartet. Sie können den Preis nicht mehr ändern', category='error')
        elif is_between(flug.istabflugzeit, flug.istankunftszeit) and old_abflug != (
                request.form['abflugdatum'] + " " + request.form['sollabflugzeit']):
            flash('Der Flug ist bereits gestartet. Sie können die Sollzeiten nicht mehr ändern', category='error')
        elif is_between(flug.istabflugzeit, flug.istankunftszeit) and old_ankunft != (
                request.form['ankunftsdatum'] + " " + request.form['sollankunftszeit']):
            flash('Der Flug ist bereits gestartet. Sie können die Sollzeiten nicht mehr ändern', category='error')
        else:

            if flug.istankunftszeit > flug.sollankunftszeit:
                flug.flugstatus = "verspätet"

            elif flug.istankunftszeit == flug.sollankunftszeit:
                flug.flugstatus = "pünktlich"

            flughafen_von = Flughafen.query.filter(Flughafen.flughafenid == flug.abflugid).first()
            flughafen_nach = Flughafen.query.filter(Flughafen.flughafenid == flug.zielid).first()
            wann = request.form['abflugdatum']

            db.session.commit()

            # random email adresse, da sonst fehler meldung wenn keine Email adresse hinterlegt ist

            emailadressen = ["test@default.com"]

            alle_nutzer = Nutzerkonto.query.join(Buchung).filter(Nutzerkonto.id == Buchung.nutzerid). \
                filter(Buchung.flugid == request.form.get('id'))

            for rows in alle_nutzer:
                emailadressen.append(str(rows.emailadresse))

            print(emailadressen)

            msg = Message('Änderungen in Ihrer Buchung', sender='airpassau.de@gmail.com', recipients=emailadressen)
            msg.html = render_template('Verwaltungspersonal/Flugdaten_geändert_email.html',
                                       user=current_user, von=flughafen_von.stadt, nach=flughafen_nach.stadt, wann=wann)
            mail.send(msg)

            flash("Flugdaten erfolgreich geändert", category='success')

        return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))


# Funktionen zu Accounte: anzeigen bearbeiten und löschen
@verwaltungspersonal_views.route('/accounts-anlegen', methods=['GET', 'POST'])
def accounts_anlegen():
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
            msg = Message('Ihr Account wurde erstellt', sender='airpassau.de@gmail.com', recipients=[emailadresse])
            msg.html = render_template('Verwaltungspersonal/neuer_account_erstellt_email.html', password=passwort,
                                       user=current_user, rolle=rolle, vorname=vorname)
            mail.send(msg)

            flash(rolle + "account wurde erfolgreich erstellt")
            return render_template("Verwaltungspersonal/accounts_anlegen.html", user=current_user)

    return render_template("Verwaltungspersonal/accounts_anlegen.html", user=current_user)


# Seite die das Bearbeiten und löschen ermöglicht
@verwaltungspersonal_views.route('/accounts-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/accounts-bearbeiten/<int:page>', methods=['GET', 'POST'])
def accounts_bearbeiten(page):
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
def accounts_ändern():
    if request.method == 'POST':
        nutzer = Nutzerkonto.query.get_or_404(request.form.get('id'))

        nutzer.vorname = request.form['vorname']
        nutzer.nachname = request.form['nachname']
        nutzer.email = request.form['emailadresse']
        nutzer.rolle = request.form['rolle']
        db.session.commit()
        flash("Nutzerdaten erfolgreich geändert")

        return redirect(url_for('verwaltungspersonal_views.accounts_bearbeiten'))


@verwaltungspersonal_views.route('/accounts-loeschen/<int:id>', methods=['GET', 'POST'])
def accounts_loeschen(id):
    account = Nutzerkonto.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()

    return redirect(url_for('verwaltungspersonal_views.accounts_bearbeiten'))


@verwaltungspersonal_views.route('/logging/')
def logging():
    return redirect(url_for('logging'))


@verwaltungspersonal_views.route('/reporting', methods=['GET', 'POST'])
def reporting():
    return render_template("Verwaltungspersonal/reporting.html", user=current_user)
