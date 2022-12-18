from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from select import select
from sqlalchemy import and_, select


from .models import Flug, Flughafen, Flugzeug, Buchung
from . import db

# store the standard routes for a website where the user can navigate to
verwaltungspersonal_views = Blueprint('verwaltungspersonal_views', __name__)



@verwaltungspersonal_views.route('/suchen')
def flug_suchen():
    flughafen = Flughafen.query.all()

    return render_template("flugsuchen.html", flughafen=flughafen)


@verwaltungspersonal_views.route('/home-vp', methods=['GET', 'POST'])
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


@verwaltungspersonal_views.route('/flug-anlegen', methods=['GET', 'POST'])
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
