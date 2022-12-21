from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
import secrets
from . import db, conn
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto
from sqlalchemy import select, or_, cast, Date

# store the standard routes for a website where the user can navigate to
views = Blueprint('views', __name__)


# Gast Funktionen
@views.route('/', methods=['GET', 'POST'])
def home():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)

    vonID = Flughafen.query.filter(Flughafen.stadt == request.args.get('von')).with_entities(Flughafen.flughafenid)
    nachID = Flughafen.query.filter(Flughafen.stadt == request.args.get('nach')).with_entities(Flughafen.flughafenid)
    abflug = request.args.get('Abflugdatum')
    passagiere = request.args.get('AnzahlPersonen')

    kuerzel_von = Flughafen.query.filter(Flughafen.flughafenid == vonID).first()
    kuerzel_nach = Flughafen.query.filter(Flughafen.flughafenid == nachID).first()

    # Datenbankabfrage nach Abflug und Ziel Flughafen sowie Datum und Passagieranzahl < Summe bereits gebuchter Passagiere

    fluege = Flug.query.filter(Flug.abflugid == vonID, Flug.zielid == nachID). \
        filter(cast(Flug.sollabflugzeit, Date) == abflug)

    return render_template("Gast/home.html", fluege=fluege, flughafen_liste=flughafen_liste, user=current_user,
                           kuerzel_nach=kuerzel_nach, kuerzel_von=kuerzel_von, passagiere=passagiere)


@views.route('/flugstatus-überprüfen', methods=['GET', 'POST'])
def flugstatus_überprüfen():
    abflug = request.args.get('abflugdatum')
    flugnummer = request.args.get('flugnummer')

    fluege = Flug.query.filter(cast(Flug.sollabflugzeit, Date) == abflug).filter(Flug.flugnummer == flugnummer)

    return render_template("Gast/flugstatus_überprüfen.html", user=current_user, fluege=fluege)


@views.route('fluglinien-anzeigen', methods=['GET', 'POST'], defaults={"page": 1})
@views.route('fluglinien-anzeigen/<int:page>', methods=['GET', 'POST'])
def fluglinien_anzeigen(page):
    page = page
    pages = 4
    fluege = Flug.query.distinct().paginate(page=page, per_page=pages, error_out=False)
    return render_template("Gast/fluglinien_anzeigen.html", user=current_user, fluege=fluege)


@views.route('/flug-buchen/<int:id>/<int:anzahlPassagiere>', methods=['GET', 'POST'])
@login_required
def flug_buchen(id, anzahlPassagiere):
    return render_template("Passagier/flug_buchen.html", user=current_user, flugid=id,
                           anzahlPassagiere=anzahlPassagiere)


@views.route('/home-vp', methods=['GET', 'POST'])
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


@views.route('/flugzeug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@views.route('/flugzeug-bearbeiten/<int:page>', methods=['GET', 'POST'])
def flugzeug_bearbeiten(page):
    page = page
    pages = 4

    # nur 4 flugzeuge werden angezeigt über paginate

    flugzeuge = Flugzeug.query.filter(Flugzeug.status == "aktiv").paginate(page=page, per_page=pages, error_out=False)

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        flugzeuge = Flugzeug.query.filter(Flugzeug.hersteller.like(search)). \
            filter(Flugzeug.status == "aktiv").paginate(page=page, per_page=pages, error_out=False)

        return render_template("Verwaltungspersonal/flugzeug_bearbeiten.html", flugzeuge=flugzeuge,
                               user=current_user, tag=tag)

    return render_template("Verwaltungspersonal/flugzeug_bearbeiten.html", flugzeuge=flugzeuge, user=current_user)


@views.route('/flugzeug-ändern', methods=['GET', 'POST'])
def flugzeug_ändern():
    if request.method == 'POST':
        flugzeug = Flugzeug.query.get_or_404(request.form.get('id'))

        flugzeug.modell = request.form['modell']
        flugzeug.hersteller = request.form['hersteller']
        flugzeug.anzahlsitzplaetze = request.form['anzahlsitzplaetze']
        db.session.commit()
        flash("Flugzeugdaten erfolgreich geändert")
        return redirect(url_for('views.flugzeug_bearbeiten'))


@views.route('/flugzeug-inaktiv-setzen/<int:id>', methods=['GET', 'POST'])
def flugzeug_inaktiv_setzen(id):
    flugzeug_inaktiv = Flugzeug.query.filter_by(flugzeugid=id).first()
    flugzeug_inaktiv.status = "inaktiv"
    db.session.merge(flugzeug_inaktiv)
    db.session.commit()

    return redirect(url_for('views.flugzeug_bearbeiten'))


@views.route('/flug-anlegen', methods=['GET', 'POST'])
def flug_anlegen():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)
    flugzeug_liste = Flugzeug.query.with_entities(Flugzeug.flugzeugid, Flugzeug.hersteller, Flugzeug.modell)

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


@views.route('/flug-bearbeiten', methods=['GET', 'POST'], defaults={"page": 1})
@views.route('/flug-bearbeiten/<int:page>', methods=['GET', 'POST'])
def flug_bearbeiten(page):
    page = page
    pages = 4
    fluege = Flug.query.paginate(page=page, per_page=pages, error_out=False)

    # suche nach Flugnummer

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        fluege = Flug.query.filter(Flug.flugnummer.like(search)).paginate(page=page, per_page=pages, error_out=False)

        return render_template("Verwaltungspersonal/flug_bearbeiten.html", fluege=fluege,
                               user=current_user, tag=tag)

    return render_template("Verwaltungspersonal/flug_bearbeiten.html", fluege=fluege, user=current_user)


# Funktionen zu Accounte: anzeigen bearbeiten und löschen

@views.route('/accounts-anlegen', methods=['GET', 'POST'])
def accounts_anlegen():
    if request.method == 'POST':
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        emailadresse = request.form.get('emailadresse')
        passwort = "12345"
        rolle = request.form.get('rolle')

        new_account = Nutzerkonto(vorname=vorname, nachname=nachname, emailadresse=emailadresse, rolle=rolle,
                                  passwort=generate_password_hash(passwort, method='sha256'))
        db.session.add(new_account)
        db.session.commit()

        flash(rolle + "account wurde erfolgreich erstellt")

    return render_template("Verwaltungspersonal/accounts_anlegen.html", user=current_user)


# Seite mit die das Bearbeiten und löschen ermöglicht
@views.route('/accounts-bearbeiten', methods=['GET', 'POST'])
def accounts_bearbeiten():
    accounts = Nutzerkonto.query.filter(
        or_(Nutzerkonto.rolle == 'Bodenpersonal', Nutzerkonto.rolle == 'Verwaltungspersonal'))

    return render_template("Verwaltungspersonal/accounts_bearbeiten.html", accounts=accounts, user=current_user)


# konkrete Funktion um Accountdaten über Modal zu ändern
@views.route('/accounts-ändern', methods=['GET', 'POST'])
def accounts_ändern():
    if request.method == 'POST':
        nutzer = Nutzerkonto.query.get_or_404(request.form.get('id'))

        nutzer.vorname = request.form['vorname']
        nutzer.nachname = request.form['nachname']
        nutzer.email = request.form['emailadresse']
        nutzer.rolle = request.form['rolle']
        db.session.commit()
        flash("Nutzerdaten erfolgreich geändert")

        return redirect(url_for('views.accounts_bearbeiten'))


@views.route('/accounts-loeschen/<int:id>', methods=['GET', 'POST'])
def accounts_loeschen(id):
    account = Nutzerkonto.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()

    return redirect(url_for('views.accounts_bearbeiten'))
