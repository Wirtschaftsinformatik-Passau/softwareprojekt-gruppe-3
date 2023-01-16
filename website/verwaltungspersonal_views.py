import random
import string

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db, mail
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date, and_
from datetime import date, timedelta
from flask_mail import Mail, Message

# store the standard routes for a website where the user can navigate to
verwaltungspersonal_views = Blueprint('verwaltungspersonal_views', __name__)


# Flugzeug funktionen
@verwaltungspersonal_views.route('/home-vp', methods=['GET', 'POST'])
def flugzeug_erstellen():
    if request.method == 'POST':
        modell = request.form.get('Modell')
        hersteller = request.form.get('Hersteller')
        anzahlsitzplaetze = request.form.get('anzahlsitzplaetze')


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
        anzahl_passagiere = Passagier.query.join(Buchung, Flug). \
            filter(Flug.flugid == Buchung.flugid).filter(Passagier.buchungsid == Buchung.buchungsid). \
            filter(Flug.flugzeugid == request.form.get('id')). \
            filter(Flug.flugstatus != "annulliert").count()

        flugzeug.modell = request.form['modell']
        flugzeug.hersteller = request.form['hersteller']


        flugzeug.anzahlsitzplaetze = request.form['anzahlsitzplaetze']
        db.session.commit()
        flash("Flugzeugdaten erfolgreich geändert")
        return redirect(url_for('verwaltungspersonal_views.flugzeug_bearbeiten'))


@verwaltungspersonal_views.route('/flugzeug-inaktiv-setzen/<int:id>', methods=['GET', 'POST'])
def flugzeug_inaktiv_setzen(id):
    flugzeug_inaktiv = Flugzeug.query.filter_by(flugzeugid=id).first()
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
        abflugid = Flughafen.query.filter(Flughafen.stadt == request.form.get('von')) \
            .with_entities(Flughafen.flughafenid)
        zielid = Flughafen.query.filter(Flughafen.stadt == request.form.get('nach')) \
            .with_entities(Flughafen.flughafenid)
        flugstatus = "pünktlich"
        abflugdatum = request.form.get('abflugdatum') + " " + request.form.get("abflugzeit")
        ankunftsdatum = request.form.get('ankunftsdatum') + " " + request.form.get("ankunftszeit")
        flugnummer = request.form.get('fluglinie')
        preis = request.form.get('preis')

        new_flug = Flug(flugzeugid=flugzeugid, abflugid=abflugid, zielid=zielid, flugstatus=flugstatus,
                        sollabflugzeit=abflugdatum, sollankunftszeit=ankunftsdatum,
                        istabflugzeit=abflugdatum, istankunftszeit=ankunftsdatum,
                        flugnummer=flugnummer,
                        preis=preis)

        db.session.add(new_flug)
        db.session.commit()
        flash('Flug hinzugefügt!', category='success')

    return render_template("Verwaltungspersonal/flug_anlegen.html", flughafen_liste=flughafen_liste, user=current_user,
                           flugzeug_liste=flugzeug_liste)


@verwaltungspersonal_views.route('/flug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@verwaltungspersonal_views.route('/flug-bearbeiten/<int:page>', methods=['GET', 'POST'])
def flug_bearbeiten(page):
    flughafen_liste = Flughafen.query.all()
    flugzeug_liste = Flugzeug.query.all()
    page = page
    pages = 4

    # alle flüge von gestern bis in die Zukunft

    fluege = Flug.query.filter(Flug.istabflugzeit > date.today() - timedelta(days=1)).order_by(Flug.flugid.desc()) \
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
    flug.flugstatus = 'annulliert'
    db.session.commit()
    flash('Flug wurde erfolgreich annulliert', category='success')
    return redirect(url_for('verwaltungspersonal_views.flug_bearbeiten'))


@verwaltungspersonal_views.route('/flug-ändern/', methods=['GET', 'POST'])
def flug_ändern():
    if request.method == 'POST':
        flug = Flug.query.get_or_404(request.form.get('id'))

        flug.abflugid = request.form['von']
        flug.zielid = request.form['nach']
        flug.flugzeugid = request.form['flugzeugtyp']
        flug.preis = request.form['preis']
        flug.sollabflugzeit = request.form['abflugdatum'] + " " + request.form['sollabflugzeit']
        flug.sollankunftszeit = request.form['ankunftsdatum'] + " " + request.form['sollankunftszeit']
        flug.istabflugzeit = request.form['abflugdatum'] + " " + request.form['istabflugzeit']
        flug.istankunftszeit = request.form['ankunftsdatum'] + " " + request.form['istankunftszeit']
        flug.flugnummer = request.form['fluglinie']

        if flug.istankunftszeit > flug.sollankunftszeit:
            flug.flugstatus = "verspätet"

        elif flug.istankunftszeit == flug.sollankunftszeit:
            flug.flugstatus = "pünktlich"

        db.session.commit()
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


# Seite mit die das Bearbeiten und löschen ermöglicht
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
