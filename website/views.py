from flask import Blueprint, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto
from . import db

# store the standard routes for a website where the user can navigate to
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)

    vonID = Flughafen.query.filter(Flughafen.stadt == request.args.get('von')).with_entities(Flughafen.flughafenid)
    nachID = Flughafen.query.filter(Flughafen.stadt == request.args.get('nach')).with_entities(Flughafen.flughafenid)
    abflug = request.args.get('Abflugdatum')
    passagiere = request.args.get('AnzahlPersonen')

    print(vonID, nachID)

    # Datenbankabfrage nach Abflug und Ziel Flughafen sowie Datum und Passagieranzahl < Summe bereits gebuchter Passagiere

    fluege = Flug.query.filter(Flug.abflugid == vonID, Flug.zielid == nachID)

    return render_template("Gast/home.html", fluege=fluege, flughafen_liste=flughafen_liste, user=current_user)


@views.route('/home-vp', methods=['GET', 'POST'])
def flugzeug_erstellen():
    flugzeuge = Flugzeug.query.with_entities(Flugzeug.hersteller, Flugzeug.modell, Flugzeug.flugzeugid,
                                             Flugzeug.anzahlsitzplaetze).order_by(Flugzeug.flugzeugid.desc()).limit(
        5).all()

    if request.method == 'POST':
        modell = request.form.get('Modell')
        hersteller = request.form.get('Hersteller')
        anzahlsitzplaetze = request.form.get('anzahlsitzplaetze')

        new_flugzeug = Flugzeug(modell=modell, hersteller=hersteller, anzahlsitzplaetze=anzahlsitzplaetze)
        db.session.add(new_flugzeug)
        db.session.commit()
        flash('Flugzeug added!', category='success')

    return render_template("Verwaltungspersonal/home_vp.html", flugzeuge=flugzeuge)


@views.route('/flugzeug-bearbeiten', methods=['GET', 'POST'])
def flugzeug_bearbeiten():
    flugzeuge = Flugzeug.query.with_entities(Flugzeug.hersteller, Flugzeug.modell, Flugzeug.flugzeugid,
                                             Flugzeug.anzahlsitzplaetze).order_by(Flugzeug.flugzeugid.desc()) \
                                            .limit(5).all()

    return render_template("Verwaltungspersonal/flugzeug_bearbeiten.html", flugzeuge=flugzeuge)


@views.route('/flug-anlegen', methods=['GET', 'POST'])
def flug_anlegen():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)

    if request.method == 'POST':
        abflugid = Flughafen.query.filter(Flughafen.stadt == request.form.get('von')) \
            .with_entities(Flughafen.flughafenid)
        zielid = Flughafen.query.filter(Flughafen.stadt == request.form.get('nach')) \
            .with_entities(Flughafen.flughafenid)
        flugstatus = "pünktlich"
        abflugdatum = request.form.get('abflugdatum') + " " + request.form.get("abflugzeit")
        ankunftsdatum = request.form.get('ankunftsdatum') + " " + request.form.get("ankunftszeit")
        flugnummer = request.form.get('fluglinie')
        preis = request.form.get('preis')
        gate = "A2"

        new_flug = Flug(flugzeugid=1, abflugid=abflugid, zielid=zielid, flugstatus=flugstatus,
                        sollabflugzeit=abflugdatum, sollankunftszeit=ankunftsdatum,
                        istabflugzeit=abflugdatum, istankunftszeit=ankunftsdatum,
                        flugnummer=flugnummer,
                        preis=preis, gate=gate)
        db.session.add(new_flug)
        db.session.commit()
        flash('Flugzeug added!', category='success')

        print(abflugid, zielid, flugstatus, abflugdatum, ankunftsdatum, flugnummer, preis, gate)

    return render_template("Verwaltungspersonal/flug_anlegen.html", flughafen_liste=flughafen_liste)


@views.route('/accounts-anlegen', methods=['GET', 'POST'])
def accounts_anlegen():
    if request.method == 'POST':
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        emailadresse = request.form.get('emailadresse')
        passwort = "aadsöf"
        rolle = request.form.get('rolle')

        new_account = Nutzerkonto(vorname=vorname, nachname=nachname, emailadresse=emailadresse, rolle=rolle,
                                  passwort=passwort)
        db.session.add(new_account)
        db.session.commit()

        flash(rolle + "account wurde erfolgreich erstellt")

    return render_template("Verwaltungspersonal/accounts_anlegen.html")


@views.route('/accounts-bearbeiten', methods=['GET', 'POST'])
def accounts_bearbeiten():
    accounts = Nutzerkonto.query.all()
    return render_template("Verwaltungspersonal/accounts_bearbeiten.html", accounts=accounts)


@views.route('/accounts-loeschen/<int:id>', methods=['GET', 'POST'])
def accounts_loeschen(id):
    account = Nutzerkonto.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    accounts = Nutzerkonto.query.all()
    return render_template("Verwaltungspersonal/accounts_bearbeiten.html", accounts=accounts)
