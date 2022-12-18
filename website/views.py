from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from select import select
from sqlalchemy import and_, select


from .models import Flug, Flughafen, Flugzeug, Buchung
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

    #Datenbankabrag nach Abflug und Ziel Flughafen sowie Datum und Passagieranzahl < Summe bereits gebuchter Passagiere

    fluege = Flug.query.filter(Flug.abflugid == vonID, Flug.zielid == nachID)

    return render_template("Gast/home.html", fluege=fluege, flughafen_liste=flughafen_liste)


@views.route('/suchen')
def flug_suchen():
    flughafen = Flughafen.query.all()

    return render_template("flugsuchen.html", flughafen=flughafen)


@views.route('/home-vp', methods=['GET', 'POST'])
def flugzeug_erstellen():
    if request.method == 'POST':
        modell = request.form.get('Modell')
        hersteller = request.form.get('Hersteller')
        anzahlsitzplaetze = request.form.get('anzahlsitzplaetze')

        new_flugzeug = Flugzeug(modell=modell, hersteller=hersteller, anzahlsitzplaetze=anzahlsitzplaetze)
        db.session.add(new_flugzeug)
        db.session.commit()
        flash('Flugzeug added!', category='success')

    return render_template("Verwaltungspersonal/home_vp.html")


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

@views.route('/buchung_suchen', methods=['GET'])
def buchungsuebersicht_erhalten():
    if request.method == "GET":
        buchung = Buchung.query.all()  # nummer und status werden gezeigt
        #von = select(Flughafen.stadt).filter(Flug.abflugid == Flughafen.flughafenid and Flug.flugid == Buchung.flugid)
        #nach = select(Flughafen.stadt).filter(Flug.zielid == Flughafen.flughafenid and Flug.flugid == Buchung.flugid)
        #datum = select(Flug.sollabflugzeit).filter(Flug.flugid == Buchung.flugid)
        von = select([Flughafen.stadt]).where(
            and_(Flug.abflugid == Flughafen.flughafenid, Flug.flugid == Buchung.flugid))


    return render_template("Passagier/buchung_suchen.html", buchung=buchung, von=von)


@views.route('/flugstatus_erhalten', methods=['POST', 'GET'])
def flugstatus_erhalten():
    # Status von der Flugnummer holen, die eingetippt worden ist

    flug_nummer = request.form.get('flug_nummer')
    #gibt SQL Statement zurück
    #flugstatus = select(Flug.flugstatus).filter(flug_nummer == Flug.flugid)
    #gibt leere Brackets zurück
    flugstatus = Flug.query.filter(flug_nummer).all()

    return render_template("Passagier/flugstatus_erhalten.html", flugstatus=flugstatus)

@views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    return render_template("Passagier/online_check_in.html")
